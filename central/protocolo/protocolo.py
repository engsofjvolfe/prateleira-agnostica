"""
Lê a folha do protocolo, para os vigias entenderem o programa que os chama.

O programa entrega ao vigia um formulário, em JSON, e espera a resposta num formato dele. Os
nomes que o programa usa ficam numa folha do projeto, lida pelo molde em
esquemas/protocolo.schema.json; no código ficam só os nomes do molde.

Dá às peças:
  - ler: a folha de um arquivo, conferida;
  - le_evento: as partes de um formulário;
  - chamadas: os usos de um lote;
  - textos_de: cada texto de dentro de um valor JSON;
  - caminho: o caminho absoluto e sem atalhos de um arquivo que um uso nomeia;
  - resposta: o que o vigia responde, por um dos modelos da folha;
  - anotacao: o arquivo em que um vigia anota o que guarda de uma sessão.

Todo erro é um ErroDeDados.
"""
import hashlib
from pathlib import Path

from conferencia_de_molde import le_conferido
from erro_de_dados import ErroDeDados
from expressao_regular import compila
from leitura_de_json import de_json
from modelo_de_texto import campos, preenche
from repetidos import repetidos

MOLDE = Path(__file__).resolve().parent / "esquemas" / "protocolo.schema.json"
EVENTOS = ("antes", "fim", "lote")  # os momentos, pelo nome no molde; o lote pode faltar na folha
# os campos do formulário, além do nome do momento; o dos usos só vem no lote, e pode faltar na folha
PARTES = ("sessao", "ferramenta", "entrada", "pasta", "fim_repetido", "chamadas")
LOTE = ("ferramenta", "entrada", "resposta")  # os campos de cada uso de um lote, pelo nome no molde
LINHA = "linha"  # o grupo da forma de uma linha numerada que traz o número dela
RESPOSTAS = ("nega", "contexto", "trava")  # os modelos do que o vigia responde, pelo nome no molde
TEXTO = "texto"  # o lugar do modelo que recebe o texto do vigia, escrito {texto}
FORMULARIO = "o formulário"  # o nome do formulário nas mensagens de erro
IMPRESSAO_DIGITAL = "sha256"  # a conta que faz o nome de cada anotação
CODIFICACAO = "utf-8"  # a forma em que a identificação entra na conta


def _sem_repetir(itens, onde):
    """Os itens, quando nenhum se repete; senão, erro que diz onde e quais."""
    mesmos = repetidos(itens)
    if mesmos:
        raise ErroDeDados(f"{onde}: repetido(s): {mesmos}")
    return itens


def textos_de(valor):
    """Cada texto de dentro de um valor JSON, nos objetos e nas listas, na ordem."""
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for dentro in valor.values():
            yield from textos_de(dentro)
    elif isinstance(valor, list):
        for dentro in valor:
            yield from textos_de(dentro)


def _modelo(dados, qual):
    """O modelo de uma resposta, que o molde já conferiu ser um objeto. Erro quando um texto de dentro dele tem
    outra coisa entre chaves que não {texto}, e quando nenhum tem o {texto}."""
    valor = dados["respostas"][qual]
    nomes = [nome for escrito in textos_de(valor) for nome in campos(escrito)]
    outros = sorted({nome for nome in nomes if nome != TEXTO})
    if outros:
        raise ErroDeDados(f"respostas/{qual}: tem entre chaves o que não é {{{TEXTO}}}: {outros}")
    if not nomes:
        raise ErroDeDados(f"respostas/{qual}: não tem o lugar do texto, {{{TEXTO}}}")
    return valor


def _confere_linha_numerada(leitura):
    """Erro quando a forma da linha numerada de uma leitura não é uma expressão regular válida ou não tem o grupo
    que traz o número da linha; a leitura sem a forma passa."""
    if "linha_numerada" not in leitura:
        return
    onde = f"leituras/{leitura['nome']}/linha_numerada"
    if LINHA not in compila(leitura["linha_numerada"], onde).groupindex:
        raise ErroDeDados(f"{onde}: não tem o grupo (?P<{LINHA}>...), que traz o número da linha")


def _folha(dados):
    """A folha pronta para os vigias, dos dados que o molde já conferiu. Erro no que o molde não vê: dois momentos
    com o mesmo nome, dois campos com o mesmo nome, a ferramenta de busca ou de leitura repetida, a forma da linha
    numerada e os modelos das respostas."""
    eventos, chaves, buscas, leituras = dados["eventos"], dados["chaves"], dados["buscas"], dados["leituras"]
    _sem_repetir([eventos[evento] for evento in EVENTOS if evento in eventos], "eventos")
    _sem_repetir([chaves[parte] for parte in ("evento",) + PARTES + ("resposta",) if parte in chaves], "chaves")
    _sem_repetir([busca["nome"] for busca in buscas], "buscas")
    _sem_repetir([leitura["nome"] for leitura in leituras], "leituras")
    for leitura in leituras:
        _confere_linha_numerada(leitura)
    return {
        "eventos": {nome: evento for evento, nome in eventos.items()},
        "chaves": chaves,
        "respostas": {qual: _modelo(dados, qual) for qual in RESPOSTAS},
        "terminal": dados["terminal"],
        "buscas": {busca["nome"]: busca["campo_padrao"] for busca in buscas},
        "escritas": dados["escritas"],
        "leituras": {leitura["nome"]: {campo: valor for campo, valor in leitura.items() if campo != "nome"}
                     for leitura in leituras},
        "resumos": dados["resumos"],
    }


def ler(caminho):
    """A folha do arquivo, conferida contra o molde e no que o molde não vê (_folha). Erro (ErroDeDados) que diz o
    arquivo, o que está errado e onde."""
    dados = le_conferido(Path(caminho), MOLDE)
    try:
        return _folha(dados)
    except ErroDeDados as erro:
        raise ErroDeDados(f"{caminho}: {erro}") from None


def le_evento(protocolo, texto):
    """{parte: valor} do formulário que chega em texto JSON: "evento", que é "antes", "fim" ou "lote", e cada
    campo que o formulário traz, pelo nome do molde. Erro (ErroDeDados) quando o formulário não é um objeto JSON e
    quando o nome do momento falta ou é de outro momento, também o do lote quando a folha não o tem."""
    dados = de_json(texto, FORMULARIO)
    if not isinstance(dados, dict):
        raise ErroDeDados(f"{FORMULARIO}: não é um objeto: {dados!r}")
    chaves = protocolo["chaves"]
    evento = dados.get(chaves["evento"])
    if not isinstance(evento, str) or evento not in protocolo["eventos"]:
        raise ErroDeDados(f"{FORMULARIO}: momento desconhecido: {evento!r}")
    return {"evento": protocolo["eventos"][evento],
            **{parte: dados[chaves[parte]] for parte in PARTES if parte in chaves and chaves[parte] in dados}}


def chamadas(protocolo, partes):
    """[{parte: valor}] de cada uso do lote que o formulário lido traz, na ordem dele: a "ferramenta", a "entrada"
    e a "resposta" que cada um traz, pelo nome do molde. Erro (ErroDeDados) quando a folha não diz o campo dos usos
    ou o da resposta, quando o formulário não traz os usos, quando eles não são uma lista e quando um deles não é
    um objeto."""
    chaves = protocolo["chaves"]
    faltam = [parte for parte in ("chamadas", "resposta") if parte not in chaves]
    if faltam:
        raise ErroDeDados(f"a folha do protocolo não diz o(s) campo(s) {faltam}")
    if "chamadas" not in partes:
        raise ErroDeDados(f"{FORMULARIO}: não traz os usos do lote, no campo {chaves['chamadas']!r}")
    lote = partes["chamadas"]
    if not isinstance(lote, list):
        raise ErroDeDados(f"{FORMULARIO}: os usos do lote não são uma lista, e sim {type(lote).__name__}")
    usos = []
    for numero, uso in enumerate(lote):
        if not isinstance(uso, dict):
            raise ErroDeDados(f"{FORMULARIO}: o uso {numero} do lote não é um objeto, e sim {type(uso).__name__}")
        usos.append({parte: uso[chaves[parte]] for parte in LOTE if chaves[parte] in uso})
    return usos


def caminho(valor, pasta):
    """O caminho absoluto e sem atalhos de um arquivo que um uso nomeia: com o ~ trocado pela pasta do usuário e,
    quando não é absoluto, a partir da pasta dada, a de onde o uso roda; a pasta que não é texto fica de fora."""
    alvo = Path(valor).expanduser()
    if not alvo.is_absolute() and isinstance(pasta, str):
        alvo = Path(pasta) / alvo
    return alvo.resolve()


def _preenchido(valor, escrito):
    """Uma cópia do valor JSON com {texto} trocado pelo texto escrito, em cada texto de dentro dele."""
    if isinstance(valor, str):
        return preenche(valor, {TEXTO: escrito})
    if isinstance(valor, dict):
        return {nome: _preenchido(dentro, escrito) for nome, dentro in valor.items()}
    if isinstance(valor, list):
        return [_preenchido(dentro, escrito) for dentro in valor]
    return valor


def resposta(protocolo, qual, texto):
    """Uma cópia do modelo "nega", "contexto" ou "trava", com o texto do vigia no lugar de {texto}."""
    return _preenchido(protocolo["respostas"][qual], texto)


def anotacao(pasta, sessao, *chaves):
    """O arquivo, na pasta, em que um vigia anota o que guarda da sessão; com chaves, o de cada chave, dentro da
    pasta da sessão, uma pasta dentro da outra na ordem das chaves. Cada nome é a impressão digital da
    identificação da sessão ou da chave, e por isso nunca sai da pasta. A sessão sem identificação e a chave que
    não é texto dão erro (ErroDeDados)."""
    if not isinstance(sessao, str) or not sessao:
        raise ErroDeDados(f"sessão sem identificação: {sessao!r}")
    for chave in chaves:
        if not isinstance(chave, str):
            raise ErroDeDados(f"chave de anotação que não é texto: {chave!r}")
    return Path(pasta).joinpath(*(hashlib.new(IMPRESSAO_DIGITAL, nome.encode(CODIFICACAO)).hexdigest()
                                  for nome in (sessao, *chaves)))
