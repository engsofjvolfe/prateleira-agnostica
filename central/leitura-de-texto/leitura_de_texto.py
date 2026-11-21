"""
Lê um arquivo de texto.

O arquivo se lê em UTF-8. O arquivo que não existe ou não se lê dá erro, que diz qual é.

Dá às peças: le_texto, CODIFICACAO e QUEBRAS_COMO_ESTAO. Todo erro é um ErroDeDados.
"""
from erro_de_dados import ErroDeDados

CODIFICACAO = "utf-8"  # a forma em que o texto está gravado no arquivo
QUEBRAS_TROCADAS = None  # o jeito de abrir o arquivo que entrega toda quebra de linha como "\n"
QUEBRAS_COMO_ESTAO = ""  # o jeito de abrir o arquivo que não mexe nas quebras de linha, nem ao ler nem ao gravar


def le_texto(caminho, exato=False):
    """O texto do arquivo. Cada quebra de linha "\\r\\n" ou "\\r" vem como "\\n"; com exato, as quebras vêm como
    estão no arquivo, para o texto que se grava de volta nele, igual. Erro (ErroDeDados), que diz o arquivo, quando
    ele não existe ou não se lê em UTF-8."""
    quebras = QUEBRAS_COMO_ESTAO if exato else QUEBRAS_TROCADAS
    try:
        with open(caminho, encoding=CODIFICACAO, newline=quebras) as arquivo:
            return arquivo.read()
    except (OSError, UnicodeDecodeError) as erro:
        raise ErroDeDados(f"{caminho}: não se lê como texto em UTF-8 ({erro})") from None
