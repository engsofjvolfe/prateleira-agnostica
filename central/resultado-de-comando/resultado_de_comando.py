"""
Roda um comando e diz como ele acabou, pelo código de saída: 0, passou; 1, não passou; outro,
quebrou.

Dá às peças: resultado, que roda o comando e devolve um Resultado, e os nomes de como um
comando acaba: PASSOU, NAO_PASSOU e QUEBROU.

Todo erro é um ErroDeDados.
"""
import subprocess
from collections import namedtuple

from erro_de_dados import ErroDeDados
from leitura_de_texto import CODIFICACAO

PASSOU = "passou"  # o comando saiu com 0
NAO_PASSOU = "nao_passou"  # o comando saiu com 1
QUEBROU = "quebrou"  # o comando saiu com outro código
FINS = {0: PASSOU, 1: NAO_PASSOU}  # o fim de cada código de saída; o código que não está aqui é o de QUEBROU
ILEGIVEL = "replace"  # o que vira o que o comando escreveu e não se lê em CODIFICACAO: um sinal de troca
SOLTO = True  # o comando roda solto do terminal: o que para para perguntar algo falha na hora

# Como o comando acabou: o fim (PASSOU, NAO_PASSOU ou QUEBROU), o código de saída e o que ele escreveu na saída
# padrão e na saída de erro.
Resultado = namedtuple("Resultado", "fim codigo saida erro")


def resultado(comando, pasta):
    """Como o comando, a lista das palavras dele, acabou, rodando a partir da pasta, sem nada pela entrada padrão e
    solto do terminal. Erro (ErroDeDados) quando o comando não tem nenhuma palavra e quando ele não roda."""
    if not comando:
        raise ErroDeDados("comando sem nenhuma palavra")
    try:
        rodado = subprocess.run(list(comando), cwd=pasta, stdin=subprocess.DEVNULL, capture_output=True,
                                encoding=CODIFICACAO, errors=ILEGIVEL, check=False, start_new_session=SOLTO)
    except OSError as erro:
        raise ErroDeDados(f"{list(comando)}: não roda: {erro}") from None
    return Resultado(FINS.get(rodado.returncode, QUEBROU), rodado.returncode, rodado.stdout, rodado.stderr)
