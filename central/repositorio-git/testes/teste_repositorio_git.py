"""
Testa o repositorio-git da pasta recebida: monta pastas sorteadas, com letras de fora do ASCII, com e sem um ".git"
acima delas, e confere, pela regra do README dele, o que ele responde.

Uso:
    python3 -I <central>/roda/roda.py teste_repositorio_git.py <pasta da peça> <pasta de gravação>

A pasta de gravação fica fora de um repositório git. O teste sai com 0 quando tudo confere, 1 quando acha um erro e 2
quando o próprio teste quebra.
"""
import os
import random
import sys
import traceback
import types
from pathlib import Path

SEMENTE = 20261120  # a semente de todos os sorteios
SORTEIOS = 8  # quantas árvores de pastas se sorteiam
CODIGO = "repositorio_git.py"  # o arquivo de código da peça, dentro da pasta dela
PASSOU, FALHOU, QUEBROU = 0, 1, 2  # os códigos de saída do teste
LETRAS = "abcçdeéfghiíjklmnoópqrstuúvwxyzãõâêôàüñ "  # as letras dos nomes sorteados
GIT = ".git"


def carrega(pasta):
    """O código da peça testada, lido do arquivo da pasta recebida, e nunca do código que o Python já preparou e
    guardou: o estrago que não muda o tamanho do arquivo passaria despercebido."""
    arquivo = pasta / CODIGO
    modulo = types.ModuleType("repositorio_git_testado")
    modulo.__file__ = str(arquivo)
    sys.modules[modulo.__name__] = modulo
    exec(compile(arquivo.read_text(encoding="utf-8"), str(arquivo), "exec"), modulo.__dict__)
    return modulo


def nome(sorte):
    return "".join(sorte.choice(LETRAS) for _ in range(sorte.randint(2, 8))).strip() + sorte.choice("çãé")


class Conferencia:
    def __init__(self, modulo):
        self.modulo, self.falhas = modulo, []

    def responde(self, caso, pasta, esperado):
        try:
            resposta = self.modulo.no_repositorio(pasta)
        except Exception:  # a peça quebrou: isso é um erro que o teste acha
            resposta = traceback.format_exc()
        if resposta is not esperado:
            self.falhas.append(f"{caso}: devia dar {esperado}, e deu {resposta!r}")


def main():
    peca, gravacao = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    if any((pasta / GIT).exists() for pasta in (gravacao, *gravacao.parents)):
        raise RuntimeError(f"{gravacao}: a pasta de gravação fica dentro de um repositório git")
    conferencia, sorte = Conferencia(carrega(peca)), random.Random(SEMENTE)
    for numero in range(SORTEIOS):
        raiz = gravacao / f"{numero}-{nome(sorte)}"
        pastas = [raiz]
        for _ in range(sorte.randint(2, 5)):
            pastas.append(pastas[-1] / nome(sorte))
        pastas[-1].mkdir(parents=True)
        conferencia.responde(f"árvore {numero} sem .git", pastas[-1], False)
        nivel = sorte.randrange(len(pastas))
        if numero % 2 == 0:
            (pastas[nivel] / GIT).mkdir()
            jeito = "pasta"
        else:
            (pastas[nivel] / GIT).write_text(f"gitdir: {nome(sorte)}", encoding="utf-8")
            jeito = "arquivo"
        for indice, pasta in enumerate(pastas):
            conferencia.responde(f"árvore {numero}, .git {jeito} no nível {nivel}, pasta {indice}", pasta,
                                 indice >= nivel)
        de_cima = Path(os.path.relpath(pastas[-1], Path.cwd()))
        conferencia.responde(f"árvore {numero}, caminho que conta da pasta do comando", de_cima, True)
        fora = gravacao / f"{numero}-fora-{nome(sorte)}"
        fora.mkdir()
        atalho = fora / nome(sorte)
        atalho.symlink_to(pastas[-1], target_is_directory=True)
        conferencia.responde(f"árvore {numero}, atalho para dentro do repositório", atalho, True)
        acima = pastas[nivel].parent / nome(sorte)
        acima.mkdir()
        conferencia.responde(f"árvore {numero}, caminho que volta para cima do .git",
                             pastas[nivel] / ".." / acima.name, False)
    for falha in conferencia.falhas:
        print(falha)
    print(f"{len(conferencia.falhas)} falha(s)")
    return FALHOU if conferencia.falhas else PASSOU


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # o próprio teste quebrou: não é um erro achado na peça
        traceback.print_exc()
        sys.exit(QUEBROU)
