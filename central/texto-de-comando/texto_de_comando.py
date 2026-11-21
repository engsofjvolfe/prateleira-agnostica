"""
Roda um comando e entrega, como texto, o que ele escreveu na saída padrão: lido em UTF-8, como
na leitura de texto, com cada quebra de linha como "\\n". O comando roda solto do terminal,
sem nada pela entrada padrão, para o que para para perguntar algo falhar na hora.

Dá às peças: texto_do_comando. Todo erro é um ErroDeDados.
"""
import io
import subprocess

from erro_de_dados import ErroDeDados
from leitura_de_texto import CODIFICACAO

PASSOU = 0  # o código de saída do comando que passou
SOLTO = True  # o comando roda solto do terminal


def texto_do_comando(comando, pasta):
    """O que o comando, a lista das palavras dele, escreveu na saída padrão, rodando a partir da pasta, lido em
    UTF-8 com cada quebra de linha como "\\n", quando ele acaba com o código de saída 0; None quando acaba com outro.
    Erro (ErroDeDados), que diz o comando, quando ele não tem nenhuma palavra, quando não roda e quando o que
    escreveu não se lê em UTF-8."""
    if not comando:
        raise ErroDeDados("comando sem nenhuma palavra")
    try:
        rodado = subprocess.run(list(comando), cwd=pasta, stdin=subprocess.DEVNULL, capture_output=True, check=False,
                                start_new_session=SOLTO)
    except OSError as erro:
        raise ErroDeDados(f"{list(comando)}: não roda: {erro}") from None
    if rodado.returncode != PASSOU:
        return None
    try:
        return io.TextIOWrapper(io.BytesIO(rodado.stdout), encoding=CODIFICACAO).read()
    except UnicodeDecodeError as erro:
        raise ErroDeDados(f"{list(comando)}: o que escreveu não se lê como texto em UTF-8 ({erro})") from None
