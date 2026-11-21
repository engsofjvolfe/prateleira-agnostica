"""
Confere dados contra o molde deles.

O molde é um arquivo em JSON Schema, que diz a forma que os dados têm de ter. Antes de
conferir os dados, o próprio molde se confere contra o molde dos moldes
(esquemas/molde.schema.json), que traz as palavras que esta peça sabe conferir: assim, toda
regra do molde é conferida. O "pattern" é uma expressão regular do Python, procurada no
texto. O "$ref" aponta para o próprio molde ("#"), para um molde de dentro dele
("#/$defs/nome") ou para um molde de dentro de um molde comum
("arquivo.schema.json#/$defs/nome"), que se procura na pasta do molde que aponta para ele e,
depois, na pasta esquemas desta peça.

Dá às peças: conferido e le_conferido. Todo erro é um ErroDeDados.
"""
import json
from collections import namedtuple
from pathlib import Path

from erro_de_dados import ErroDeDados
from expressao_regular import compila
from leitura_de_json import le_json

MOLDES = Path(__file__).resolve().parent / "esquemas"  # a pasta do molde dos moldes e dos moldes comuns
MOLDE_DOS_MOLDES = MOLDES / "molde.schema.json"  # as palavras do JSON Schema que esta peça confere, e o valor de cada
REFERENCIA = "#"  # o sinal que, numa referência, separa o arquivo do molde comum do lugar dentro dele
CAMINHO = "/"  # o sinal que separa as partes de um lugar, nos dados e na referência
ESCAPES_DA_REFERENCIA = (("~1", "/"), ("~0", "~"))  # como a referência escreve "/" e "~" num nome, nesta ordem

# O tipo do Python de cada tipo do JSON Schema; o inteiro vem antes do número, para o tipo de um valor ser o mais
# estreito.
TIPOS = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool,
         "null": type(None)}

# A raiz das referências de "#": o molde, o arquivo dele (None quando ele não é um molde comum) e a pasta em que se
# procura primeiro um molde comum.
_Raiz = namedtuple("_Raiz", "molde arquivo pasta")


def _mostra(valor):
    """O valor escrito como no JSON, para a mensagem de erro."""
    return json.dumps(valor, ensure_ascii=False)


def _do_tipo(valor, tipo):
    """Se o valor é do tipo do molde. O booleano não é número, e o inteiro é o número escrito sem ponto."""
    if tipo not in TIPOS:
        raise ErroDeDados(f"o molde usa um tipo desconhecido: {tipo!r}")
    return isinstance(valor, TIPOS[tipo]) and (tipo == "boolean" or not isinstance(valor, bool))


def _tipo_de(valor):
    """O tipo do JSON Schema de um valor, o mais estreito."""
    return next(tipo for tipo in TIPOS if _do_tipo(valor, tipo))


def _igual(a, b):
    """Se dois valores são o mesmo: o booleano só é igual a booleano, o número a número de mesmo valor, e as listas
    e os objetos, item por item."""
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_igual(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_igual(a[nome], b[nome]) for nome in a)
    numeros = [_do_tipo(valor, "number") for valor in (a, b)]
    if all(numeros):
        return a == b
    return not any(numeros) and type(a) is type(b) and a == b


def _junta(erros):
    """Os erros [(lugar, motivo)] numa linha só, cada um com o lugar ("/" é a raiz dos dados)."""
    return "; ".join(f"{lugar or CAMINHO}: {motivo}" for lugar, motivo in erros)


def _fora_do_texto(dados, molde, lugar):
    erros = []
    if len(dados) < molde.get("minLength", 0):
        erros.append((lugar, f"{_mostra(dados)} tem menos de {molde['minLength']} caractere(s)"))
    if "maxLength" in molde and len(dados) > molde["maxLength"]:
        erros.append((lugar, f"{_mostra(dados)} tem mais de {molde['maxLength']} caractere(s)"))
    if "pattern" in molde:
        forma = compila(molde["pattern"], f"a forma {_mostra(molde['pattern'])} do molde")
        if not forma.search(dados):
            erros.append((lugar, f"{_mostra(dados)} não segue a forma {molde['pattern']}"))
    return erros


def _fora_do_numero(dados, molde, lugar):
    erros = []
    if "minimum" in molde and dados < molde["minimum"]:
        erros.append((lugar, f"{_mostra(dados)} é menor que {molde['minimum']}"))
    if "maximum" in molde and dados > molde["maximum"]:
        erros.append((lugar, f"{_mostra(dados)} é maior que {molde['maximum']}"))
    return erros


class _Conferencia:
    """Uma conferência de dados contra um molde. Guarda o molde de cada arquivo já lido, para ler e conferir cada
    um uma vez só."""

    def __init__(self):
        self.lidos = {}

    def dos_dados(self, dados, molde, pasta):
        """[(lugar, motivo)] de cada valor dos dados fora do molde, com o lugar dentro dos dados ("/a/0/b"; "" é a
        raiz). Antes, o molde se confere contra o molde dos moldes. A pasta é onde se procura primeiro um molde
        comum."""
        self.confere_molde(molde)
        return self.fora(dados, molde, _Raiz(molde, None, pasta), "")

    def raiz_do_arquivo(self, arquivo):
        """A raiz do molde de um arquivo, lido e conferido contra o molde dos moldes."""
        arquivo = arquivo.resolve()
        if arquivo not in self.lidos:
            molde = le_json(arquivo)
            self.lidos[arquivo] = _Raiz(molde, arquivo, arquivo.parent)
            self.confere_molde(molde)
        return self.lidos[arquivo]

    def confere_molde(self, molde):
        """Erro (ErroDeDados), que diz cada lugar, quando o molde sai do molde dos moldes: tem uma palavra de fora
        dele, ou o valor de uma palavra não é da forma que ela pede."""
        dos_moldes = self.raiz_do_arquivo(MOLDE_DOS_MOLDES)
        erros = self.fora(molde, dos_moldes.molde, dos_moldes, "")
        if erros:
            raise ErroDeDados(f"o molde sai do que o {MOLDE_DOS_MOLDES.name} aceita: {_junta(erros)}")

    def referido(self, referencia, raiz):
        """(molde, raiz dele) para que a referência aponta: na raiz dada, a própria raiz ("#") ou um molde de
        dentro dela; com o arquivo de um molde comum antes do "#", o desse arquivo, achado na pasta da raiz ou,
        senão, na pasta dos moldes, e que passa a ser a raiz das referências de dentro dele."""
        arquivo, _, lugar = referencia.partition(REFERENCIA)
        if arquivo:
            pastas = [pasta for pasta in (raiz.pasta, MOLDES) if pasta is not None]
            achado = next((pasta / arquivo for pasta in pastas if (pasta / arquivo).is_file()), pastas[-1] / arquivo)
            raiz = self.raiz_do_arquivo(achado)
        alvo = raiz.molde
        for parte in lugar.split(CAMINHO)[1:]:
            for escrito, lido in ESCAPES_DA_REFERENCIA:
                parte = parte.replace(escrito, lido)
            if not isinstance(alvo, dict) or parte not in alvo:
                raise ErroDeDados(f"o molde aponta para o que não existe: {referencia!r}")
            alvo = alvo[parte]
        return alvo, raiz

    def fora_da_lista(self, dados, molde, raiz, lugar):
        erros = []
        if len(dados) < molde.get("minItems", 0):
            erros.append((lugar, f"tem menos de {molde['minItems']} item(ns)"))
        if "maxItems" in molde and len(dados) > molde["maxItems"]:
            erros.append((lugar, f"tem mais de {molde['maxItems']} item(ns)"))
        if molde.get("uniqueItems"):
            erros += [(f"{lugar}{CAMINHO}{numero}", f"{_mostra(valor)} repete um item de antes")
                      for numero, valor in enumerate(dados) if any(_igual(valor, outro) for outro in dados[:numero])]
        for numero, valor in enumerate(dados):
            erros += self.fora(valor, molde.get("items", True), raiz, f"{lugar}{CAMINHO}{numero}")
        return erros

    def fora_do_objeto(self, dados, molde, raiz, lugar):
        erros = [(f"{lugar}{CAMINHO}{nome}", "falta") for nome in molde.get("required", []) if nome not in dados]
        if len(dados) < molde.get("minProperties", 0):
            erros.append((lugar, f"tem menos de {molde['minProperties']} campo(s)"))
        if "maxProperties" in molde and len(dados) > molde["maxProperties"]:
            erros.append((lugar, f"tem mais de {molde['maxProperties']} campo(s)"))
        nomes, campos = molde.get("propertyNames", True), molde.get("properties", {})
        outros = molde.get("additionalProperties", True)
        for nome, valor in dados.items():
            dentro = f"{lugar}{CAMINHO}{nome}"
            erros += [(dentro, f"o nome {motivo}") for _, motivo in self.fora(nome, nomes, raiz, dentro)]
            if nome in campos:
                erros += self.fora(valor, campos[nome], raiz, dentro)
            elif outros is False:
                erros.append((dentro, "campo que o molde não conhece"))
            else:
                erros += self.fora(valor, outros, raiz, dentro)
        return erros

    def fora(self, dados, molde, raiz, lugar, seguidas=frozenset()):
        """[(lugar, motivo)] de cada valor dos dados fora do molde, com as referências partindo da raiz. As
        seguidas são as referências já seguidas neste mesmo valor, cada uma com o arquivo da raiz dela: a que volta
        a ela mesma sem passar a um valor de dentro dá erro (ErroDeDados)."""
        if isinstance(molde, bool):
            return [] if molde else [(lugar, "o molde não aceita valor aqui")]
        erros = []
        if "$ref" in molde:
            alvo, outra = self.referido(molde["$ref"], raiz)
            seguida = (outra.arquivo, molde["$ref"].partition(REFERENCIA)[2])
            if seguida in seguidas:
                raise ErroDeDados(f"a referência do molde volta a ela mesma: {molde['$ref']!r}")
            erros += self.fora(dados, alvo, outra, lugar, seguidas | {seguida})
        tipos = molde.get("type", list(TIPOS))
        tipos = tipos if isinstance(tipos, list) else [tipos]
        if not any([_do_tipo(dados, tipo) for tipo in tipos]):  # todos, para o tipo desconhecido sempre dar erro
            return erros + [(lugar, f"é {_tipo_de(dados)}, e não {' ou '.join(tipos)}")]
        if "const" in molde and not _igual(dados, molde["const"]):
            erros.append((lugar, f"{_mostra(dados)} não é {_mostra(molde['const'])}"))
        if "enum" in molde and not any(_igual(dados, valor) for valor in molde["enum"]):
            erros.append((lugar, f"{_mostra(dados)} não é um destes: {_mostra(molde['enum'])}"))
        if isinstance(dados, str):
            erros += _fora_do_texto(dados, molde, lugar)
        elif _do_tipo(dados, "number"):
            erros += _fora_do_numero(dados, molde, lugar)
        elif isinstance(dados, list):
            erros += self.fora_da_lista(dados, molde, raiz, lugar)
        elif isinstance(dados, dict):
            erros += self.fora_do_objeto(dados, molde, raiz, lugar)
        for parte in molde.get("allOf", []):
            erros += self.fora(dados, parte, raiz, lugar, seguidas)
        if "if" in molde:
            ramo = "else" if self.fora(dados, molde["if"], raiz, lugar, seguidas) else "then"
            erros += self.fora(dados, molde.get(ramo, True), raiz, lugar, seguidas)
        return erros


def conferido(dados, molde, nome):
    """Os dados, conferidos contra o arquivo do molde. Erro (ErroDeDados) que diz o nome dos dados e cada valor
    fora do molde, com o lugar dele dentro dos dados. O erro do próprio molde diz o arquivo dele."""
    molde = Path(molde)
    regras = le_json(molde)
    try:
        erros = _Conferencia().dos_dados(dados, regras, molde.parent)
    except ErroDeDados as erro:
        raise ErroDeDados(f"{molde}: {erro}") from None
    if erros:
        raise ErroDeDados(f"{nome}: fora do molde {molde.name}: {_junta(erros)}")
    return dados


def le_conferido(caminho, molde):
    """Os dados de um arquivo JSON, lidos (le_json) e conferidos contra o arquivo do molde (conferido), com o
    arquivo dos dados no erro."""
    return conferido(le_json(caminho), molde, caminho)
