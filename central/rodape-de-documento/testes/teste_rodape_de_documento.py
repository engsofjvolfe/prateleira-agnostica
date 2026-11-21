"""
Testa o rodape-de-documento da pasta recebida: monta projetos sorteados, com letras de fora do ASCII, e confere, pela
regra do README dele, o que cada pedido entrega e quando dá erro.

Uso:
    python3 -I <central>/roda/roda.py teste_rodape_de_documento.py <pasta da peça> <pasta de gravação>

A pasta de gravação fica fora de um repositório git. O teste sai com 0 quando tudo confere, 1 quando acha um erro e 2
quando o próprio teste quebra. A pasta de cada caso que passa se apaga; fica só a do caso que falha.
"""
import copy
import datetime
import json
import os
import random
import re
import shutil
import subprocess
import sys
import traceback
import types
from pathlib import Path

from erro_de_dados import ErroDeDados

SEMENTE = 20261120  # a semente de todos os sorteios
PROJETOS = 6  # quantos projetos se sorteiam para a montagem
CODIGO = "rodape_de_documento.py"  # o arquivo de código da peça, dentro da pasta dela
PASSOU, FALHOU, QUEBROU = 0, 1, 2  # os códigos de saída do teste
LETRAS = "abcçdeéfghiíjklmnoópqrstuúvwxyzãõâêôàüñ"  # as letras dos nomes e dos textos sorteados
PARES = (("{{", "}}"), ("«", "»"), ("<%", "%>"), ("⟦", "⟧"))  # os textos que abrem e fecham um campo
SEPARADORES = ("\n", "\n\n", "\n \n", " \n\n")
QUEBRAS = ("\n", "\r\n", "\r")
QUEBRA = re.compile(r"\r\n|\r|\n")
FORMATOS = ("%d/%m/%Y", "%Y-%m-%d", "%Y·%m·%d %z")
FORMATO_COM_HORA = "%Y-%m-%d %H:%M %z"
MARCA = "<!-- ŕodapé -->"
LINK = r"\[[^\]\n]*\]\((?P<alvo>[^)\s]*)\)"  # um link escrito [texto](alvo), sem espaços no alvo
SEM_LINK = r"`[^`\n]*`"
SECAO, FIM_DA_PARTE, ESCOLHA = "§ ", "¶ ", "@ rodapé: "  # o começo das linhas de seção, de fim e de escolha
LINHA_DE_SECAO, LINHA_DE_FIM, LINHA_DE_ESCOLHA = "^§ ", "^¶ ", r"^@ rodapé: (?P<nome>\S+)$"
LUGAR_SECAO, LUGAR_FIM = "secao", "fim"
LUGARES = (LUGAR_SECAO, LUGAR_FIM)
FALTA, DIFERENTE, SOBRA = "falta", "diferente", "sobra"
CAMPOS_DA_PECA = ("caminho", "nome", "mudanca", "hoje")
FUSOS = ("+05:30", "-03:00", "+00:00", "+09:45", "-08:00")


def carrega(pasta):
    """O código da peça testada, lido do arquivo da pasta recebida, e nunca do código que o Python já preparou e
    guardou: o estrago que não muda o tamanho do arquivo passaria despercebido."""
    arquivo = pasta / CODIGO
    modulo = types.ModuleType("rodape_de_documento_testado")
    modulo.__file__ = str(arquivo)
    sys.modules[modulo.__name__] = modulo
    exec(compile(arquivo.read_text(encoding="utf-8"), str(arquivo), "exec"), modulo.__dict__)
    return modulo


def palavra(sorte, minimo=2, maximo=7):
    return "".join(sorte.choice(LETRAS) for _ in range(sorte.randint(minimo, maximo)))


def frase(sorte, minimo=1, maximo=5):
    return " ".join(palavra(sorte) for _ in range(sorte.randint(minimo, maximo)))


def escreve(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto.encode("utf-8") if isinstance(texto, str) else texto)


def relativo(destino, pasta):
    return os.path.relpath(destino, pasta).replace(os.sep, "/")


def hoje(formato):
    return datetime.datetime.now().astimezone().strftime(formato)


def quebra_do(texto):
    achada = QUEBRA.search(texto)
    return achada.group() if achada else "\n"


def linha_de(texto, posicao):
    """O número da linha da posição, contado a partir de 1."""
    return len(QUEBRA.findall(texto[:posicao])) + 1


class Conferencia:
    def __init__(self, modulo):
        self.modulo, self.falhas = modulo, []

    def pede(self, nome, *argumentos):
        """(a resposta, o erro da peça ou None, a exceção que não é o erro da peça ou None)."""
        try:
            return getattr(self.modulo, nome)(*argumentos), None, None
        except ErroDeDados as erro:
            return None, erro, None
        except Exception:  # a peça quebrou com outro erro: isso é um erro que o teste acha
            return None, None, traceback.format_exc()

    def falha(self, caso, motivo):
        self.falhas.append(f"{caso}: {motivo}")

    def responde(self, caso, nome, *argumentos):
        """A resposta; quando a peça dá erro, a falha fica anotada e a resposta é None."""
        resposta, erro, outro = self.pede(nome, *argumentos)
        if erro is not None or outro is not None:
            self.falha(caso, f"{nome} não devia dar erro ({erro or outro})")
        return resposta

    def igual(self, caso, esperado, nome, *argumentos):
        resposta, erro, outro = self.pede(nome, *argumentos)
        if erro is not None or outro is not None or resposta != esperado:
            self.falha(caso, f"{nome} devia dar {esperado!r}, e deu {resposta!r} ({erro or outro})")
        return resposta

    def igual_hoje(self, caso, esperado_de, formato, nome, *argumentos):
        """Como igual, com o esperado feito pela data do dia de antes ou de depois do pedido."""
        antes = hoje(formato)
        resposta, erro, outro = self.pede(nome, *argumentos)
        esperados = (esperado_de(antes), esperado_de(hoje(formato)))
        if erro is not None or outro is not None or resposta not in esperados:
            self.falha(caso, f"{nome} devia dar {esperados[0]!r}, e deu {resposta!r} ({erro or outro})")
        return resposta

    def da_erro(self, caso, nome, *argumentos, palavra=None):
        """A peça tem de dar o erro dela; com a palavra, a mensagem tem de trazê-la."""
        resposta, erro, outro = self.pede(nome, *argumentos)
        if erro is None or (palavra is not None and str(palavra) not in str(erro)):
            self.falha(caso, f"{nome} devia dar erro com {str(palavra)!r}, e deu {resposta!r} ({erro or outro})")


# ---------------------------------------------------------------- o projeto sorteado


class Projeto:
    """Um projeto sorteado: a pasta raiz, os arquivos que os links alcançam, os modelos e o arquivo dos rodapés. Cada
    modelo é uma lista de peças, para o teste montar o rodapé esperado pela regra: ("texto", t), ("link", rótulo,
    destino, barra, lugar), ("campo", nome)."""

    def __init__(self, pasta, sorte, marca):
        self.sorte, self.raiz, self.marca = sorte, pasta / palavra(sorte), marca
        self.ext = palavra(sorte, 1, 3)
        self.abre, self.fecha = sorte.choice(PARES)
        self.separador = sorte.choice(SEPARADORES)
        self.formato = sorte.choice(FORMATOS)
        self.tipo, self.nome_fim, self.nome_secao, self.sem_rodape = (palavra(sorte) + str(i) for i in range(4))
        self.dados = self.raiz / palavra(sorte) / palavra(sorte)
        self.arquivo = self.dados / (palavra(sorte) + ".json")
        self.alvo_arquivo = self.raiz / palavra(sorte) / f"{palavra(sorte)}.{palavra(sorte, 1, 3)}"
        self.alvo_pasta = self.raiz / palavra(sorte)
        escreve(self.alvo_arquivo, frase(sorte))
        self.alvo_pasta.mkdir(parents=True, exist_ok=True)
        self.nome_do_valor = palavra(sorte)
        self.valor = f"{frase(sorte)} {self.abre}caminho{self.fecha} [{palavra(sorte)}]({palavra(sorte)})"
        self.fora, self.com_secao = palavra(sorte) + "f", palavra(sorte) + "s"
        pasta_dos_modelos = self.dados / palavra(sorte)
        self.modelos = {LUGAR_FIM: pasta_dos_modelos / (palavra(sorte) + "1.txt"),
                        LUGAR_SECAO: pasta_dos_modelos / (palavra(sorte) + "2.txt")}
        self.pecas = {LUGAR_FIM: self._pecas_do_fim(), LUGAR_SECAO: self._pecas_da_secao()}
        for lugar in LUGARES:
            self.escreve_modelo(lugar, self.pecas[lugar])
        self.config = {
            "versao_schema": 1,
            "tipos": {self.tipo: {"arquivos": [f"**/*.{self.ext}"], "separador": self.separador, "links": [LINK],
                                  "partes_sem_link": [SEM_LINK], "linha_de_secao": LINHA_DE_SECAO,
                                  "linha_de_fim": LINHA_DE_FIM, "linha_de_escolha": LINHA_DE_ESCOLHA}},
            "rodapes": {
                self.nome_fim: {"modelos": {self.tipo: relativo(self.modelos[LUGAR_FIM], self.dados)},
                                "documentos": ["**"], "fora": [f"{self.fora}/**"], "lugar": LUGAR_FIM},
                self.nome_secao: {"modelos": {self.tipo: relativo(self.modelos[LUGAR_SECAO], self.dados)},
                                  "documentos": [f"{self.com_secao}/**"], "lugar": LUGAR_SECAO},
            },
            "campos": {"abre": self.abre, "fecha": self.fecha, "valores": {self.nome_do_valor: self.valor}},
            "formato_da_data": self.formato,
            "sem_rodape": self.sem_rodape,
        }
        if marca is not None:
            self.config["tipos"][self.tipo]["marca"] = marca
        escreve(self.arquivo, json.dumps(self.config, ensure_ascii=False))

    def _pecas_do_fim(self):
        sorte, p = self.sorte, palavra
        fixos = (f"[{p(sorte)}](https://{p(sorte)}.ç/{p(sorte)}) [{p(sorte)}](#{p(sorte)}) "
                 f"[{p(sorte)}](/{p(sorte)}/{p(sorte)}) `[{p(sorte)}]({p(sorte)}/{p(sorte)})`")
        return [("texto", p(sorte) + " "), ("link", p(sorte), self.alvo_arquivo, False, ""),
                ("texto", f" {p(sorte)}\n"), ("link", p(sorte), self.alvo_pasta, True, ""), ("texto", " · "),
                ("link", p(sorte), self.alvo_arquivo, False, "#" + p(sorte)), ("texto", "\n" + fixos + "\n"),
                ("campo", "caminho"), ("texto", " "), ("campo", "nome"), ("texto", " "), ("campo", "hoje"),
                ("texto", " "), ("campo", self.nome_do_valor), ("texto", f" {self.abre}{p(sorte)}")]

    def _pecas_da_secao(self):
        sorte = self.sorte
        return [("link", palavra(sorte), self.alvo_arquivo, False, ""), ("texto", f" · [{palavra(sorte)}](#ç) "),
                ("campo", "nome")]

    def escreve_modelo(self, lugar, pecas):
        pasta = self.modelos[lugar].parent
        texto = ""
        for peca in pecas:
            if peca[0] == "texto":
                texto += peca[1]
            elif peca[0] == "campo":
                texto += self.abre + peca[1] + self.fecha
            else:
                _, rotulo, destino, barra, lugar_no_arquivo = peca
                texto += f"[{rotulo}]({relativo(destino, pasta)}{'/' if barra else ''}{lugar_no_arquivo})"
        escreve(self.modelos[lugar], "\n \n" + texto + " \n\n  ")
        self.pecas[lugar] = pecas

    def montado(self, lugar, caminho, data):
        """O rodapé esperado para o documento, pela regra: cada link com o caminho a partir da pasta do documento e
        cada campo com o valor dele."""
        pasta = os.path.dirname(os.path.join(self.raiz, caminho))
        valores = {"caminho": caminho, "nome": caminho.rsplit("/", 1)[-1], "hoje": data,
                   self.nome_do_valor: self.valor}
        texto = ""
        for peca in self.pecas[lugar]:
            if peca[0] == "texto":
                texto += peca[1]
            elif peca[0] == "campo":
                texto += valores[peca[1]]
            else:
                _, rotulo, destino, barra, lugar_no_arquivo = peca
                caminho_novo = relativo(destino, pasta)
                if barra and not caminho_novo.endswith("/"):
                    caminho_novo += "/"
                texto += f"[{rotulo}]({caminho_novo}{lugar_no_arquivo})"
        return texto

    def com(self, mudanca):
        """Um arquivo dos rodapés novo, na mesma pasta, com a mudança feita numa cópia da configuração."""
        config = copy.deepcopy(self.config)
        mudanca(config)
        arquivo = self.dados / (palavra(self.sorte) + "-ç.json")
        escreve(arquivo, json.dumps(config, ensure_ascii=False))
        return arquivo

    def modelo_novo(self, texto):
        """O caminho, a partir da pasta do arquivo dos rodapés, de um modelo novo com o texto."""
        caminho = self.dados / (palavra(self.sorte) + "-m.txt")
        escreve(caminho, texto)
        return relativo(caminho, self.dados)


class Documento:
    """Um documento sorteado, guardado em partes: o começo, as seções e o que fica depois da linha de fim."""

    def __init__(self, sorte, vazio=False):
        if vazio:
            self.partes, self.cauda, self.quebra, self.final = [[]], [], sorte.choice(QUEBRAS), False
        else:
            comeco = [frase(sorte) for _ in range(sorte.randint(0, 2))]
            secoes = [[SECAO + frase(sorte)] + [frase(sorte) for _ in range(sorte.randint(0, 2))]
                      for _ in range(sorte.randint(0, 3))]
            if not comeco and not secoes:
                comeco = [frase(sorte)]
            self.partes = [comeco] + secoes
            for parte in self.partes:
                if parte and sorte.random() < 0.4:
                    parte += ["  ", ""][:sorte.randint(1, 2)]
            self.cauda = [FIM_DA_PARTE + frase(sorte), frase(sorte)] if sorte.random() < 0.4 else []
            self.quebra, self.final = sorte.choice(QUEBRAS), sorte.random() < 0.7
        self.monta()

    def monta(self):
        linhas = [linha for parte in self.partes for linha in parte] + self.cauda
        contadas, textos = 0, []
        for grupo in self.partes + [self.cauda]:
            texto = ""
            for linha in grupo:
                contadas += 1
                texto += linha + (self.quebra if contadas < len(linhas) or self.final else "")
            textos.append(texto)
        self.textos, self.texto_da_cauda = textos[:-1], textos[-1]
        self.texto = "".join(textos)

    def ultima_linha_com_texto(self, indice):
        antes = sum(len(parte) for parte in self.partes[:indice])
        numeros = [antes + j + 1 for j, linha in enumerate(self.partes[indice]) if linha.strip()]
        return numeros[-1] if numeros else antes + 1


def lugares_da_parte(documento, indice, levados):
    ultima = indice == len(documento.partes) - 1
    return [lugar for lugar in LUGARES if lugar in levados and ((indice > 0) if lugar == LUGAR_SECAO else ultima)]


def esperado(projeto, documento, blocos, achados=None):
    """O documento que a peça deve entregar, pela regra de "Onde o rodapé fica": (o texto, [(lugar, primeira linha,
    última linha)] de cada rodapé posto). Os blocos vêm com "\\n"; achados diz os lugares dos rodapés que o documento
    já tem, para tirá-los."""
    achados = achados or {}
    quebra = quebra_do(documento.texto)
    separador = projeto.separador.replace("\n", quebra)
    saida, trechos, mexeu, ultima = "", [], False, len(documento.partes) - 1
    for indice, texto in enumerate(documento.textos):
        lugares = lugares_da_parte(documento, indice, blocos)
        if not lugares and indice not in achados:
            saida += texto
            continue
        mexeu = True
        feito = texto.rstrip()
        saida += feito
        for lugar in lugares:
            if feito:
                saida += separador
            bloco = ((projeto.marca + "\n") if projeto.marca else "") + blocos[lugar]
            bloco = bloco.replace("\n", quebra)
            primeira = linha_de(saida, len(saida))
            trechos.append((lugar, primeira, primeira + bloco.count(quebra)))
            saida += bloco
            feito += bloco
        if feito:
            saida += separador if indice < ultima or documento.texto_da_cauda else quebra
    saida += documento.texto_da_cauda
    if mexeu and saida and saida[-1] not in "\r\n":
        saida += quebra
    return saida, trechos


# ---------------------------------------------------------------- os casos


def caso_padroes(conf, pasta, sorte):
    """Os padrões, pelo eh_documento: o "*", o "?", o "**" e o caractere que pega a si mesmo."""
    raiz = pasta / palavra(sorte)
    d1, d2, ext, nome = palavra(sorte) + "1", palavra(sorte) + "2", palavra(sorte, 1, 3), palavra(sorte)
    letra = sorte.choice(LETRAS)
    casos = [
        (f"**/*.{ext}", [f"{nome}.{ext}", f"{d1}/{nome}.{ext}", f"{d1}/{d2}/{nome}.{ext}", f".{ext}"],
         [f"{nome}.{ext}ç", f"{d1}/{nome}.x{ext}"]),
        (f"{d1}/*", [f"{d1}/{nome}"], [f"{d1}/{d2}/{nome}", f"{d2}/{nome}", d1]),
        (f"{d1}/**/{nome}", [f"{d1}/{nome}", f"{d1}/{d2}/{nome}", f"{d1}/{d2}/{d1}/{nome}"],
         [nome, f"{d2}/{nome}", f"{d1}/{nome}ç"]),
        (f"{d1}/**", [d1, f"{d1}/{nome}", f"{d1}/{d2}/{nome}"], [f"{d2}/{nome}", f"{d1}ç"]),
        (f"{nome}?{ext}", [f"{nome}{letra}{ext}", f"{nome}.{ext}"], [f"{nome}{ext}", f"{nome}{letra}{letra}{ext}",
                                                                    f"{nome}/{ext}"]),
        (f"{nome}*", [nome, f"{nome}{letra}"], [f"{nome}/{letra}", f"{letra}{nome}"]),
        ("**", [nome, f"{d1}/{d2}/{nome}"], []),
    ]
    for numero, (padrao, pega, nao_pega) in enumerate(casos):
        config = {"versao_schema": 1, "tipos": {"t": {"arquivos": [padrao], "separador": "\n"}}, "rodapes": {}}
        arquivo = raiz / f"{numero}-{palavra(sorte)}" / "r.json"
        escreve(arquivo, json.dumps(config, ensure_ascii=False))
        rodapes = conf.responde(f"padrão {padrao!r}", "le_rodapes", arquivo, raiz)
        if rodapes is None:
            continue
        for caminho in pega:
            conf.igual(f"padrão {padrao!r} pega {caminho!r}", True, "eh_documento", rodapes, caminho)
        for caminho in nao_pega:
            conf.igual(f"padrão {padrao!r} não pega {caminho!r}", False, "eh_documento", rodapes, caminho)
    projeto = Projeto(pasta, sorte, None)
    arquivo = projeto.com(lambda c: c["tipos"][projeto.tipo].__setitem__("arquivos", ["**"]))
    rodapes = conf.responde("tudo segue o tipo", "le_rodapes", arquivo, projeto.raiz)
    if rodapes is not None:
        for caminho in [arquivo, *projeto.modelos.values()]:
            conf.igual(f"{caminho.name} não é documento", False, "eh_documento", rodapes,
                       relativo(caminho, projeto.raiz))
        conf.igual("outro arquivo é documento", True, "eh_documento", rodapes,
                   relativo(projeto.alvo_arquivo, projeto.raiz))
    arquivo = projeto.com(lambda c: c["tipos"].__setitem__(palavra(sorte) + "ç",
                                                           {"arquivos": [f"{d1}/**"], "separador": "\n"}))
    rodapes = conf.responde("dois tipos", "le_rodapes", arquivo, projeto.raiz)
    if rodapes is not None:
        conf.da_erro("dois tipos", "eh_documento", rodapes, f"{d1}/{nome}.{projeto.ext}",
                     palavra=f"{d1}/{nome}.{projeto.ext}")
        conf.igual("um tipo só", True, "eh_documento", rodapes, f"{d2}/{nome}.{projeto.ext}")


def caso_erros_de_leitura(conf, pasta, sorte):
    """Cada erro que o README lista ao ler o arquivo dos rodapés, com o arquivo na mensagem."""
    projeto = Projeto(pasta, sorte, None)
    if conf.responde("o arquivo certo", "le_rodapes", projeto.arquivo, projeto.raiz) is None:
        return
    tipo, fim, secao = projeto.tipo, projeto.nome_fim, projeto.nome_secao
    abre, fecha = projeto.abre, projeto.fecha

    def no_tipo(chave, valor):
        return lambda c: c["tipos"][tipo].__setitem__(chave, valor)

    def modelo(texto, marca=None):
        caminho = projeto.modelo_novo(texto)

        def muda(c):
            c["rodapes"][fim]["modelos"][tipo] = caminho
            if marca is not None:
                c["tipos"][tipo]["marca"] = marca
        return muda
    p = palavra
    casos = [
        ("lugar fora do molde", lambda c: c["rodapes"][fim].__setitem__("lugar", p(sorte))),
        ("separador com texto", no_tipo("separador", "\n" + p(sorte) + "\n")),
        ("separador que não termina numa quebra", no_tipo("separador", "\n ")),
        ("chave a mais", lambda c: c.__setitem__(p(sorte) + "ç", 1)),
        ("padrão repetido em arquivos", lambda c: c["tipos"][tipo]["arquivos"].append(c["tipos"][tipo]["arquivos"][0])),
        ("padrão repetido em documentos", lambda c: c["rodapes"][secao]["documentos"].append(
            c["rodapes"][secao]["documentos"][0])),
        ("padrão repetido em fora", lambda c: c["rodapes"][fim]["fora"].append(c["rodapes"][fim]["fora"][0])),
        ("expressão que não vale", no_tipo("linha_de_secao", "(" + p(sorte))),
        ("link sem o grupo alvo", lambda c: c["tipos"][tipo]["links"].append(r"\[" + p(sorte) + r"\]")),
        ("escolha sem o grupo nome", no_tipo("linha_de_escolha", "^@ (?P<outro>.*)")),
        ("tipo que não está em tipos", lambda c: c["rodapes"][fim]["modelos"].__setitem__(
            p(sorte) + "ç", c["rodapes"][fim]["modelos"][tipo])),
        ("seção sem linha_de_secao", lambda c: c["tipos"][tipo].pop("linha_de_secao")),
        ("sem_rodape com o nome de um rodapé", lambda c: c.__setitem__("sem_rodape", fim)),
        ("valor com o nome de um campo da peça", lambda c: c["campos"]["valores"].__setitem__(
            sorte.choice(CAMPOS_DA_PECA), frase(sorte))),
        ("modelo que falta", lambda c: c["rodapes"][fim]["modelos"].__setitem__(tipo, p(sorte) + "-falta.txt")),
        ("modelo que não se lê em UTF-8", modelo(b"\xff\xfe" + p(sorte).encode("utf-8"))),
        ("modelo vazio", modelo(" \n  \n\t")),
        ("modelo com uma linha igual à marca", modelo(f"{p(sorte)}\n  {MARCA} \n{p(sorte)}", MARCA)),
        ("modelo com linha de escolha", modelo(f"{p(sorte)}\n{ESCOLHA}{p(sorte)}")),
        ("modelo com linha de seção", modelo(f"{p(sorte)}\n{SECAO}{p(sorte)}")),
        ("modelo com linha de fim", modelo(f"{p(sorte)}\n{FIM_DA_PARTE}{p(sorte)}")),
        ("link que não leva a nada", modelo(f"{p(sorte)} [{p(sorte)}]({p(sorte)}-ç/{p(sorte)})")),
        ("links que se cruzam", lambda c: c["tipos"][tipo]["links"].append(r"\((?P<alvo>[^)\s]*)\)")),
        ("campo dentro do alvo", modelo(f"[{p(sorte)}](https://{p(sorte)}/{abre}nome{fecha})")),
        ("campo sem valor", modelo(f"{p(sorte)} {abre}{p(sorte)}ç{fecha}")),
        ("campo de data sem formato", lambda c: c.pop("formato_da_data")),
        ("mudança fora de um repositório git", modelo(f"{p(sorte)} {abre}mudanca{fecha}")),
    ]
    for caso, mudanca in casos:
        arquivo = projeto.com(mudanca)
        conf.da_erro(caso, "le_rodapes", arquivo, projeto.raiz, palavra=arquivo)
    arquivo = projeto.dados / (p(sorte) + "-json.json")
    escreve(arquivo, "{" + p(sorte))
    conf.da_erro("JSON que não se lê", "le_rodapes", arquivo, projeto.raiz, palavra=arquivo)


def documentos_do_projeto(projeto, sorte):
    """(caminho, documento, lugares que ele leva) dos documentos sorteados de um projeto."""
    p = palavra
    return [
        (f"{projeto.com_secao}/{p(sorte)}/{p(sorte)}.{projeto.ext}", Documento(sorte), {LUGAR_SECAO, LUGAR_FIM}),
        (f"{projeto.fora}/{p(sorte)}.{projeto.ext}", Documento(sorte), set()),
        (f"{p(sorte)}.{projeto.ext}", Documento(sorte), {LUGAR_FIM}),
        (f"{p(sorte)}/{p(sorte)}/{p(sorte)}.{projeto.ext}", Documento(sorte, vazio=True), {LUGAR_FIM}),
    ]


def caso_montagem(conf, pasta, sorte):
    """Cada pedido num projeto sorteado: o rodapé montado, o lugar dele, o que falta, o que se separa."""
    projeto = Projeto(pasta, sorte, sorte.choice((None, MARCA)))
    rodapes = conf.responde("ler", "le_rodapes", projeto.arquivo, projeto.raiz)
    if rodapes is None:
        return
    for caminho, documento, levados in documentos_do_projeto(projeto, sorte):
        caso = f"{caminho} ({'com' if projeto.marca else 'sem'} marca, quebra {documento.quebra!r})"
        conf.igual(caso, True, "eh_documento", rodapes, caminho)

        def blocos(data):
            return {lugar: projeto.montado(lugar, caminho, data) for lugar in levados}
        feito = conf.igual_hoje(caso, lambda data: esperado(projeto, documento, blocos(data))[0], projeto.formato,
                                "com_rodapes", rodapes, caminho, documento.texto)
        if feito is None:
            continue
        conf.igual(f"{caso}: de novo", feito, "com_rodapes", rodapes, caminho, feito)
        faltas = [(lugar, documento.ultima_linha_com_texto(indice), FALTA) for indice in range(len(documento.partes))
                  for lugar in lugares_da_parte(documento, indice, levados)]
        conf.igual(f"{caso}: antes", sorted(faltas, key=lambda f: (f[1], LUGARES.index(f[0]))), "problemas", rodapes,
                   caminho, documento.texto)
        conf.igual(f"{caso}: depois", [], "problemas", rodapes, caminho, feito)
        conf.igual_hoje(caso, blocos, projeto.formato, "rodapes_montados", rodapes, caminho, feito)
        achados = {indice for indice in range(len(documento.partes)) if lugares_da_parte(documento, indice, levados)}
        sem_rodapes, _ = esperado(projeto, documento, {}, achados)
        _, trechos = esperado(projeto, documento, blocos(hoje(projeto.formato)))
        conf.igual(f"{caso}: separa", (sem_rodapes, trechos), "separa", rodapes, caminho, feito)


def caso_tirar_e_trocar(conf, pasta, sorte):
    """Com marca, o rodapé que o documento não leva mais sai; sem marca, o rodapé de um modelo que mudou fica, e o novo
    entra depois dele."""
    for marca in (MARCA, None):
        projeto = Projeto(pasta, sorte, marca)
        rodapes = conf.responde("ler", "le_rodapes", projeto.arquivo, projeto.raiz)
        if rodapes is None:
            return
        documento = Documento(sorte)
        documento.cauda = []
        documento.monta()
        caminho = f"{projeto.com_secao}/{palavra(sorte)}.{projeto.ext}"
        feito = conf.responde("pôr", "com_rodapes", rodapes, caminho, documento.texto)
        if feito is None:
            continue
        quebra = quebra_do(feito)
        if marca is not None:
            escolhido = ESCOLHA + projeto.sem_rodape + quebra + feito
            documento.partes[0].insert(0, ESCOLHA + projeto.sem_rodape)
            documento.monta()
            levados = {LUGAR_SECAO, LUGAR_FIM}
            achados = {indice for indice in range(len(documento.partes))
                       if lugares_da_parte(documento, indice, levados)}
            data = hoje(projeto.formato)
            _, trechos = esperado(projeto, documento, {lugar: projeto.montado(lugar, caminho, data)
                                                       for lugar in levados})
            sem, _ = esperado(projeto, documento, {}, achados)
            conf.igual("tira com marca", sem, "com_rodapes", rodapes, caminho, escolhido)
            conf.igual("sobra com marca", [(lugar, primeira, SOBRA) for lugar, primeira, _ in trechos], "problemas",
                       rodapes, caminho, escolhido)
            conf.igual("sem rodapé escolhido", {}, "rodapes_montados", rodapes, caminho, escolhido)
        else:
            pecas = projeto.pecas[LUGAR_FIM] + [("texto", " " + palavra(sorte))]
            antigo = projeto.montado(LUGAR_FIM, caminho, hoje(projeto.formato)).replace("\n", quebra)
            projeto.escreve_modelo(LUGAR_FIM, pecas)
            rodapes = conf.responde("ler de novo", "le_rodapes", projeto.arquivo, projeto.raiz)
            trocado = conf.responde("trocar", "com_rodapes", rodapes, caminho, feito) if rodapes else None
            if trocado is not None:
                novo = projeto.montado(LUGAR_FIM, caminho, hoje(projeto.formato)).replace("\n", quebra)
                if antigo not in trocado or not trocado.endswith(novo + quebra):
                    conf.falha("troca sem marca", f"o velho devia ficar e o novo entrar no fim: {trocado!r}")


def caso_escolha(conf, pasta, sorte):
    """A linha de escolha, o sem_rodape, o fora e os erros de qual rodapé o documento leva."""
    projeto = Projeto(pasta, sorte, MARCA)
    outro_tipo, outro_fim, so_outro = palavra(sorte) + "t", palavra(sorte) + "f", palavra(sorte) + "o"

    def muda(c):
        c["tipos"][outro_tipo] = {"arquivos": [f"**/*.{projeto.ext}ç"], "separador": "\n"}
        modelo = c["rodapes"][projeto.nome_fim]["modelos"][projeto.tipo]
        c["rodapes"][outro_fim] = {"modelos": {projeto.tipo: modelo}, "documentos": [f"{palavra(sorte)}-ç/**"],
                                   "lugar": LUGAR_FIM}
        c["rodapes"][so_outro] = {"modelos": {outro_tipo: modelo}, "documentos": ["**"], "lugar": LUGAR_FIM}
    arquivo = projeto.com(muda)
    rodapes = conf.responde("ler", "le_rodapes", arquivo, projeto.raiz)
    if rodapes is None:
        return
    texto = frase(sorte) + "\n"
    caminho_fora = f"{projeto.fora}/{palavra(sorte)}.{projeto.ext}"
    caminho = f"{palavra(sorte)}.{projeto.ext}"
    conf.igual("fora", [], "problemas", rodapes, caminho_fora, texto)
    escolha = f"{ESCOLHA}{projeto.nome_secao}\n{ESCOLHA}{projeto.nome_fim}\n{ESCOLHA}{projeto.nome_fim}\n"
    montados = conf.responde("escolha", "rodapes_montados", rodapes, caminho_fora, escolha + texto)
    if montados is not None and sorted(montados) != sorted(LUGARES):
        conf.falha("escolha", f"devia levar os dois rodapés escolhidos, e leva {sorted(montados)}")
    conf.igual("sem_rodape sozinho", {}, "rodapes_montados", rodapes, caminho, f"{ESCOLHA}{projeto.sem_rodape}\n"
               + texto)
    casos = [
        ("nome que não é de rodapé", f"{ESCOLHA}{palavra(sorte)}ç\n"),
        ("sem_rodape junto de outro", f"{ESCOLHA}{projeto.sem_rodape}\n{ESCOLHA}{projeto.nome_fim}\n"),
        ("rodapé sem modelo para o tipo", f"{ESCOLHA}{so_outro}\n"),
        ("dois rodapés do mesmo lugar", f"{ESCOLHA}{projeto.nome_fim}\n{ESCOLHA}{outro_fim}\n"),
    ]
    for caso, linhas in casos:
        conf.da_erro(caso, "com_rodapes", rodapes, caminho, linhas + texto, palavra=caminho)
    arquivo = projeto.com(lambda c: c["rodapes"].__setitem__(outro_fim, {
        "modelos": c["rodapes"][projeto.nome_fim]["modelos"], "documentos": ["**"], "lugar": LUGAR_FIM}))
    rodapes = conf.responde("ler", "le_rodapes", arquivo, projeto.raiz)
    if rodapes is not None:
        conf.da_erro("dois rodapés cobrem o mesmo lugar", "com_rodapes", rodapes, caminho, texto, palavra=caminho)
        conf.da_erro("não é documento", "com_rodapes", rodapes, f"{palavra(sorte)}.ç{projeto.ext}", texto)


def caso_fora_do_dia(conf, pasta, sorte):
    """O rodapé diferente, a data do campo hoje e o que vem depois do último rodapé."""
    for marca in (MARCA, None):
        projeto = Projeto(pasta, sorte, marca)
        rodapes = conf.responde("ler", "le_rodapes", projeto.arquivo, projeto.raiz)
        if rodapes is None:
            return
        documento = Documento(sorte)
        documento.cauda = [FIM_DA_PARTE + frase(sorte), frase(sorte)]
        documento.final = True
        documento.monta()
        caminho = f"{palavra(sorte)}.{projeto.ext}"
        data = hoje(projeto.formato)
        feito = conf.responde("pôr", "com_rodapes", rodapes, caminho, documento.texto)
        if feito is None or data not in feito:
            continue
        _, trechos = esperado(projeto, documento, {LUGAR_FIM: projeto.montado(LUGAR_FIM, caminho, data)})
        linha_do_fim = trechos[-1][1]
        quebra = quebra_do(feito)
        outra = datetime.datetime(sorte.randint(2001, 2020), sorte.randint(1, 12), sorte.randint(1, 28)).astimezone()
        conf.igual("outra data em hoje", [], "problemas", rodapes, caminho,
                   feito.replace(data, outra.strftime(projeto.formato)))
        conf.igual("o que não é data em hoje", [(LUGAR_FIM, linha_do_fim, DIFERENTE)], "problemas", rodapes, caminho,
                   feito.replace(data, palavra(sorte)))
        conf.igual("sem a quebra do fim", [(LUGAR_FIM, linha_do_fim, DIFERENTE)], "problemas", rodapes, caminho,
                   feito[:-len(quebra)])
        mexido, linha = mexido_na_linha(feito, linha_do_fim, marca)
        conf.igual("último rodapé fora do jeito", [(LUGAR_FIM, linha, DIFERENTE)], "problemas", rodapes, caminho,
                   mexido)
        documento = Documento(sorte)
        documento.partes = documento.partes[:1] + [[SECAO + frase(sorte), frase(sorte)] for _ in range(2)]
        documento.cauda = []
        documento.monta()
        caminho = f"{projeto.com_secao}/{palavra(sorte)}.{projeto.ext}"
        feito = conf.responde("pôr nas seções", "com_rodapes", rodapes, caminho, documento.texto)
        if feito is None:
            continue
        _, trechos = esperado(projeto, documento, {lugar: projeto.montado(lugar, caminho, data) for lugar in LUGARES})
        mexido, linha = mexido_na_linha(feito, trechos[0][1], marca)
        conf.igual("rodapé do meio fora do jeito", [(LUGAR_SECAO, linha, DIFERENTE)], "problemas", rodapes, caminho,
                   mexido)


def mexido_na_linha(texto, linha, marca):
    """O texto com o rodapé que começa na linha mexido, e a linha em que o rodapé fica: com marca, uma letra a mais
    logo depois da marca; sem marca, uma linha em branco a mais antes dele."""
    quebra = quebra_do(texto)
    posicao = sum(len(pedaco) for pedaco in re.split(r"(\r\n|\r|\n)", texto)[:2 * (linha - 1)])
    if marca is not None:
        depois_da_marca = posicao + len(marca) + len(quebra)
        return texto[:depois_da_marca] + "ç" + texto[depois_da_marca:], linha
    return texto[:posicao] + quebra + texto[posicao:], linha + 1


def caso_erros_no_documento(conf, pasta, sorte):
    """As linhas iguais à marca a mais numa parte e o link refeito que a expressão não acha inteiro."""
    projeto = Projeto(pasta, sorte, MARCA)
    rodapes = conf.responde("ler", "le_rodapes", projeto.arquivo, projeto.raiz)
    if rodapes is None:
        return
    f = frase
    caminho = f"{projeto.com_secao}/{palavra(sorte)}.{projeto.ext}"
    casos = [
        ("marca no começo com seções", f"{f(sorte)}\n{MARCA}\n{SECAO}{f(sorte)}\n"),
        ("duas marcas numa seção do meio", f"{SECAO}{f(sorte)}\n{MARCA}\n{MARCA}\n{SECAO}{f(sorte)}\n"),
        ("três marcas na última seção", f"{SECAO}{f(sorte)}\n{MARCA}\n{MARCA}\n {MARCA} \n"),
        ("duas marcas sem seções", f"{f(sorte)}\n{MARCA}\n{f(sorte)}\n{MARCA}\n"),
    ]
    for caso, texto in casos:
        conf.da_erro(caso, "com_rodapes", rodapes, caminho, texto, palavra=caminho)
    com_espaco = projeto.raiz / f"{palavra(sorte)} {palavra(sorte)}"
    escreve(com_espaco / f"{palavra(sorte)}.txt", f(sorte))
    modelo = com_espaco / palavra(sorte) / f"{palavra(sorte)}.txt"
    escreve(modelo, f"[{palavra(sorte)}](../{next(com_espaco.glob('*.txt')).name})")
    arquivo = projeto.com(lambda c: c["rodapes"][projeto.nome_fim]["modelos"].__setitem__(
        projeto.tipo, relativo(modelo, projeto.dados)))
    com_link = conf.responde("ler com o modelo novo", "le_rodapes", arquivo, projeto.raiz)
    fora_do_espaco = f"{palavra(sorte)}.{projeto.ext}"
    if com_link is not None:
        conf.da_erro("link refeito que a expressão não acha", "com_rodapes", com_link, fora_do_espaco, f(sorte),
                     palavra=fora_do_espaco)
    texto = (f"{SECAO}{f(sorte)}\n{MARCA}\n{f(sorte)}\n{FIM_DA_PARTE}{f(sorte)}\n{FIM_DA_PARTE}{f(sorte)}\n"
             f"{SECAO}{f(sorte)}\n")
    _, trechos = conf.responde("cauda", "separa", rodapes, f"{palavra(sorte)}.{projeto.ext}", texto) or (None, [])
    if trechos != [(LUGAR_FIM, 2, 4)]:
        conf.falha("a última linha de fim", f"o rodapé vai até antes da última linha de fim, e veio {trechos}")


class Repositorio:
    """Um repositório git de prova, com a pasta raiz dentro dele e commits com datas sorteadas."""

    def __init__(self, pasta, sorte):
        self.pasta, self.sorte = pasta / palavra(sorte), sorte
        self.pasta.mkdir()
        self.ambiente = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                             GIT_AUTHOR_NAME="ç", GIT_AUTHOR_EMAIL="ç@ç", GIT_COMMITTER_NAME="ç",
                             GIT_COMMITTER_EMAIL="ç@ç")
        self.git("init", "-q")

    def git(self, *palavras, ambiente=None):
        subprocess.run(["git", *palavras], cwd=self.pasta, env={**self.ambiente, **(ambiente or {})}, check=True,
                       capture_output=True, stdin=subprocess.DEVNULL)

    def data(self):
        s = self.sorte
        return f"{s.randint(2001, 2025)}-{s.randint(1, 12):02d}-{s.randint(1, 28):02d}T{s.randint(0, 23):02d}:" \
               f"{s.randint(0, 59):02d}:00{s.choice(FUSOS)}"

    def commit(self):
        """Faz um commit de tudo, com a data do commit e a do autor diferentes; dá a data do commit."""
        data = self.data()
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", palavra(self.sorte), ambiente={"GIT_COMMITTER_DATE": data,
                                                                 "GIT_AUTHOR_DATE": self.data()})
        return data


def caso_mudanca(conf, pasta, sorte):
    """O campo mudanca: a data do último commit em que o texto mudou, no fuso dele, sem contar os rodapés e seguindo
    a troca de nome; a do dia quando a mudança ainda não entrou num commit."""
    repositorio = Repositorio(pasta, sorte)
    raiz = repositorio.pasta / palavra(sorte)
    abre, fecha = sorte.choice(PARES)
    palavra_do_modelo = palavra(sorte)
    escreve(raiz / "m.txt", f"{palavra_do_modelo} {abre}mudanca{fecha}")
    marca = sorte.choice((None, MARCA))
    tipo = {"arquivos": ["**/*.ç"], "separador": "\n\n"}
    if marca:
        tipo["marca"] = marca
    escreve(raiz / "r.json", json.dumps({
        "versao_schema": 1, "tipos": {"t": tipo},
        "rodapes": {"r": {"modelos": {"t": "m.txt"}, "documentos": ["**"], "lugar": LUGAR_FIM}},
        "campos": {"abre": abre, "fecha": fecha}, "formato_da_data": FORMATO_COM_HORA}, ensure_ascii=False))

    def montado(data):
        return {LUGAR_FIM: f"{palavra_do_modelo} {data}"}

    def no_formato(data):
        return datetime.datetime.fromisoformat(data).strftime(FORMATO_COM_HORA)

    def rodapes():
        return conf.responde("ler", "le_rodapes", raiz / "r.json", raiz)
    caminho, texto = f"{palavra(sorte)}/{palavra(sorte)}.ç", frase(sorte) + "\n"
    escreve(raiz / caminho, texto)
    primeira = repositorio.commit()
    conf.igual("primeiro commit", montado(no_formato(primeira)), "rodapes_montados", rodapes(), caminho, texto)
    feito = conf.responde("pôr", "com_rodapes", rodapes(), caminho, texto)
    if feito is None:
        return
    escreve(raiz / caminho, feito)
    repositorio.commit()
    conf.igual("commit só do rodapé", montado(no_formato(primeira)), "rodapes_montados", rodapes(), caminho, feito)
    conf.igual("em dia", [], "problemas", rodapes(), caminho, feito)
    novo = f"{palavra(sorte)}ç/{palavra(sorte)}.ç"
    (raiz / novo).parent.mkdir()
    repositorio.git("mv", relativo(raiz / caminho, repositorio.pasta), relativo(raiz / novo, repositorio.pasta))
    conf.igual("troca de nome antes do commit", montado(no_formato(primeira)), "rodapes_montados", rodapes(), novo,
               feito)
    repositorio.commit()
    conf.igual("troca de nome no commit", montado(no_formato(primeira)), "rodapes_montados", rodapes(), novo, feito)
    mudado = frase(sorte) + "\n" + feito
    conf.igual_hoje("mudança antes do commit", montado, FORMATO_COM_HORA, "rodapes_montados", rodapes(), novo, mudado)
    escreve(raiz / novo, mudado)
    ultima = repositorio.commit()
    conf.igual("mudança no commit", montado(no_formato(ultima)), "rodapes_montados", rodapes(), novo, mudado)
    conf.igual_hoje("documento novo", montado, FORMATO_COM_HORA, "rodapes_montados", rodapes(),
                    f"{palavra(sorte)}.ç", texto)


CASOS = [("padrões", caso_padroes), ("erros de leitura", caso_erros_de_leitura)] + \
        [(f"montagem {numero}", caso_montagem) for numero in range(PROJETOS)] + \
        [("tirar e trocar", caso_tirar_e_trocar), ("escolha", caso_escolha), ("fora do dia", caso_fora_do_dia),
         ("erros no documento", caso_erros_no_documento), ("mudança", caso_mudanca)]


def main():
    peca, gravacao = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    if any((pasta / ".git").exists() for pasta in (gravacao, *gravacao.parents)):
        raise RuntimeError(f"{gravacao}: a pasta de gravação fica dentro de um repositório git")
    conferencia, sorte = Conferencia(carrega(peca)), random.Random(SEMENTE)
    for numero, (nome, caso) in enumerate(CASOS):
        pasta = gravacao / f"{numero:02d}-{nome.replace(' ', '-')}"
        pasta.mkdir()
        antes = len(conferencia.falhas)
        caso(conferencia, pasta, sorte)
        if len(conferencia.falhas) == antes:
            shutil.rmtree(pasta)
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
