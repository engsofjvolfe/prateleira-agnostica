"""
Roda o código de uma peça com as peças da central à mão.

O comando chama este arquivo com o arquivo de código da peça e, depois dele, as opções da
peça. As peças da central são as pastas vizinhas da pasta deste arquivo: de cada uma vale o
arquivo de código com o nome da pasta, com "_" no lugar de "-". Dali em diante, o código da
peça pede cada uma pelo nome, como pede o que já vem com o Python.

Dá erro, e não roda nada, quando falta o arquivo de código da peça, quando ele não é um
arquivo e quando uma peça da central tem o nome de algo que já vem com o Python.
"""
import importlib.abc
import importlib.util
import runpy
import sys
from pathlib import Path

CENTRAL = Path(__file__).resolve().parent.parent  # a pasta da central: a que guarda a pasta deste arquivo
SEPARADOR_DA_PASTA = "-"  # o que separa as palavras no nome de uma pasta
SEPARADOR_DO_CODIGO = "_"  # o que separa as palavras no nome de um arquivo de código
EXTENSAO = ".py"  # o fim do nome de um arquivo de código
PRINCIPAL = "__main__"  # o nome que o Python dá ao código que o comando roda


class _Central(importlib.abc.MetaPathFinder):
    """Diz ao Python, pelo nome, onde está o código de cada peça da central."""

    def __init__(self, codigos):
        self.codigos = codigos

    def find_spec(self, nome, caminho=None, alvo=None):
        if nome not in self.codigos:
            return None
        return importlib.util.spec_from_file_location(nome, self.codigos[nome])


def codigos_da_central(central):
    """{nome: arquivo} do código de cada peça da central, em ordem: em cada pasta dela, o arquivo com o nome da
    pasta, com "_" no lugar de "-"; a pasta sem esse arquivo fica de fora."""
    codigos = {}
    for pasta in sorted(item for item in central.iterdir() if item.is_dir()):
        nome = pasta.name.replace(SEPARADOR_DA_PASTA, SEPARADOR_DO_CODIGO)
        arquivo = pasta / (nome + EXTENSAO)
        if arquivo.is_file():
            codigos[nome] = arquivo
    return codigos


def main():
    if len(sys.argv) < 2:
        raise SystemExit(f"uso: {Path(sys.argv[0]).name} <arquivo de código da peça> <opções da peça>")
    codigo = Path(sys.argv[1])
    if not codigo.is_file():
        raise SystemExit(f"{codigo}: não é um arquivo de código")
    codigos = codigos_da_central(CENTRAL)
    do_python = sorted(set(codigos) & sys.stdlib_module_names)
    if do_python:
        raise SystemExit(f"{CENTRAL}: peça com o nome de algo que já vem com o Python: {do_python}")
    sys.meta_path.insert(0, _Central(codigos))
    del sys.argv[0]  # o código da peça recebe as opções como se o comando o chamasse direto
    runpy.run_path(str(codigo), run_name=PRINCIPAL)


if __name__ == PRINCIPAL:
    main()
