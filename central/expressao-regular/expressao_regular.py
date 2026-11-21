"""
Prepara uma expressão regular para o uso.

A expressão regular é a do Python. A que não é válida dá erro, que diz onde ela está escrita.

Dá às peças: compila. Todo erro é um ErroDeDados.
"""
import re

from erro_de_dados import ErroDeDados


def compila(texto, onde):
    """A expressão regular do texto, pronta para o uso. Erro (ErroDeDados), que diz onde ela está escrita, quando
    ela não é válida."""
    try:
        return re.compile(texto)
    except re.error as erro:
        raise ErroDeDados(f"{onde}: não é uma expressão regular válida ({erro})") from None
