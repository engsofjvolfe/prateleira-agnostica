"""
Preenche um modelo: um texto com lugares marcados, cada um com um nome entre chaves.

O lugar é tudo o que está entre uma chave que abre e a chave que fecha, sem outra chave no
meio; o nome dele é o que está entre as duas. A chave sem par fica como está.

Dá às peças: campos e preenche. Todo erro é um ErroDeDados.
"""
import re

from erro_de_dados import ErroDeDados

LUGAR = re.compile(r"\{([^{}]*)\}")  # um lugar do modelo; o grupo é o nome dele


def campos(modelo):
    """Os nomes dos lugares do modelo, na ordem em que aparecem; o que aparece duas vezes vem duas vezes."""
    return LUGAR.findall(modelo)


def preenche(modelo, valores):
    """O modelo com cada lugar trocado pelo valor dele em valores, {nome: valor}; o resto fica como está, e o valor
    posto não se lê de novo como modelo. Erro (ErroDeDados) quando o modelo tem um lugar sem valor."""
    def troca(achado):
        nome = achado.group(1)
        if nome not in valores:
            raise ErroDeDados(f"o modelo {modelo!r} tem o lugar {{{nome}}}, que não tem valor aqui")
        return str(valores[nome])

    return LUGAR.sub(troca, modelo)
