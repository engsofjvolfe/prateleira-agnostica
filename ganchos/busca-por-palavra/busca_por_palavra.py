"""
O vigia que barra a busca por palavra.

Antes de tudo, pergunta à conferencia-de-protecao, com a lista (--lista), se a IA continua sem conseguir alterar os
arquivos que o projeto fechou para ela; enquanto ela consegue, barra todo uso, com o que a conferência achou.

Antes de um uso da ferramenta de terminal: barra o comando de busca, ou um de dentro de
outro, quando um padrão dele não é um dos livres; quando ele tira os padrões de um arquivo;
quando não dá para saber o que ele procura; e barra a linha que não se lê. Antes de um uso
de uma ferramenta de busca: barra a busca cujo padrão não é um dos livres. O que ele
responde é o texto do motivo, com a parte que causou o bloqueio.

Com --exatas, um arquivo e uma forma, uma vez para cada arquivo, passa também, no terminal,
a busca exata: a que lê só esse arquivo, com cada padrão seguindo a forma inteira e sem
nenhum sinal que a busca lê como padrão.

Os comandos de busca, as opções de cada um e os padrões livres vêm da configuração
(--config), lida pelo molde em esquemas/busca-por-palavra.schema.json; o jeito de ler a
linha do terminal, da configuração do terminal (--terminal); o texto do motivo, do arquivo
dado em --motivo; e os nomes do programa, da folha do protocolo (--protocolo).
"""
import argparse
import json
import sys
from collections import namedtuple
from pathlib import Path

import protocolo
from conferencia_de_molde import le_conferido
from conferencia_de_protecao import achados_da_lista
from erro_de_dados import ErroDeDados
from expressao_regular import compila
from leitura_de_texto import le_texto
from leitura_do_terminal import (ATRIBUICAO, OPCAO, OPCAO_LONGA, ComandoIlegivel, comandos_achados,
                                 configuracao_do_terminal)
from repetidos import repetidos

MOLDE = Path(__file__).resolve().parent / "esquemas" / "busca-por-palavra.schema.json"
MOMENTO = "antes"  # o momento que o vigia trata, pelo nome no molde da folha do protocolo
RESPOSTA = "nega"  # o modelo com que o vigia responde, pelo nome no molde da folha do protocolo
QUEBRA = "\n"  # o que separa o texto do motivo da parte que causou o bloqueio
FIM_DAS_OPCOES = OPCAO_LONGA  # a palavra depois da qual toda palavra de uma busca é solta
# as listas de opções de um comando de busca, pelo nome no molde da configuração
DO_PADRAO, DE_ARQUIVO, COM_VALOR, SEM_VALOR = ("opcoes_do_padrao", "opcoes_de_arquivo", "opcoes_com_valor",
                                               "opcoes_sem_valor")
LISTAS = (DO_PADRAO, DE_ARQUIVO, COM_VALOR, SEM_VALOR)
LEVAM_VALOR = (DO_PADRAO, DE_ARQUIVO, COM_VALOR)
SINAIS_DE_PADRAO = frozenset("\\.*+?[](){}^$|")  # os sinais que uma busca lê como padrão, e não como letra
Exata = namedtuple("Exata", "arquivo forma")  # a busca exata: o arquivo, sem atalhos, e a forma de cada padrão


def ler_configuracao(caminho, terminal):
    """A configuração do vigia, conferida, com a configuração do terminal: os padrões livres e, de cada comando
    de busca, as palavras dele e a lista em que está cada opção que ele cita. Erro (ErroDeDados) quando uma opção
    de um comando aparece mais de uma vez."""
    dados = le_conferido(Path(caminho), MOLDE)
    buscas = []
    for numero, busca in enumerate(dados["buscas"]):
        mesmas = repetidos([opcao for lista in LISTAS for opcao in busca[lista]])
        if mesmas:
            raise ErroDeDados(f"{caminho}: buscas/{numero}: opção que aparece mais de uma vez: {mesmas}")
        buscas.append({"palavras": busca["comando"].split(),
                       "opcoes": {opcao: lista for lista in LISTAS for opcao in busca[lista]}})
    return {"livres": frozenset(dados["padroes_livres"]), "terminal": configuracao_do_terminal(terminal),
            "buscas": buscas}


def buscas_exatas(pares):
    """As Exatas do --exatas, uma para cada par (arquivo, forma); nenhuma sem ele. Erro (ErroDeDados) quando o
    arquivo não existe e quando a forma não é uma expressão regular válida."""
    exatas = []
    for caminho, forma in pares or []:
        arquivo = Path(caminho).resolve()
        if not arquivo.is_file():
            raise ErroDeDados(f"--exatas: o arquivo {arquivo} não existe")
        exatas.append(Exata(arquivo, compila(forma, f"--exatas: a forma de {arquivo}")))
    return exatas


def _opcoes_da_palavra(opcoes, palavra):
    """(opção, valor colado nela) de cada opção que a palavra traz; o valor é None quando não vem colado. A longa
    traz o valor depois de "="; a palavra que é uma opção citada vale inteira; a outra é um grupo de opções de uma
    letra, que acaba na primeira que leva valor (o resto da palavra é o valor dela) ou que a configuração não
    cita."""
    if palavra.startswith(OPCAO_LONGA):
        nome, sinal, valor = palavra.partition(ATRIBUICAO)
        yield nome, (valor if sinal else None)
    elif palavra in opcoes:
        yield palavra, None
    else:
        letras = palavra[len(OPCAO):]
        for numero, letra in enumerate(letras):
            opcao = OPCAO + letra
            leva_valor = opcoes.get(opcao) in LEVAM_VALOR
            yield opcao, ((letras[numero + 1:] or None) if leva_valor else None)
            if leva_valor or opcao not in opcoes:
                return


def le_busca(opcoes, seguintes):
    """(padrões, arquivos) da busca, pelas palavras que vêm depois do comando dela e pela lista de cada opção que a
    configuração cita; None quando não dá para saber o que ela procura. Os padrões são o valor de cada opção de
    padrão e, sem nenhuma, a primeira palavra solta; os arquivos são as outras soltas. Solta é a palavra que não é
    opção nem valor de opção, e toda palavra depois de FIM_DAS_OPCOES. Não dá para saber quando a busca traz uma
    opção que a configuração não cita, uma opção depois de uma palavra solta, uma opção que tira os padrões de um
    arquivo, uma opção sem valor com um valor colado, uma opção sem o valor que ela leva ou nenhum padrão."""
    padroes, soltas, palavras = [], [], iter(seguintes)
    for palavra in palavras:
        if palavra == FIM_DAS_OPCOES:
            soltas.extend(palavras)
            break
        if palavra == OPCAO or not palavra.startswith(OPCAO):
            soltas.append(palavra)
            continue
        if soltas:
            return None
        for opcao, colado in _opcoes_da_palavra(opcoes, palavra):
            lista = opcoes.get(opcao)
            if lista not in LEVAM_VALOR:
                if lista is None or colado is not None:
                    return None
                continue
            valor = colado if colado is not None else next(palavras, None)
            if lista == DE_ARQUIVO or valor is None:
                return None
            if lista == DO_PADRAO:
                padroes.append(valor)
    if padroes:
        return padroes, soltas
    return ([soltas[0]], soltas[1:]) if soltas else None


def _arquivo(pasta, nome):
    """O caminho sem atalhos do arquivo de uma busca, a partir da pasta de onde o comando roda; None quando o nome
    não é absoluto e a pasta não é texto."""
    if isinstance(pasta, str):
        return (Path(pasta) / nome).resolve()
    return Path(nome).resolve() if Path(nome).is_absolute() else None


def eh_exata(exata, pasta, padroes, arquivos):
    """Se a busca é a exata: tem ao menos um arquivo, e todos são o da exata; e cada padrão segue a forma inteira,
    sem nenhum sinal que a busca lê como padrão."""
    return (bool(arquivos) and all(_arquivo(pasta, nome) == exata.arquivo for nome in arquivos)
            and all(exata.forma.fullmatch(padrao) and not SINAIS_DE_PADRAO & set(padrao) for padrao in padroes))


def passa(config, exatas, pasta, opcoes, seguintes):
    """Se a busca passa: dá para saber o que ela procura, e todos os padrões dela são livres ou ela é a exata de
    um arquivo do --exatas."""
    lida = le_busca(opcoes, seguintes)
    if lida is None:
        return False
    padroes, arquivos = lida
    if all(padrao in config["livres"] for padrao in padroes):
        return True
    return any(eh_exata(exata, pasta, padroes, arquivos) for exata in exatas)


def parte_barrada(config, exatas, pasta, comando):
    """A primeira busca barrada da linha, ou de um comando de dentro dela, da palavra do comando de busca em
    diante; None quando não há. ComandoIlegivel quando a linha não se lê."""
    buscas = config["buscas"]
    procurados = [busca["palavras"] for busca in buscas]
    for indice, seguintes, trecho in comandos_achados(comando, procurados, config["terminal"]):
        if not passa(config, exatas, pasta, buscas[indice]["opcoes"], seguintes):
            return trecho
    return None


def o_que_barra(config, folha, exatas, partes):
    """O que barra o uso: no terminal, a busca barrada, o sinal que deixou a linha sem leitura ou o comando que
    não é um texto; numa ferramenta de busca, o padrão que não é livre; None quando nada barra. Erro (ErroDeDados)
    quando a ferramenta não é a de terminal nem uma de busca."""
    ferramenta, entrada = partes.get("ferramenta"), partes.get("entrada")
    terminal = folha["terminal"]
    if ferramenta == terminal["ferramenta"]:
        comando = entrada.get(terminal["campo_comando"]) if isinstance(entrada, dict) else None
        if not isinstance(comando, str):
            return f"{ferramenta}: {comando!r}"
        try:
            return parte_barrada(config, exatas, partes.get("pasta"), comando)
        except ComandoIlegivel as erro:
            return str(erro)
    if isinstance(ferramenta, str) and ferramenta in folha["buscas"]:
        padrao = entrada.get(folha["buscas"][ferramenta]) if isinstance(entrada, dict) else None
        livre = isinstance(padrao, str) and padrao in config["livres"]
        return None if livre else f"{ferramenta}: {padrao}"
    raise ErroDeDados(f"a ferramenta {ferramenta!r} não é a de terminal nem uma de busca")


def responde(args, formulario):
    """O que o vigia responde ao formulário, pelo modelo da folha do protocolo; None quando ele deixa passar. Erro
    (ErroDeDados) quando um arquivo não se lê ou não segue o molde e quando o momento não é o de antes de um uso."""
    config = ler_configuracao(args.config, args.terminal)
    motivo = le_texto(args.motivo).strip()
    exatas = buscas_exatas(args.exatas)
    folha = protocolo.ler(args.protocolo)
    partes = protocolo.le_evento(folha, formulario)
    if partes["evento"] != MOMENTO:
        raise ErroDeDados(f"o vigia trata só o momento de antes de um uso, e chegou o de {partes['evento']}")
    achados = achados_da_lista(args.lista)
    if achados:
        return protocolo.resposta(folha, RESPOSTA, motivo + QUEBRA + QUEBRA.join(achados))
    parte = o_que_barra(config, folha, exatas, partes)
    return None if parte is None else protocolo.resposta(folha, RESPOSTA, motivo + QUEBRA + parte)


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    leitor.add_argument("--config", required=True, type=Path,
                        help="a configuração, com os comandos de busca e os padrões livres")
    leitor.add_argument("--terminal", required=True, type=Path, help="a configuração do terminal")
    leitor.add_argument("--protocolo", required=True, type=Path, help="a folha do protocolo")
    leitor.add_argument("--lista", required=True, type=Path,
                        help="a lista dos arquivos e das pastas que o projeto fechou para a IA")
    leitor.add_argument("--motivo", required=True, type=Path, help="o texto do motivo do bloqueio")
    leitor.add_argument("--exatas", nargs=2, action="append", metavar=("ARQUIVO", "FORMA"),
                        help="o arquivo de uma busca exata e a forma de cada padrão dela, uma expressão regular; "
                             "uma vez para cada arquivo")
    args = leitor.parse_args(argumentos)
    try:
        saida = responde(args, sys.stdin.read())
    except ErroDeDados as erro:
        raise SystemExit(str(erro)) from None
    if saida is not None:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    main()
