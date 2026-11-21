"""
Faz as tentativas da conferencia-de-protecao com o usuário com que roda e escreve os achados em JSON na saída
padrão: a lista dos pares [caminho, tipo], com o caminho vazio (null) no que não é de um arquivo.

Só o desprotegidos o roda, com o usuário da IA, pelo pedido de outro usuário, e pelo roda.py da central. A única
opção é o pedido, em JSON: os caminhos e as palavras do pedido de administrador.

Sai com 0 quando escreveu os achados e com 2 quando a opção não tem a forma combinada.
"""
import json
import sys

from conferencia_de_protecao import CAMINHOS, PEDIDO, achados_daqui
from erro_de_dados import ErroDeDados
from leitura_de_json import de_json

ESCREVEU = 0  # o código de saída de quando os achados foram escritos
FORA_DA_FORMA = 2  # o código de saída de quando a opção não tem a forma combinada
ORIGEM = "a opção do tentativas.py"  # de onde vem o texto que o de_json lê, para a mensagem do erro


def _textos(valor):
    """Se o valor é uma lista de textos."""
    return isinstance(valor, list) and all(isinstance(item, str) for item in valor)


def _pedido(opcoes):
    """(caminhos, pedido de administrador) da única opção, ou None quando ela não tem a forma combinada."""
    if len(opcoes) != 1:
        return None
    try:
        dados = de_json(opcoes[0], ORIGEM)
    except ErroDeDados:
        return None
    if not isinstance(dados, dict) or set(dados) != {CAMINHOS, PEDIDO}:
        return None
    if not (_textos(dados[CAMINHOS]) and _textos(dados[PEDIDO])):
        return None
    return dados[CAMINHOS], dados[PEDIDO]


def principal(opcoes):
    """Faz as tentativas do pedido e escreve os achados; devolve o código de saída."""
    pedido = _pedido(opcoes)
    if pedido is None:
        return FORA_DA_FORMA
    achados = achados_daqui(*pedido)
    sys.stdout.write(json.dumps([list(achado) for achado in achados], ensure_ascii=False))
    return ESCREVEU


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
