"""
Os caminhos que um caminho cobre: os lugares do disco que uma peça trata quando trata o caminho.

Um arquivo cobre a si mesmo. Uma pasta cobre a si mesma e tudo o que está dentro dela, também nas pastas de dentro;
um atalho de dentro dela conta, mas não se segue. Um atalho cobre a si mesmo e o que cobre o caminho para onde ele
leva. Um caminho que ainda não existe cobre a pasta em que vai aparecer, sem o que está dentro dela.

Dá às peças: cobertos, destino_do_atalho, lugar_real e os tipos de caminho ARQUIVO, PASTA, ATALHO, ONDE_VAI_APARECER
e FALTA.

Todo erro é um ErroDeDados.
"""
import os
from collections import namedtuple

from erro_de_dados import ErroDeDados

ARQUIVO = "arquivo"  # o tipo do caminho que é um arquivo
PASTA = "pasta"  # o tipo da pasta, coberta com tudo o que está dentro dela
ATALHO = "atalho"  # o tipo do caminho que é um atalho
ONDE_VAI_APARECER = "onde_vai_aparecer"  # o tipo da pasta em que um caminho que ainda não existe vai aparecer
FALTA = "falta"  # o tipo da pasta em que um caminho que ainda não existe vai aparecer, quando ela também não existe

# Um caminho coberto: o caminho, o tipo dele e se ele está dentro de uma pasta coberta.
Coberto = namedtuple("Coberto", "caminho tipo de_dentro")


def lugar_real(caminho):
    """O lugar do disco em que o caminho fica: a pasta dele no lugar real, e o último nome como está, sem seguir o
    atalho que ele seja."""
    return os.path.join(os.path.realpath(os.path.dirname(caminho)), os.path.basename(caminho))


def destino_do_atalho(atalho):
    """O caminho para onde o atalho leva, escrito desde o início do disco. O que o atalho guarda conta a partir do
    lugar real da pasta dele, e o ".." sobe a partir do lugar real, como o computador faz: a pasta do atalho, e as do
    que ele guarda, podem ser alcançadas por outros atalhos. O último nome não se segue: o atalho que leva a outro
    atalho dá esse outro, e não o último da fila. Erro (ErroDeDados) quando o atalho não se lê."""
    try:
        guardado = os.readlink(atalho)
    except OSError as erro:
        raise ErroDeDados(f"{atalho}: o atalho não se lê: {erro}") from None
    destino = os.path.join(os.path.realpath(os.path.dirname(atalho)), guardado)
    if os.path.basename(destino) in ("", os.curdir, os.pardir):
        return os.path.realpath(destino)
    return lugar_real(destino)


def _tipo(caminho):
    """O tipo do caminho que existe, sem seguir atalho: ATALHO, PASTA ou ARQUIVO."""
    if os.path.islink(caminho):
        return ATALHO
    return PASTA if os.path.isdir(caminho) else ARQUIVO


def _nomes(pasta):
    """Os caminhos do que está na pasta, do último ao primeiro em ordem de nome, para saírem de uma pilha na ordem.
    Erro (ErroDeDados) quando a pasta não se deixa ler."""
    try:
        nomes = sorted(os.listdir(pasta), reverse=True)
    except OSError as erro:
        raise ErroDeDados(f"{pasta}: a pasta não se lê: {erro}") from None
    return [os.path.join(pasta, nome) for nome in nomes]


def _de_dentro(pasta, vistos):
    """Cada caminho de dentro da pasta e das pastas de dentro dela, em ordem: cada pasta antes do que está nela, e o
    que está numa pasta em ordem de nome. O atalho de dentro não se segue. O caminho já visto não volta, nem o que
    está dentro dele. A volta se dá por uma pilha, e não por chamadas uma dentro da outra, para a pasta muito funda
    não parar a peça."""
    cobertos_de_dentro, pilha = [], _nomes(pasta)
    while pilha:
        caminho = pilha.pop()
        if caminho in vistos:
            continue
        vistos.add(caminho)
        tipo = _tipo(caminho)
        cobertos_de_dentro.append(Coberto(caminho, tipo, True))
        if tipo == PASTA:
            pilha += _nomes(caminho)
    return cobertos_de_dentro


def cobertos(caminho, vistos):
    """Os caminhos que o caminho cobre, em ordem, cada um um Coberto. O caminho que está em vistos não volta, e cada
    caminho que vem entra em vistos: assim, o lugar que dois caminhos cobrem vem uma vez só, e o atalho que leva a si
    mesmo para. Erro (ErroDeDados) quando o caminho não começa no início do disco, quando uma pasta coberta não se
    deixa ler e quando um atalho coberto não se lê."""
    if not os.path.isabs(caminho):
        raise ErroDeDados(f"caminho que não começa no início do disco: {caminho}")
    resposta, atual, com_o_de_dentro = [], caminho, True
    while atual not in vistos:
        vistos.add(atual)
        if not os.path.lexists(atual):
            if not com_o_de_dentro:
                resposta.append(Coberto(atual, FALTA, False))
                break
            atual, com_o_de_dentro = os.path.dirname(atual), False
            continue
        tipo = _tipo(atual)
        if tipo == PASTA and not com_o_de_dentro:
            tipo = ONDE_VAI_APARECER
        resposta.append(Coberto(atual, tipo, False))
        if tipo != ATALHO:
            if tipo == PASTA:
                resposta += _de_dentro(atual, vistos)
            break
        atual = destino_do_atalho(atual)
    return resposta
