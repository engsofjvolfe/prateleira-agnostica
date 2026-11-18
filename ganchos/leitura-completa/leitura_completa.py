"""Vigia que só deixa a IA ler um documento inteiro, do começo ao fim.

Lê o formulário do programa pela entrada padrão, em JSON, pela folha do protocolo
(--protocolo), e anota, de cada sessão, até que linha cada arquivo foi lido, num arquivo da
pasta de estado da configuração (--config). A cada consulta, antes de tudo, pergunta à
conferencia-de-protecao, com a lista (--lista), se a IA continua sem conseguir alterar os
arquivos que o projeto fechou para ela; enquanto ela consegue, barra todo uso e trava o fim,
com o que a conferência achou, e não anota nada. Em cada momento:
  - antes de um uso: o de uma ferramenta de leitura só passa quando a entrada só tem os
    campos que a folha conhece para ela e a leitura começa na primeira linha do arquivo ou na
    seguinte à última lida dele; o de uma ferramenta de escrita (uma troca ou um inteiro da
    folha) barra quando cai na pasta de estado e, fora dela, só passa quando nenhum arquivo
    está lido só em parte; o de uma ferramenta que lê de
    outro jeito (a do terminal, as de busca e as de resumo da folha) barra, com o nome dela; o
    de outra ferramenta passa calado;
  - depois de um lote de usos: anota, de cada leitura, as linhas que vieram de fato, pelos
    números das linhas numeradas do que ela devolveu, e não pelo que se pediu; vale o trecho
    seguido que começa na primeira linha devolvida, quando ele começa na primeira linha do
    arquivo ou na seguinte à última lida, e só até a última linha que o arquivo tem;
  - no fim da resposta: trava enquanto houver arquivo lido só em parte.
A anotação guarda a impressão digital do trecho lido, e o que ela diz de um arquivo deixa de
valer quando esse trecho muda; o arquivo que só cresce depois dele continua de onde parou. As
linhas de um arquivo são contadas nele mesmo, com as quebras de linha que o leitor de texto da
central entende; o arquivo que não existe ou não se lê como texto não tem o que ler. A
resposta que barra ou trava traz o texto do motivo ou do fim (--motivo, --fim) e, uma por
linha, cada parte que a causou: o arquivo e a última linha lida dele, com a última que ele
tem; o arquivo e o campo que a folha não conhece para a leitura; ou o nome da ferramenta que
lê de outro jeito. O que não serve (configuração, folha, texto, formulário ou anotação fora da
forma) dá a mensagem na saída de erro e sai com o código 2. Os mecanismos da central chegam
pelo comando, que começa pelo roda.py. Só biblioteca padrão, num sistema que tranca arquivos
como o Linux.
"""
import argparse
import fcntl
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import protocolo
from conferencia_de_molde import le_conferido
from conferencia_de_protecao import achados_da_lista
from erro_de_dados import ErroDeDados
from expressao_regular import compila
from leitura_de_texto import CODIFICACAO, le_texto
from tipo_de_json import do_tipo

PASTA = Path(__file__).resolve().parent
MOLDE = PASTA / "esquemas" / "leitura-completa.schema.json"
MOLDE_DA_ANOTACAO = PASTA / "esquemas" / "anotacao.schema.json"
NAO_SERVE = 2  # o código de saída quando a configuração, um argumento, um texto ou o formulário não serve
QUEBRA = "\n"  # o que separa as linhas de um texto já lido pela central
IMPRESSAO = "sha256"  # a conta que faz a impressão digital do trecho lido
TRAVA = ".trava"  # o fim do nome do arquivo que tranca a anotação de uma sessão


def le_configuracao(caminho):
    """A configuração, lida pelo molde, com a pasta de estado a partir da pasta dela."""
    dados = le_conferido(caminho, MOLDE)
    return {"estado": Path(caminho).resolve().parent / dados["estado"]}


def chave_do(caminho, pasta):
    """O caminho de um arquivo como chave da anotação: absoluto, a partir da pasta de onde o
    uso roda, e sem atalhos, pelo protocolo."""
    return str(protocolo.caminho(caminho, pasta))


def linhas_do(chave):
    """As linhas do arquivo, com as quebras de linha que o leitor de texto da central entende;
    None quando o arquivo não existe ou não se lê como texto."""
    try:
        texto = le_texto(chave)
    except ErroDeDados:
        return None
    linhas = texto.split(QUEBRA)
    return linhas[:-1] if linhas and linhas[-1] == "" else linhas


def ultima_de(linhas, primeira):
    """O número da última linha do arquivo, com a primeira linha no número dado."""
    return primeira + len(linhas) - 1


def impressao_de(linhas, quantas):
    """A impressão digital das primeiras linhas do arquivo, que são o trecho já lido."""
    return hashlib.new(IMPRESSAO, QUEBRA.join(linhas[:quantas]).encode(CODIFICACAO)).hexdigest()


def lida_de(anotado, chave, primeira, linhas):
    """O número da última linha lida do arquivo, na numeração da primeira linha dada; a de
    antes da primeira quando nada se leu nessa numeração e quando o trecho anotado não é mais o
    que está no arquivo, porque aí o que estava anotado deixa de valer."""
    nota = anotado.get(chave)
    if nota is None or nota["primeira"] != primeira or linhas is None:
        return primeira - 1
    quantas = nota["lida"] - primeira + 1
    if quantas > len(linhas) or impressao_de(linhas, quantas) != nota["impressao"]:
        return primeira - 1
    return nota["lida"]


def situacao(chave, lida, ultima):
    """A parte que causa um bloqueio: o arquivo e a última linha lida dele, com a última que
    ele tem."""
    return f"{chave}: {lida}/{ultima}"


def em_parte(anotado):
    """A situação de cada arquivo anotado lido só em parte, em ordem."""
    saida = []
    for chave in sorted(anotado):
        linhas = linhas_do(chave)
        if linhas is None:
            continue
        primeira = anotado[chave]["primeira"]
        lida, ultima = lida_de(anotado, chave, primeira, linhas), ultima_de(linhas, primeira)
        if lida < ultima:
            saida.append(situacao(chave, lida, ultima))
    return saida


def le_anotado(arquivo):
    """O que a anotação da sessão guarda, {arquivo: {"primeira": número, "lida": número,
    "impressao": texto}}, conferido pelo molde dela; vazio quando ela não existe; erro
    (ErroDeDados) quando ela está fora do molde."""
    if not arquivo.exists():
        return {}
    return le_conferido(arquivo, MOLDE_DA_ANOTACAO)


def grava_anotado(arquivo, anotado):
    """Grava a anotação inteira de uma vez: num arquivo novo da mesma pasta, que toma o lugar
    do antigo, para que quem lê nunca a veja pela metade."""
    with tempfile.NamedTemporaryFile("w", encoding=CODIFICACAO, dir=arquivo.parent, delete=False) as novo:
        json.dump(anotado, novo, ensure_ascii=False, sort_keys=True)
    os.replace(novo.name, arquivo)


@contextmanager
def trancado(arquivo):
    """Tranca a anotação da sessão enquanto ela se lê e se grava, para que dois lotes ao mesmo
    tempo não perquem a anotação um do outro."""
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo.with_name(arquivo.name + TRAVA), "a", encoding=CODIFICACAO) as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        yield


def confere_leitura(leitura, entrada, pasta, anotado):
    """As partes que barram a leitura: cada campo da entrada que a folha não conhece para ela,
    ou a situação do arquivo, quando ela não começa na primeira linha nem na seguinte à última
    lida; nenhuma quando ela pode rodar, também quando o arquivo não tem o que ler."""
    caminho = entrada.get(leitura["campo_caminho"])
    if not isinstance(caminho, str) or not caminho:
        raise ErroDeDados(f"a entrada da leitura não tem o texto {leitura['campo_caminho']!r}, o caminho do arquivo")
    chave = chave_do(caminho, pasta)
    conhecidos = {leitura["campo_caminho"], leitura["campo_comeco"], leitura["campo_quantas"],
                  *leitura.get("campos_livres", [])}
    estranhos = sorted(set(entrada) - conhecidos)
    if estranhos:
        return [f"{chave}: {campo}" for campo in estranhos]
    primeira, linhas = leitura["primeira_linha"], linhas_do(chave)
    if linhas is None:
        return []
    comeco, lida = entrada.get(leitura["campo_comeco"], primeira), lida_de(anotado, chave, primeira, linhas)
    if not do_tipo(comeco, "integer") or comeco not in (primeira, lida + 1):
        return [situacao(chave, lida, ultima_de(linhas, primeira))]
    return []


def escritas(proto):
    """As ferramentas que escrevem, pela folha: as que trocam um trecho e as que gravam o
    arquivo inteiro."""
    return set(proto["escritas"]["trocas"]) | set(proto["escritas"]["inteiros"])


def outros_leitores(proto):
    """As ferramentas que leem um arquivo de outro jeito, pela folha: a do terminal, as de
    busca e as que leem por outro modelo de IA e entregam um resumo."""
    return {proto["terminal"]["ferramenta"], *proto["buscas"], *proto["resumos"]}


def na_pasta_de_estado(proto, entrada, pasta, estado):
    """Os arquivos que a escrita alteraria dentro da pasta de estado, pelos campos de caminho da
    folha, em ordem. Erro (ErroDeDados) quando a escrita não traz nenhum desses campos, porque
    aí não se sabe onde ela cai."""
    campos = proto["escritas"]["campos_caminho"]
    valores = [entrada[campo] for campo in campos if isinstance(entrada.get(campo), str) and entrada[campo]]
    if not valores:
        raise ErroDeDados(f"a escrita não traz o caminho num campo que a folha conhece: {campos}")
    chaves = (chave_do(valor, pasta) for valor in valores)
    return [chave for chave in chaves if Path(chave).is_relative_to(estado)]


def antes(proto, partes, anotado, estado):
    """As partes que barram o uso de antes, pela ferramenta dele."""
    ferramenta, entrada = partes.get("ferramenta"), partes.get("entrada")
    if not isinstance(ferramenta, str) or not isinstance(entrada, dict):
        raise ErroDeDados("o formulário de antes não traz a ferramenta, um texto, e a entrada, um objeto")
    if ferramenta in proto["leituras"]:
        return confere_leitura(proto["leituras"][ferramenta], entrada, partes.get("pasta"), anotado)
    if ferramenta in escritas(proto):
        return na_pasta_de_estado(proto, entrada, partes.get("pasta"), estado) or em_parte(anotado)
    if ferramenta in outros_leitores(proto):
        return [ferramenta]
    return []


def trecho_seguido(forma, devolvido):
    """(primeiro, último) número do trecho seguido de linhas numeradas que começa na primeira
    linha numerada do que a leitura devolveu, em cada texto de dentro dele; None quando nada
    veio numerado."""
    numeros = [int(achada.group(protocolo.LINHA)) for texto in protocolo.textos_de(devolvido)
               for linha in texto.split(QUEBRA) for achada in [forma.match(linha)] if achada]
    if not numeros:
        return None
    ultimo = numeros[0]
    for numero in numeros[1:]:
        if numero != ultimo + 1:
            break
        ultimo = numero
    return numeros[0], ultimo


def anota_lote(proto, partes, anotado):
    """Anota, de cada leitura do lote, o trecho seguido que veio, quando ele começa na primeira
    linha do arquivo ou na seguinte à última lida, até a última linha que o arquivo tem, para
    que a linha que entra depois nele não fique por lida, com a impressão digital do trecho;
    diz se a anotação mudou."""
    mudou = False
    for chamada in protocolo.chamadas(proto, partes):
        leitura = proto["leituras"].get(chamada.get("ferramenta"))
        entrada = chamada.get("entrada")
        if leitura is None or "resposta" not in chamada or not isinstance(entrada, dict):
            continue
        if "linha_numerada" not in leitura:
            raise ErroDeDados(f"a folha não diz a forma da linha numerada de {chamada['ferramenta']!r}")
        caminho = entrada.get(leitura["campo_caminho"])
        trecho = trecho_seguido(compila(leitura["linha_numerada"], "linha_numerada"), chamada["resposta"])
        if not isinstance(caminho, str) or not caminho or trecho is None:
            continue
        primeira, (de, ate) = leitura["primeira_linha"], trecho
        chave = chave_do(caminho, partes.get("pasta"))
        linhas = linhas_do(chave)
        if linhas is None:
            continue
        if de in (primeira, lida_de(anotado, chave, primeira, linhas) + 1):
            ate = min(ate, ultima_de(linhas, primeira))
            anotado[chave] = {"primeira": primeira, "lida": ate,
                              "impressao": impressao_de(linhas, ate - primeira + 1)}
            mudou = True
    return mudou


def trabalho(args, texto):
    """A resposta do vigia ao formulário, ou None quando ele não tem o que dizer."""
    config = le_configuracao(args.config)
    proto = protocolo.ler(args.protocolo)
    textos = {"nega": le_texto(args.motivo), "trava": le_texto(args.fim)}
    partes = protocolo.le_evento(proto, texto)
    arquivo = protocolo.anotacao(config["estado"], partes.get("sessao"))
    achados = achados_da_lista(args.lista)
    if partes["evento"] == "lote":
        if achados:  # com a proteção aberta, a anotação não se grava
            return None
        with trancado(arquivo):
            anotado = le_anotado(arquivo)
            if anota_lote(proto, partes, anotado):
                grava_anotado(arquivo, anotado)
        return None
    qual = "trava" if partes["evento"] == "fim" else "nega"
    if achados:
        causas = achados
    elif qual == "trava":
        causas = em_parte(le_anotado(arquivo))
    else:
        causas = antes(proto, partes, le_anotado(arquivo), config["estado"].resolve())
    if not causas:
        return None
    return protocolo.resposta(proto, qual, textos[qual].rstrip() + QUEBRA + QUEBRA.join(causas))


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path, help="a configuração da peça")
    leitor.add_argument("--protocolo", required=True, type=Path, help="a folha do protocolo do programa")
    leitor.add_argument("--lista", required=True, type=Path,
                        help="a lista dos arquivos e das pastas que o projeto fechou para a IA")
    leitor.add_argument("--motivo", required=True, type=Path, help="o texto do uso barrado")
    leitor.add_argument("--fim", required=True, type=Path, help="o texto da resposta travada")
    args = leitor.parse_args(argumentos)
    try:
        saida = trabalho(args, sys.stdin.read())
    except ErroDeDados as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        sys.exit(NAO_SERVE)
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
