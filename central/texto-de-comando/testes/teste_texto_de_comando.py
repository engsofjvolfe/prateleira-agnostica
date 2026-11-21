"""
Testa o texto-de-comando da pasta recebida: roda comandos que escrevem textos sorteados, com letras de fora do ASCII,
e confere, pela regra do README dele, o que ele entrega e quando dá erro.

Uso:
    python3 -I <central>/roda/roda.py teste_texto_de_comando.py <pasta da peça> <pasta de gravação>

Sai com 0 quando tudo confere, 1 quando acha um erro e 2 quando o próprio teste quebra.
"""
import importlib.util
import os
import random
import sys
import traceback
from pathlib import Path

from erro_de_dados import ErroDeDados

SEMENTE = 20261118  # a semente de todos os sorteios
SORTEIOS = 12  # quantos textos se sorteiam
CODIGO = "texto_de_comando.py"  # o arquivo de código da peça, dentro da pasta dela
PASSOU, FALHOU, QUEBROU = 0, 1, 2  # os códigos de saída do teste
LETRAS = "abcçdeéfghiíjklmnoópqrstuúvwxyzãõâêôàüñ "  # as letras dos textos sorteados, com as de fora do ASCII
QUEBRAS = ("\n", "\r\n", "\r")  # os jeitos de escrever a quebra de linha
NAO_SE_LE = b"\xff\xfe\xc3"  # bytes que não se leem em UTF-8


def carrega(pasta):
    """O código da peça testada, carregado da pasta recebida."""
    especificacao = importlib.util.spec_from_file_location("texto_de_comando_testado", pasta / CODIGO)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def python(*linhas):
    """O comando que roda as linhas de Python, com o mesmo Python do teste."""
    return [sys.executable, "-I", "-c", "\n".join(linhas)]


def escreve(dados, codigo=0):
    """O comando que escreve os bytes na saída padrão e acaba com o código."""
    return python("import sys", f"sys.stdout.buffer.write(bytes.fromhex({dados.hex()!r}))", f"sys.exit({codigo})")


class Conferencia:
    def __init__(self, modulo):
        self.modulo, self.falhas = modulo, []

    def pede(self, comando, pasta):
        """(o que a peça entregou, o erro dela ou None, a exceção que não é o erro da peça ou None)."""
        try:
            return self.modulo.texto_do_comando(comando, pasta), None, None
        except ErroDeDados as erro:
            return None, erro, None
        except Exception:  # a peça quebrou com outro erro: isso é um erro que o teste acha
            return None, None, traceback.format_exc()

    def entrega(self, caso, comando, pasta, esperado):
        texto, erro, outro = self.pede(comando, pasta)
        if erro is not None or outro is not None or texto != esperado:
            self.falhas.append(f"{caso}: devia entregar {esperado!r}, e veio {texto!r} ({erro or outro})")

    def da_erro(self, caso, comando, pasta, palavra=None):
        """A peça tem de dar o erro dela; com a palavra, a mensagem tem de trazê-la."""
        texto, erro, outro = self.pede(comando, pasta)
        if erro is None or (palavra is not None and palavra not in str(erro)):
            self.falhas.append(f"{caso}: devia dar erro, e veio {texto!r} ({outro})")


def com_entrada(dados, pedido):
    """Roda o pedido com a entrada padrão do teste trocada por uma que tem os dados, e a devolve depois."""
    leitura, escrita = os.pipe()
    os.write(escrita, dados)
    os.close(escrita)
    guardada = os.dup(0)
    os.dup2(leitura, 0)
    try:
        return pedido()
    finally:
        os.dup2(guardada, 0)
        os.close(guardada)
        os.close(leitura)


def main():
    pasta, gravacao = Path(sys.argv[1]), Path(sys.argv[2])
    conferencia, sorte = Conferencia(carrega(pasta)), random.Random(SEMENTE)
    for numero in range(SORTEIOS):
        linhas = ["".join(sorte.choice(LETRAS) for _ in range(sorte.randint(1, 20))) for _ in range(sorte.randint(1, 4))]
        quebras = [sorte.choice(QUEBRAS) for _ in linhas]
        escrito = "".join(linha + quebra for linha, quebra in zip(linhas, quebras))
        conferencia.entrega(f"texto {numero}", escreve(escrito.encode("utf-8")), gravacao, "\n".join(linhas) + "\n")
        codigo = sorte.randint(1, 9)
        conferencia.entrega(f"código {codigo}", escreve(escrito.encode("utf-8"), codigo), gravacao, None)
    conferencia.da_erro("o que não se lê em UTF-8", escreve(NAO_SE_LE), gravacao, sys.executable)
    conferencia.da_erro("comando sem nenhuma palavra", [], gravacao)
    conferencia.da_erro("programa que não existe", [str(gravacao / "não-existe-ç")], gravacao)
    pasta_de_rodar = gravacao / "pasta-ç"
    pasta_de_rodar.mkdir()
    conferencia.entrega("roda a partir da pasta", python("import os", "print(os.getcwd())"), pasta_de_rodar,
                        f"{pasta_de_rodar}\n")
    leitura = python("import sys", "print(len(sys.stdin.read()))")
    texto = com_entrada("ç".encode("utf-8") * sorte.randint(1, 9), lambda: conferencia.pede(leitura, gravacao))
    if texto != ("0\n", None, None):
        conferencia.falhas.append(f"sem nada pela entrada padrão: devia ler 0, e veio {texto!r}")
    conferencia.entrega("solto do terminal", python("import os", "print(os.getsid(0) == os.getpid())"), gravacao,
                        "True\n")
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
