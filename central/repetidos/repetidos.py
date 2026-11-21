"""
Acha os valores repetidos de uma lista.

Dá às peças: repetidos.
"""
from collections import Counter


def repetidos(valores):
    """Os valores que aparecem mais de uma vez na lista, cada um uma vez só, em ordem; uma lista vazia quando nada
    se repete."""
    return sorted(valor for valor, vezes in Counter(valores).items() if vezes > 1)
