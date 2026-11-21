"""
Prova que o teste de uma peça pega os defeitos dela.

A peça testada se copia para a pasta de trabalho: uma vez sem estrago e uma vez para cada
estrago da lista, que é a troca de um trecho de um arquivo dela por outro. O teste roda
contra cada cópia, por um comando que recebe, depois das palavras dele, a pasta da cópia e
uma pasta vazia para o que ele gravar. O código de saída do comando diz como o teste acabou:
0, passou; 1, falhou; outro, quebrou. O teste que passa do limite de tempo é cortado, com
tudo o que ele pôs para rodar. O teste tem de passar na cópia sem estrago; um estrago é pego
quando o teste falha na cópia dele.

Dá às peças: prova. Todo erro do que a prova recebe é um ErroDeDados.
"""
import math
import os
import shutil
import signal
import subprocess
from pathlib import Path, PurePosixPath

from conferencia_de_molde import le_conferido
from erro_de_dados import ErroDeDados
from leitura_de_texto import CODIFICACAO, QUEBRAS_COMO_ESTAO, le_texto
from repetidos import repetidos

MOLDE = Path(__file__).resolve().parent / "esquemas" / "copias-estragadas.schema.json"  # o molde da lista de estragos
ILEGIVEL = "replace"  # o que o teste escreveu fora da codificação se troca por um sinal, em vez de dar erro
SOBE = ".."  # a parte de um caminho que sobe para a pasta de cima
SEM_ESTRAGO = "sem-estrago"  # na pasta de trabalho, a pasta da rodada da cópia sem estrago
ESTRAGOS = "estragos"  # na pasta de trabalho, a pasta que guarda a da rodada de cada estrago, com o nome dele
COPIA = "copia"  # na pasta de uma rodada, a pasta que guarda a cópia, com o nome da peça testada
GRAVACAO = "gravacao"  # na pasta de uma rodada, a pasta vazia que o teste recebe para o que ele gravar
SAIDA = "saida.txt"  # na pasta de uma rodada, o que o teste escreveu na saída padrão
ERRO = "erro.txt"  # na pasta de uma rodada, o que o teste escreveu na saída de erro
PASSOU = 0  # o código de saída do teste que passou
FALHOU = 1  # o código de saída do teste que falhou, por achar um erro
ESCAPOU = "escapou"  # o resultado do estrago cujo teste passou
PEGO = "pego"  # o resultado do estrago cujo teste falhou
QUEBROU = "quebrou"  # o resultado do estrago cujo teste saiu com outro código
CORTADO = "cortado"  # o resultado do estrago cujo teste passou do limite de tempo


def _troca(peca, estrago):
    """(partes, texto) da troca de um estrago: as partes do caminho do arquivo dele, contadas da pasta da peça
    testada, e o texto do arquivo com o trecho trocado. Erro (ErroDeDados), com o motivo, quando o arquivo não é um
    arquivo de dentro da peça, é um atalho, fica dentro de uma pasta que é atalho ou não se lê como texto, e quando
    o trecho que sai é igual ao que entra, não aparece no arquivo ou aparece mais de uma vez."""
    caminho = PurePosixPath(estrago["arquivo"])
    arquivo = peca.joinpath(*caminho.parts)
    if caminho.is_absolute() or SOBE in caminho.parts or peca not in arquivo.parents:
        raise ErroDeDados(f"{estrago['arquivo']!r} não é um arquivo de dentro da peça testada")
    if any(item.is_symlink() for item in (arquivo, *arquivo.parents) if peca in item.parents):
        raise ErroDeDados(f"{estrago['arquivo']!r} é um atalho ou fica dentro de uma pasta que é atalho")
    if not arquivo.is_file():
        raise ErroDeDados(f"{estrago['arquivo']!r} não é um arquivo de dentro da peça testada")
    texto, sai, entra = le_texto(arquivo, exato=True), estrago["de"], estrago["para"]
    if entra == sai:
        raise ErroDeDados("o trecho que entra é igual ao que sai")
    lugar = texto.find(sai)
    if lugar < 0:
        raise ErroDeDados(f"o trecho que sai não aparece em {estrago['arquivo']!r}")
    if texto.find(sai, lugar + 1) >= 0:
        raise ErroDeDados(f"o trecho que sai aparece mais de uma vez em {estrago['arquivo']!r}")
    return caminho.parts, texto[:lugar] + entra + texto[lugar + len(sai):]


def _trocas(peca, lista, origem):
    """A troca (_troca) de cada estrago da lista, na ordem dela. Erro (ErroDeDados) que diz a origem da lista e,
    de cada estrago que não se pode fazer, o nome e o motivo."""
    trocas, erros = [], []
    for estrago in lista:
        try:
            trocas.append(_troca(peca, estrago))
        except ErroDeDados as erro:
            erros.append(f"{estrago['nome']}: {erro}")
    if erros:
        raise ErroDeDados(f"{origem}: {'; '.join(erros)}")
    return trocas


def _escolhidos(lista, so):
    """Os nomes dos estragos da lista que batem com alguma das escolhas (campo, valor); os de todos, sem escolha
    nenhuma. Erro (ErroDeDados) na escolha de um campo que os estragos não têm ou que não bate com nenhum deles."""
    for campo, valor in so:
        if any(campo not in estrago for estrago in lista):
            raise ErroDeDados(f"a escolha pelo campo {campo!r}: os estragos não têm esse campo")
        if all(estrago[campo] != valor for estrago in lista):
            raise ErroDeDados(f"a escolha de {campo!r} igual a {valor!r} não bate com nenhum estrago")
    return {estrago["nome"] for estrago in lista
            if not so or any(estrago[campo] == valor for campo, valor in so)}


def _corta(processo):
    """Mata o comando e tudo o que ele pôs para rodar, e espera o fim dele. O comando roda num grupo só dele, e é
    o grupo inteiro que morre; no sistema que não tem grupos, morre só o comando."""
    if hasattr(os, "killpg"):
        try:
            os.killpg(processo.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        processo.kill()
    processo.wait()


def _roda(comando, pasta, limite):
    """O código de saída do comando, que roda sem entrada, com a saída padrão e a de erro gravadas na pasta da
    rodada; None quando ele passa do limite de tempo, em segundos, e é cortado. Erro (ErroDeDados) quando o
    comando não roda."""
    with open(pasta / SAIDA, "wb") as saida, open(pasta / ERRO, "wb") as erro:
        try:
            processo = subprocess.Popen(comando, stdin=subprocess.DEVNULL, stdout=saida, stderr=erro,
                                        start_new_session=True)
        except OSError as motivo:
            raise ErroDeDados(f"o comando do teste não roda: {comando[0]!r} ({motivo})") from None
        try:
            return processo.wait(timeout=limite)
        except subprocess.TimeoutExpired:
            return None
        finally:
            if processo.returncode is None:
                _corta(processo)


def _ultima_linha(pasta):
    """A última linha com algo escrito do que o teste escreveu na saída de erro ou, sem nada nela, na saída
    padrão; "" quando ele não escreveu nada."""
    for nome in (ERRO, SAIDA):
        escrito = (pasta / nome).read_bytes().decode(CODIFICACAO, ILEGIVEL)
        linhas = [linha for linha in escrito.splitlines() if linha.strip()]
        if linhas:
            return linhas[-1]
    return ""


def _rodada(peca, comando, pasta, limite, troca=None):
    """(código de saída, última linha) do teste que roda contra uma cópia da peça testada, feita na pasta da
    rodada, com a troca (partes do arquivo, texto dele) quando ela vem; o código é None quando o teste é
    cortado."""
    copia, gravacao = pasta / COPIA / peca.name, pasta / GRAVACAO
    shutil.copytree(peca, copia, symlinks=True)
    gravacao.mkdir()
    if troca is not None:
        partes, texto = troca
        with open(copia.joinpath(*partes), "w", encoding=CODIFICACAO, newline=QUEBRAS_COMO_ESTAO) as arquivo:
            arquivo.write(texto)
    return _roda([*comando, str(copia), str(gravacao)], pasta, limite), _ultima_linha(pasta)


def _resultado(codigo):
    """O resultado de um estrago, pelo código de saída do teste que rodou contra a cópia dele (None, o do teste
    cortado)."""
    if codigo is None:
        return CORTADO
    return {PASSOU: ESCAPOU, FALHOU: PEGO}.get(codigo, QUEBROU)


def prova(peca, comando, estragos, trabalho, limite, so=()):
    """[(nome, resultado, última linha)] de cada estrago que rodou, na ordem da lista: o resultado é "pego",
    "escapou", "quebrou" ou "cortado", e a última linha é a que o teste escreveu. Recebe a pasta da peça testada,
    as palavras do comando do teste, o arquivo da lista de estragos, a pasta de trabalho, o limite de tempo de cada
    rodada, em segundos, e, em so, as escolhas (campo, valor) dos estragos que rodam; sem escolha, rodam todos.
    Erro (ErroDeDados) no que impede a prova, conferido antes da primeira cópia, e no teste que não passa na cópia
    sem estrago."""
    peca, trabalho, comando, so = Path(peca).resolve(), Path(trabalho).resolve(), list(comando), list(so)
    if not peca.is_dir():
        raise ErroDeDados(f"{peca}: a peça testada não é uma pasta")
    lista = le_conferido(estragos, MOLDE)["estragos"]
    iguais = repetidos([estrago["nome"] for estrago in lista])
    if iguais:
        raise ErroDeDados(f"{estragos}: estragos com o mesmo nome: {iguais}")
    trocas = _trocas(peca, lista, estragos)
    escolhidos = _escolhidos(lista, so)
    if isinstance(limite, bool) or not isinstance(limite, (int, float)) or not math.isfinite(limite) or limite <= 0:
        raise ErroDeDados(f"o limite de tempo não é um número maior que zero: {limite!r}")
    if not comando:
        raise ErroDeDados("o comando do teste não tem nenhuma palavra")
    if trabalho == peca or peca in trabalho.parents:
        raise ErroDeDados(f"{trabalho}: a pasta de trabalho fica dentro da peça testada")
    if trabalho.exists() and (not trabalho.is_dir() or any(trabalho.iterdir())):
        raise ErroDeDados(f"{trabalho}: a pasta de trabalho não está vazia")
    trabalho.mkdir(parents=True, exist_ok=True)
    codigo, linha = _rodada(peca, comando, trabalho / SEM_ESTRAGO, limite)
    if codigo != PASSOU:
        fim = f"passou do limite de {limite} segundo(s)" if codigo is None else f"saiu com o código {codigo}"
        raise ErroDeDados(f"{peca}: o teste não passa na cópia sem estrago: {fim}; a última linha dele: {linha!r}")
    resultados = []
    for estrago, troca in zip(lista, trocas):
        if estrago["nome"] in escolhidos:
            codigo, linha = _rodada(peca, comando, trabalho / ESTRAGOS / estrago["nome"], limite, troca)
            resultados.append((estrago["nome"], _resultado(codigo), linha))
    return resultados
