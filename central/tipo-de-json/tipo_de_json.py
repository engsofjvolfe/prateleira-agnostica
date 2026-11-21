"""
Diz se um valor é de um tipo do JSON.

Dá às peças: TIPOS e do_tipo.
"""
from erro_de_dados import ErroDeDados

# o nome de cada tipo do JSON e o que ele é no Python; o sim e o não ficam só no "boolean", e o número inteiro
# também é um "number"
TIPOS = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool,
         "null": type(None)}


def do_tipo(valor, tipo):
    """Se o valor é do tipo de nome dado, um dos de TIPOS. O sim e o não só são do "boolean", porque o Python os
    conta como números e o JSON não. O nome que não é de nenhum tipo dá erro (ErroDeDados)."""
    if tipo not in TIPOS:
        raise ErroDeDados(f"tipo desconhecido: {tipo!r}")
    return isinstance(valor, TIPOS[tipo]) and (tipo == "boolean" or not isinstance(valor, bool))
