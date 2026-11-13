"""
O vigia que garante que o que a IA escreve segue as regras do projeto, sem depender da palavra dela.

Um só programa para os momentos ligados a ele. O formulário chega pelo canal por onde o programa que chama manda texto
(a entrada padrão), escrito em JSON, a forma de texto que guarda dados em campos com nome; os nomes dos campos e dos
momentos estão na folha do protocolo (--protocolo), o arquivo que traduz o programa que chama para a peça. O vigia só
deixa a resposta terminar quando cada arquivo escrito na tarefa foi lido do começo ao fim depois da última escrita,
passou nas conferências que o projeto liga a ele e, se é dos que só uma pessoa confere, tem o ok dela para o conteúdo
de agora.

- Antes de uma escrita: barra a escrita na pasta das anotações e, enquanto um arquivo espera o ok de uma pessoa, a
  escrita em outro; na primeira escrita num arquivo, ou na volta a ele depois de escrever em outro, entrega os textos
  de regras ligados a ele; e anota o arquivo como escrito, sem leitura e sem ok.
- Antes de um comando no terminal: barra o que escreve num arquivo, o que roda código escrito no comando e o que não
  se lê.
- Depois de uma leitura, de um uso só ou de um lote: anota as linhas lidas de cada arquivo escrito.
- Na mensagem da pessoa: quando ela é o texto do ok seguido do caminho de um arquivo escrito, anota o ok para o
  conteúdo de agora do arquivo.
- No fim da resposta: confere cada arquivo escrito que ainda existe, em ordem alfabética; trava o fim quando falta
  leitura ou uma conferência não passa; avisa quando só falta o ok; e, quando tudo passa, apaga as anotações da
  sessão, e a tarefa seguinte começa do zero.

A configuração (--config) se lê pelo molde em esquemas/regras-de-codigo.schema.json, o arquivo que diz a forma que ela
tem de ter; os caminhos dela partem da pasta dela, e as conferências rodam dali. As listas do terminal vêm da
configuração do terminal (--terminal), e os textos que abrem os avisos, dos arquivos --fim e --bloqueio; depois do
texto, um aviso leva só dados. Um erro barra, com a mensagem dele, no momento que deixa barrar; nos outros, a mensagem
vai para o canal de erros do terminal. As peças da central chegam pelo roda.py, o programa da central que as acha e
roda esta peça com elas.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import protocolo_temporario as protocolo
from conferencia_de_molde import le_conferido
from erro_de_dados import ErroDeDados
from leitura_de_json import le_json
from leitura_de_texto import CODIFICACAO, le_texto
from leitura_do_terminal_temporaria import (DUPLICACAO, ESCRITA, FECHA_DESCRITOR, OPCAO, TEXTO_EMBUTIDO,
                                            ComandoIlegivel, configuracao_do_terminal, eh_redirecionamento, lidos,
                                            opcao_bate, posicoes_de_comando)
from resultado_de_comando import PASSOU, resultado

MOLDE = Path(__file__).resolve().parent / "esquemas" / "regras-de-codigo.schema.json"

# A forma dos avisos: depois do texto que os abre, só dados.
QUEBRA = "\n"  # separa as linhas de um item
SEPARADOR = QUEBRA * 2  # separa os textos de regras entregues juntos, e o texto que abre um aviso e cada item dele
ENTRE_DADOS = ": "  # separa os dados de um item: o nome da regra, o caminho, as linhas, o código de saída
ENTRE_TRECHOS = ", "  # separa os trechos de linhas não lidas
LIGA_TRECHO = "-"  # liga a primeira e a última linha de um trecho
ENTRE_PALAVRAS = " "  # separa as palavras da parte de um comando

CURINGA = "*"  # num padrão de nome, vale por qualquer trecho do caminho
QUALQUER = ".*"  # o mesmo, numa expressão regular

# As anotações de uma sessão, pelas chaves do protocolo.anotacao: a pasta com a anotação de cada arquivo escrito e a
# anotação do último arquivo escrito.
ARQUIVOS = "arquivos"
ULTIMO = "ultimo"
PARCIAL = ".parcial"  # o fim do nome da anotação enquanto ela se grava; a que tem esse fim não se lê
IMPRESSAO_DIGITAL = "sha256"  # a conta que guarda, no ok, o conteúdo do arquivo

BARRAM = {"antes": "nega", "fim": "trava"}  # os momentos que deixam barrar, cada um com o modelo com que se barra


def ler_configuracao(arquivo):
    """A configuração, lida pelo molde dela, com os caminhos inteiros, a partir da pasta dela."""
    arquivo = Path(arquivo).resolve()
    dados = le_conferido(arquivo, MOLDE)
    pasta = arquivo.parent
    return {
        "pasta": pasta,
        "estado": (pasta / dados["estado"]).resolve(),
        "regras": [dict(regra, texto=(pasta / regra["texto"]).resolve()) for regra in dados["regras"]],
        "conferencias": dados["conferencias"],
        "ok_de_pessoa": dados["ok_de_pessoa"],
    }


def bate(padroes, caminho):
    """Se o caminho inteiro bate com um dos padrões de nome: o * vale por qualquer trecho, e maiúscula e minúscula
    contam igual."""
    alvo = str(caminho).casefold()
    return any(re.fullmatch(QUALQUER.join(map(re.escape, padrao.casefold().split(CURINGA))), alvo, re.DOTALL)
               for padrao in padroes)


def junta(caminhos):
    """Os textos dos arquivos, na ordem, separados."""
    return SEPARADOR.join(le_texto(caminho).strip() for caminho in caminhos)


def aviso(texto, itens):
    """O texto que abre o aviso, lido do arquivo, e cada item dele, separados."""
    return SEPARADOR.join([junta([texto]), *itens])


def texto_em(valor, campo):
    """O texto do campo, quando o valor é um objeto e o campo traz um texto; None nos outros casos."""
    dentro = valor.get(campo) if isinstance(valor, dict) else None
    return dentro if isinstance(dentro, str) else None


def caminho_do_uso(partes, valor):
    """O caminho inteiro do arquivo que o uso nomeia, a partir da pasta de onde ele roda."""
    return protocolo.caminho(valor, partes.get("pasta"))


def anotacao(config, partes, *chaves):
    """O caminho de uma anotação da sessão do formulário, pelas chaves; sem chaves, o da pasta da sessão."""
    return protocolo.anotacao(config["estado"], partes.get("sessao"), *chaves)


def anotacao_do_arquivo(config, partes, caminho):
    """O caminho da anotação de um arquivo escrito na tarefa."""
    return anotacao(config, partes, ARQUIVOS, str(caminho))


def grava(arquivo, dados):
    """Grava os dados no arquivo, em JSON, de uma vez: quem lê nunca o acha pela metade."""
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding=CODIFICACAO, dir=arquivo.parent, suffix=PARCIAL,
                                     delete=False) as parcial:
        json.dump(dados, parcial, ensure_ascii=False, sort_keys=True)
    os.replace(parcial.name, arquivo)


def lido(arquivo):
    """Os dados da anotação; None quando ela não existe."""
    return le_json(arquivo) if arquivo.is_file() else None


def escritos(config, partes):
    """A anotação de cada arquivo escrito na tarefa, em ordem alfabética do caminho."""
    pasta = anotacao(config, partes, ARQUIVOS)
    if not pasta.is_dir():
        return []
    anotados = [le_json(item) for item in pasta.iterdir() if item.is_file() and item.suffix != PARCIAL]
    return sorted(anotados, key=lambda anotado: anotado["caminho"])


def impressao(caminho):
    """A impressão digital do conteúdo do arquivo."""
    return hashlib.new(IMPRESSAO_DIGITAL, Path(caminho).read_bytes()).hexdigest()


def espera_ok(config, anotado):
    """Se o arquivo escrito existe, é dos que só uma pessoa confere e não tem o ok dela para o conteúdo de agora."""
    caminho = Path(anotado["caminho"])
    return (caminho.is_file() and bate(config["ok_de_pessoa"]["arquivos"], caminho)
            and anotado.get("ok") != impressao(caminho))


def destino_livre(terminal, operador, destino):
    """Se a saída vai para outra saída ou entrada, pelo número dela, ou para um destino livre."""
    if destino is None or destino[1]:
        return False
    alvo = destino[0]
    if operador.endswith(DUPLICACAO) and (alvo.isdigit() or alvo == FECHA_DESCRITOR):
        return True
    return alvo in terminal.destinos_livres


def redirecionamento_que_escreve(terminal, partes):
    """O sinal que manda a saída para um arquivo que não é livre, com o destino, ou o que traz um texto embutido;
    None se não há."""
    for numero, (texto, operador) in enumerate(partes):
        if not operador:
            continue
        if TEXTO_EMBUTIDO in texto:
            return texto
        if ESCRITA in texto and eh_redirecionamento(texto):
            destino = partes[numero + 1] if numero + 1 < len(partes) else None
            if not destino_livre(terminal, texto, destino):
                return ENTRE_PALAVRAS.join([texto] + ([destino[0]] if destino else []))
    return None


def comando_que_escreve(terminal, palavras):
    """O comando que sempre escreve, o que tem uma opção que o faz escrever ou rodar código, com ela, e o programa
    que, chamado sem arquivo, lê código do terminal; None se não há."""
    for posicao in posicoes_de_comando(palavras, terminal.prefixos | terminal.rodam_texto):
        nome = Path(palavras[posicao]).name
        seguintes = palavras[posicao + 1:]
        if nome in terminal.sempre_escrevem:
            return nome
        for opcao in terminal.escrevem_com_opcao.get(nome, ()):
            for palavra in seguintes:
                if opcao_bate(opcao, palavra):
                    return ENTRE_PALAVRAS.join([nome, palavra])
        sem_arquivo = all(palavra.startswith(OPCAO) for palavra in seguintes)
        if nome in terminal.leem_codigo_sem_arquivo and sem_arquivo:
            return nome
    return None


def parte_que_escreve(terminal, comando):
    """A primeira parte da linha, de um comando de dentro dela ou de um texto que ela manda rodar, que escreve num
    arquivo ou roda código escrito no comando; None se não há."""
    for partes, simples in lidos(comando, terminal.rodam_texto):
        achado = redirecionamento_que_escreve(terminal, partes)
        for palavras in simples:
            achado = achado or comando_que_escreve(terminal, palavras)
        if achado:
            return achado
    return None


def inteiro(valor):
    """Se o valor é um número inteiro, e não sim ou não."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def trecho_lido(proto, uso):
    """(o caminho como o uso o escreveu, a primeira linha, a última linha) do que o uso leu, com as linhas contadas a
    partir de 1. None quando o uso não é de uma ferramenta de leitura e quando a leitura não conta: quando a entrada
    traz um campo que a folha não conhece, ou um começo ou uma quantidade que não se leem como linhas. Erro quando a
    leitura não traz o caminho."""
    ferramenta = uso.get("ferramenta")
    leitura = proto["leituras"].get(ferramenta) if isinstance(ferramenta, str) else None
    if leitura is None:
        return None
    entrada = uso.get("entrada")
    caminho = texto_em(entrada, leitura["campo_caminho"])
    if caminho is None:
        raise ErroDeDados(f"a leitura não traz o caminho, no campo {leitura['campo_caminho']!r}")
    conhecidos = {leitura["campo_caminho"], leitura["campo_comeco"], leitura["campo_quantas"],
                  *leitura.get("campos_livres", ())}
    comeco = entrada.get(leitura["campo_comeco"], leitura["primeira_linha"])
    quantas = entrada.get(leitura["campo_quantas"], leitura["linhas_sem_limite"])
    if set(entrada) - conhecidos or not inteiro(comeco) or not inteiro(quantas):
        return None
    if comeco < leitura["primeira_linha"] or quantas < 1:
        return None
    primeira = comeco - leitura["primeira_linha"] + 1
    return caminho, primeira, primeira + quantas - 1


def juntos(trechos):
    """Os trechos de linhas [primeira, última], em ordem, com os que se tocam juntos num só."""
    juntados = []
    for primeira, ultima in sorted(trechos):
        if juntados and primeira <= juntados[-1][1] + 1:
            juntados[-1][1] = max(juntados[-1][1], ultima)
        else:
            juntados.append([primeira, ultima])
    return juntados


def nao_lidas(lidas, total):
    """Os trechos (primeira, última) das linhas de 1 a total que não estão entre as lidas, já em ordem e juntas."""
    faltam, proxima = [], 1
    for primeira, ultima in lidas:
        if primeira > total:
            break
        if primeira > proxima:
            faltam.append((proxima, primeira - 1))
        proxima = max(proxima, ultima + 1)
    if proxima <= total:
        faltam.append((proxima, total))
    return faltam


def escrito(primeira, ultima):
    """Um trecho de linhas, como dado: o número da linha, ou a primeira e a última ligadas."""
    return str(primeira) if primeira == ultima else f"{primeira}{LIGA_TRECHO}{ultima}"


def nega(proto, textos, parte):
    """O bloqueio: o texto que o abre e a parte do comando ou da escrita que o causou."""
    return protocolo.resposta(proto, "nega", aviso(textos["bloqueio"], [parte]))


def antes_do_terminal(terminal, proto, partes, textos):
    """Antes de um comando no terminal: barra o que escreve num arquivo, o que roda código escrito nele e o que não se
    lê; calado quando não há o que barrar."""
    campo = proto["terminal"]["campo_comando"]
    comando = texto_em(partes.get("entrada"), campo)
    if comando is None:
        raise ErroDeDados(f"o uso do terminal não traz o comando, no campo {campo!r}")
    try:
        parte = parte_que_escreve(terminal, comando)
    except ComandoIlegivel as erro:
        parte = str(erro)
    return None if parte is None else nega(proto, textos, parte)


def antes_da_escrita(config, proto, partes, textos):
    """Antes de uma escrita: barra a escrita na pasta das anotações e, enquanto um arquivo espera o ok de uma pessoa, a
    escrita em outro; anota o arquivo como escrito e entrega os textos de regras ligados a ele, na primeira escrita
    nele e na volta a ele depois de escrever em outro."""
    campos = proto["escritas"]["campos_caminho"]
    valores = [valor for valor in (texto_em(partes.get("entrada"), campo) for campo in campos) if valor is not None]
    if not valores:
        raise ErroDeDados(f"a escrita não traz o caminho num campo que a folha conhece: {campos}")
    caminho = caminho_do_uso(partes, valores[0])
    nome = str(caminho)
    if caminho.is_relative_to(config["estado"]):
        return nega(proto, textos, nome)
    esperam = [anotado["caminho"] for anotado in escritos(config, partes) if espera_ok(config, anotado)]
    if esperam and nome not in esperam:
        return nega(proto, textos, nome)
    ultimo = anotacao(config, partes, ULTIMO)
    anterior = lido(ultimo)
    grava(anotacao_do_arquivo(config, partes, caminho), {"caminho": nome, "lidas": []})
    grava(ultimo, {"caminho": nome})
    regras = [regra["texto"] for regra in config["regras"] if bate(regra["arquivos"], caminho)]
    if not regras or (anterior is not None and anterior["caminho"] == nome):
        return None
    return protocolo.resposta(proto, "contexto", junta(regras))


def depois_da_leitura(config, proto, partes, usos):
    """Depois de uma leitura, de um uso só ou de um lote: anota as linhas lidas de cada arquivo escrito na tarefa;
    sempre calado."""
    for uso in usos:
        trecho = trecho_lido(proto, uso)
        if trecho is None:
            continue
        valor, primeira, ultima = trecho
        arquivo = anotacao_do_arquivo(config, partes, caminho_do_uso(partes, valor))
        anotado = lido(arquivo)
        if anotado is not None:  # a leitura de um arquivo que a tarefa não escreveu não se confere
            anotado["lidas"] = juntos(anotado["lidas"] + [[primeira, ultima]])
            grava(arquivo, anotado)
    return None


def na_mensagem(config, proto, partes):
    """Na mensagem da pessoa: quando ela é o texto do ok seguido do caminho de um arquivo escrito, anota o ok para o
    conteúdo de agora do arquivo; sempre calado."""
    texto = texto_em(partes, "mensagem")
    if texto is None:
        raise ErroDeDados(f"a mensagem da pessoa não traz o texto, no campo {proto['chaves'].get('mensagem')!r}")
    abre = config["ok_de_pessoa"]["mensagem"]
    mensagem = texto.strip()
    if not mensagem.startswith(abre):
        return None
    caminho = caminho_do_uso(partes, mensagem[len(abre):].strip())
    arquivo = anotacao_do_arquivo(config, partes, caminho)
    anotado = lido(arquivo)
    if anotado is not None and caminho.is_file():
        anotado["ok"] = impressao(caminho)
        grava(arquivo, anotado)
    return None


def no_fim(config, proto, partes, textos):
    """No fim da resposta: trava quando falta leitura ou uma conferência não passa, avisa quando só falta o ok de uma
    pessoa e, quando tudo passa, apaga as anotações da sessão."""
    falta, esperam = [], []
    for anotado in escritos(config, partes):
        caminho = Path(anotado["caminho"])
        if not caminho.is_file():
            continue  # o arquivo que não existe mais não tem o que ler nem o que conferir
        faltam = nao_lidas(anotado["lidas"], len(le_texto(caminho).splitlines()))
        if faltam:
            trechos = ENTRE_TRECHOS.join(escrito(primeira, ultima) for primeira, ultima in faltam)
            falta.append(ENTRE_DADOS.join([anotado["caminho"], trechos]))
        for conferencia in config["conferencias"]:
            if not bate(conferencia["arquivos"], caminho):
                continue
            rodado = resultado(conferencia["comando"] + [anotado["caminho"]], config["pasta"])
            if rodado.fim != PASSOU:
                cabeca = ENTRE_DADOS.join([conferencia["nome"], anotado["caminho"], str(rodado.codigo)])
                falta.append(QUEBRA.join(parte for parte in (cabeca, rodado.saida.strip(), rodado.erro.strip())
                                         if parte))
        if espera_ok(config, anotado):
            esperam.append(anotado["caminho"])
    if falta:
        return protocolo.resposta(proto, "trava", aviso(textos["fim"], falta))
    if esperam:
        return protocolo.resposta(proto, "aviso", aviso(textos["fim"], esperam))
    sessao = anotacao(config, partes)
    if sessao.is_dir():
        shutil.rmtree(sessao)
    return None


def trata(args, proto, partes):
    """O que o vigia responde ao formulário; None quando ele fica calado."""
    config = ler_configuracao(args.config)
    anotacao(config, partes)  # a sessão sem identificação dá erro em todo momento
    terminal = configuracao_do_terminal(args.terminal)
    textos = {"fim": args.fim, "bloqueio": args.bloqueio}
    for texto in textos.values():  # o texto que falta dá erro em todo momento, também no que não o usa
        le_texto(texto)
    evento = partes["evento"]
    if evento == "antes" and partes.get("ferramenta") == proto["terminal"]["ferramenta"]:
        return antes_do_terminal(terminal, proto, partes, textos)
    if evento == "antes":
        return antes_da_escrita(config, proto, partes, textos)
    if evento == "depois":
        return depois_da_leitura(config, proto, partes, [partes])
    if evento == "lote":
        return depois_da_leitura(config, proto, partes, protocolo.chamadas(proto, partes))
    if evento == "mensagem":
        return na_mensagem(config, proto, partes)
    return no_fim(config, proto, partes, textos)


def main(argumentos=None):
    """Lê as opções e o formulário, responde no formato da folha e escreve a resposta, quando há uma."""
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    leitor.add_argument("--config", required=True, type=Path, help="a configuração do vigia")
    leitor.add_argument("--terminal", required=True, type=Path, help="a configuração do terminal")
    leitor.add_argument("--protocolo", required=True, type=Path, help="a folha do protocolo do programa")
    leitor.add_argument("--fim", required=True, type=Path, help="o texto que abre o aviso do fim da resposta")
    leitor.add_argument("--bloqueio", required=True, type=Path, help="o texto que abre o aviso de bloqueio")
    args = leitor.parse_args(argumentos)
    try:
        proto = protocolo.ler(args.protocolo)
        partes = protocolo.le_evento(proto, sys.stdin.read())
    except ErroDeDados as erro:  # sem a folha ou sem o momento, não há como responder no formato do programa
        raise SystemExit(str(erro)) from None
    try:
        saida = trata(args, proto, partes)
    except ErroDeDados as erro:
        if partes["evento"] not in BARRAM:
            raise SystemExit(str(erro)) from None
        saida = protocolo.resposta(proto, BARRAM[partes["evento"]], str(erro))
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
