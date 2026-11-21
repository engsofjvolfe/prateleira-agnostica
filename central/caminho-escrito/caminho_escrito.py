"""
O caminho que um arquivo de dados escreve, inteiro.

Um arquivo de dados, como a configuração de uma peça, pode escrever caminhos. O caminho que não começa no início do
disco conta a partir da pasta do arquivo que o escreve. Assim, ele não depende da pasta de onde o comando roda.

Dá às peças: caminho_escrito.
"""
import os


def caminho_escrito(arquivo, escrito):
    """O caminho que o arquivo de dados escreve, inteiro e sem "." nem "..": o que já começa no início do disco fica
    como está; o que não começa conta a partir da pasta do arquivo."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(arquivo)), escrito))
