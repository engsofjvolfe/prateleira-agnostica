"""
Lê dados em JSON, de um texto ou de um arquivo.

Além do texto que não é JSON, dá erro o que outro leitor poderia ler de outro jeito: o NaN e
o Infinity, que não são números do JSON; o texto com só metade de um caractere (um
substituto UTF-16 solto), que não se grava em UTF-8; e o objeto com o mesmo nome mais de uma
vez.

Dá às peças: de_json e le_json. Todo erro é um ErroDeDados.
"""
import json

from erro_de_dados import ErroDeDados
from leitura_de_texto import CODIFICACAO, le_texto
from repetidos import repetidos


def _texto_partido(dados):
    """O primeiro texto dos dados, nome ou valor, com só metade de um caractere; None quando não há."""
    pilha = [dados]
    while pilha:
        valor = pilha.pop()
        if isinstance(valor, str):
            try:
                valor.encode(CODIFICACAO)
            except UnicodeEncodeError:
                return valor
        elif isinstance(valor, dict):
            pilha.extend(reversed([parte for par in valor.items() for parte in par]))
        elif isinstance(valor, list):
            pilha.extend(reversed(valor))
    return None


def de_json(texto, origem):
    """Os dados do texto em JSON. Erro (ErroDeDados), que diz a origem do texto, como o arquivo que o traz, quando
    ele não é JSON e quando traz o NaN ou o Infinity, só metade de um caractere ou um objeto com o mesmo nome mais
    de uma vez."""
    def constante(nome):
        raise ErroDeDados(f"{origem}: não se lê como JSON ({nome} não é número do JSON)")

    def objeto(pares):
        mesmos = repetidos([nome for nome, _ in pares])
        if mesmos:
            raise ErroDeDados(f"{origem}: não se lê como JSON (objeto com o mesmo nome mais de uma vez: {mesmos})")
        return dict(pares)

    try:
        dados = json.loads(texto, parse_constant=constante, object_pairs_hook=objeto)
    except json.JSONDecodeError as erro:
        raise ErroDeDados(f"{origem}: não se lê como JSON ({erro})") from None
    except RecursionError:
        raise ErroDeDados(f"{origem}: não se lê como JSON (tem valores demais, um dentro do outro)") from None
    partido = _texto_partido(dados)
    if partido is not None:
        raise ErroDeDados(f"{origem}: não se lê como JSON (o texto {partido!r} tem só metade de um caractere, que "
                          f"não se grava em UTF-8)")
    return dados


def le_json(caminho):
    """Os dados de um arquivo JSON, lido como texto (le_texto) e como JSON (de_json), com o arquivo no erro."""
    return de_json(le_texto(caminho), caminho)
