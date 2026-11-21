"""
Monta, põe, acha e tira o rodapé de um documento, pelo arquivo dos rodapés que o projeto escreve: os tipos de
documento, os rodapés e os modelos deles. O rodapé se monta do modelo, com cada link refeito para a pasta do documento
e cada campo trocado pelo valor dele, e fica no fim do documento ou no fim de cada seção.

Dá às peças: le_rodapes, eh_documento, com_rodapes, problemas, rodapes_montados e separa. Todo erro é um ErroDeDados.
"""
import bisect
import datetime
import os
import re
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path

from caminho_escrito import caminho_escrito
from conferencia_de_molde import le_conferido
from erro_de_dados import ErroDeDados
from expressao_regular import compila
from leitura_de_texto import le_texto
from repetidos import repetidos
from repositorio_git import no_repositorio
from texto_de_comando import texto_do_comando

MOLDE = Path(__file__).resolve().parent / "esquemas" / "rodape-de-documento.schema.json"  # o molde dos rodapés
SECAO, FIM = "secao", "fim"  # os lugares de um rodapé
LUGARES = (SECAO, FIM)  # os lugares, na ordem em que ficam no fim de uma parte
FALTA, DIFERENTE, SOBRA = "falta", "diferente", "sobra"  # os motivos de um rodapé fora do dia
CAMINHO, NOME, MUDANCA, HOJE = "caminho", "nome", "mudanca", "hoje"  # os campos que a peça dá
CAMPOS_DA_PECA = (CAMINHO, NOME, MUDANCA, HOJE)
CAMPOS_DE_DATA = (MUDANCA, HOJE)
ALVO, NOME_ESCOLHIDO = "alvo", "nome"  # o grupo das expressões de links e o da linha de escolha
QUEBRA = re.compile(r"\r\n|\r|\n")  # uma quebra de linha, escrita de qualquer jeito
QUEBRA_DO_MODELO = "\n"  # a quebra de linha do modelo lido e a do documento que não tem nenhuma
ESPACOS = re.compile(r"\s+")  # os espaços e as quebras de linha seguidos
ESQUEMA = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*:")  # o esquema no começo de um alvo, como "https:"
ALVOS_QUE_FICAM = ("#", "/")  # os começos de um alvo que fica como está
LUGAR_NO_ARQUIVO = "#"  # o que separa o caminho do lugar dentro do arquivo
BARRA = "/"  # o que separa as partes de um caminho
QUALQUER_PARTE, QUALQUER_PEDACO, QUALQUER_CARACTERE = "**", "*", "?"  # o que um padrão aceita
QUALQUER_TEXTO = r"[\s\S]*?"  # no achador, o lugar do valor de um campo que pode ter mais de uma linha
QUALQUER_LINHA = r"[^\r\n]*?"  # no achador e na comparação, o lugar de um caminho ou de um valor de uma linha só
QUALQUER_ESPACO = r"\s+"  # no achador, o lugar de um espaço ou de uma quebra de linha do modelo
SO_ESPACOS_ATE_O_FIM = r"\s*\Z"  # no achador, o que pode vir depois do rodapé, até o fim da parte
GIT, HEAD = "git", "HEAD"
RENOMEADO, TROCA_DE_NOME = "2 ", "R"  # no "git status --porcelain=v2": a linha do arquivo com outro nome
CAMPOS_DO_RENOMEADO = 9  # quantos espaços vêm antes do caminho, nessa linha

Problema = namedtuple("Problema", "lugar linha motivo")  # um rodapé fora do dia
Trecho = namedtuple("Trecho", "lugar primeira ultima")  # as linhas em que um rodapé está


@dataclass(frozen=True)
class _Tipo:
    nome: str
    arquivos: tuple
    separador: str
    links: tuple
    partes_sem_link: tuple
    marca: object
    linha_de_escolha: object
    linha_de_secao: object
    linha_de_fim: object


@dataclass(frozen=True)
class _Link:
    inicio: int
    fim: int
    alvo_inicio: int
    alvo_fim: int
    expressao: object
    destino: object  # o caminho inteiro do arquivo ou da pasta; None quando o alvo fica como está
    lugar: str  # o que vem depois do "#", com ele
    barra: bool  # o caminho escrito termina com "/"


@dataclass(frozen=True)
class _Campo:
    inicio: int
    fim: int
    nome: str


@dataclass(frozen=True)
class _Modelo:
    arquivo: Path
    texto: str
    links: tuple
    campos: tuple
    achador: object  # a expressão que acha, num documento, o rodapé feito deste modelo


@dataclass(frozen=True)
class _Rodape:
    nome: str
    modelos: dict
    documentos: tuple
    fora: tuple
    lugar: str


@dataclass(frozen=True)
class Rodapes:
    """Os rodapés lidos e conferidos: a resposta do le_rodapes."""
    arquivo: Path
    raiz: Path
    tipos: dict
    rodapes: dict
    valores: dict
    formato_da_data: object
    sem_rodape: object
    nao_documentos: frozenset
    git: dict = field(default_factory=dict, compare=False)  # o que se pergunta ao git uma vez só


@dataclass(frozen=True)
class _Parte:
    inicio: int
    fim: int
    capacidade: int  # quantos rodapés com marca cabem nela


@dataclass(frozen=True)
class _Achado:
    parte: int
    lugar: str
    inicio: int  # o começo da linha em que o rodapé começa
    fim: int  # o começo do rodapé seguinte da parte, ou o fim da parte


@dataclass(frozen=True)
class _Analise:
    rodapes: Rodapes
    caminho: str
    texto: str
    tipo: _Tipo
    quebra: str
    linhas: tuple
    partes: tuple
    cauda: int  # onde começa o que fica depois da última parte
    levados: dict
    achados: tuple


# ---------------------------------------------------------------- os padrões


def _padrao(texto):
    """As partes de um padrão: a expressão de cada uma, ou None para "**"."""
    partes = []
    for parte in texto.split(BARRA):
        if parte == QUALQUER_PARTE:
            partes.append(None)
            continue
        traduzida = "".join(".*" if letra == QUALQUER_PEDACO else "." if letra == QUALQUER_CARACTERE
                            else re.escape(letra) for letra in parte)
        partes.append(re.compile(traduzida, re.DOTALL))
    return tuple(partes)


def _pega(padrao, caminho):
    """Se o padrão pega o caminho, com "/" entre as partes."""
    partes = caminho.split(BARRA)
    posicoes = {0}
    for parte in padrao:
        if not posicoes:
            return False
        if parte is None:
            posicoes = set(range(min(posicoes), len(partes) + 1))
        else:
            posicoes = {j + 1 for j in posicoes if j < len(partes) and parte.fullmatch(partes[j])}
    return len(partes) in posicoes


# ---------------------------------------------------------------- a leitura do arquivo dos rodapés


def _lugar(*chaves):
    """O lugar de um valor no arquivo, como "/a/0/b"."""
    return "".join(BARRA + str(chave).replace("~", "~0").replace(BARRA, "~1") for chave in chaves)


def _expressao(arquivo, lugar, texto, grupo):
    """A expressão pronta; com o grupo, ela tem de tê-lo."""
    expressao = compila(texto, f"{arquivo}: {lugar}")
    if grupo is not None and grupo not in expressao.groupindex:
        raise ErroDeDados(f"{arquivo}: {lugar}: a expressão não tem o grupo {grupo!r}")
    return expressao


def _opcional(arquivo, dados, lugar, chave, grupo=None):
    texto = dados.get(chave)
    return None if texto is None else _expressao(arquivo, _lugar(*lugar, chave), texto, grupo)


def _sem_padrao_repetido(arquivo, dados):
    listas = [(("tipos", nome, "arquivos"), tipo["arquivos"]) for nome, tipo in sorted(dados["tipos"].items())]
    for nome, rodape in sorted(dados["rodapes"].items()):
        listas += [(("rodapes", nome, chave), rodape.get(chave, [])) for chave in ("documentos", "fora")]
    for lugar, padroes in listas:
        repetido = repetidos(padroes)
        if repetido:
            raise ErroDeDados(f"{arquivo}: {_lugar(*lugar)}: padrão repetido: {repetido[0]!r}")


def _le_tipo(arquivo, nome, dados):
    lugar = ("tipos", nome)
    return _Tipo(
        nome=nome,
        arquivos=tuple(_padrao(texto) for texto in dados["arquivos"]),
        separador=dados["separador"],
        links=tuple(_expressao(arquivo, _lugar(*lugar, "links", i), texto, ALVO)
                    for i, texto in enumerate(dados.get("links", []))),
        partes_sem_link=tuple(_expressao(arquivo, _lugar(*lugar, "partes_sem_link", i), texto, None)
                              for i, texto in enumerate(dados.get("partes_sem_link", []))),
        marca=dados.get("marca"),
        linha_de_escolha=_opcional(arquivo, dados, lugar, "linha_de_escolha", NOME_ESCOLHIDO),
        linha_de_secao=_opcional(arquivo, dados, lugar, "linha_de_secao"),
        linha_de_fim=_opcional(arquivo, dados, lugar, "linha_de_fim"),
    )


def _aparado(texto):
    """O texto sem as linhas em branco do começo e sem os espaços e as quebras de linha do fim."""
    linhas = texto.split(QUEBRA_DO_MODELO)
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    return QUEBRA_DO_MODELO.join(linhas).rstrip()


def _cruzam(inicio, fim, outro_inicio, outro_fim):
    return inicio < outro_fim and outro_inicio < fim


def _le_link(achado, expressao, caminho_do_modelo, erro):
    inicio_do_alvo, fim_do_alvo = achado.span(ALVO)
    alvo = achado.group(ALVO)
    fica = alvo is None or ESQUEMA.match(alvo) or alvo.startswith(ALVOS_QUE_FICAM)
    if fica:
        return _Link(achado.start(), achado.end(), inicio_do_alvo, fim_do_alvo, expressao, None, "", False)
    escrito, separador, depois = alvo.partition(LUGAR_NO_ARQUIVO)
    destino = os.fspath(caminho_escrito(caminho_do_modelo, escrito))
    if not os.path.exists(destino):
        raise erro(f"o link {achado.group()!r} leva a {destino}, que não existe")
    return _Link(achado.start(), achado.end(), inicio_do_alvo, fim_do_alvo, expressao, destino, separador + depois,
                 escrito.endswith(BARRA))


def _links_do_modelo(texto, tipo, caminho_do_modelo, erro):
    sem_link = [achado.span() for expressao in tipo.partes_sem_link for achado in expressao.finditer(texto)
                if achado.start() < achado.end()]
    links = []
    for expressao in tipo.links:
        for achado in expressao.finditer(texto):
            if achado.start() == achado.end() or any(_cruzam(*achado.span(), *parte) for parte in sem_link):
                continue
            links.append(_le_link(achado, expressao, caminho_do_modelo, erro))
    links.sort(key=lambda link: (link.inicio, link.fim))
    for anterior, seguinte in zip(links, links[1:]):
        if seguinte.inicio < anterior.fim:
            raise erro(f"dois links se cruzam: {texto[anterior.inicio:anterior.fim]!r} e "
                       f"{texto[seguinte.inicio:seguinte.fim]!r}")
    return tuple(links)


def _campos_do_modelo(texto, links, campos, erro):
    if campos["expressao"] is None:
        return ()
    achados = []
    for achado in campos["expressao"].finditer(texto):
        nome = achado.group(1)
        if any(link.alvo_inicio >= 0 and _cruzam(*achado.span(), link.alvo_inicio, link.alvo_fim) for link in links):
            raise erro(f"o campo {achado.group()!r} fica dentro do alvo de um link")
        if nome not in campos["nomes"]:
            raise erro(f"o campo {nome!r} não tem valor")
        if nome in CAMPOS_DE_DATA and not campos["com_data"]:
            raise erro(f"o campo de data {nome!r} pede o formato_da_data")
        if nome == MUDANCA and not campos["no_git"]:
            raise erro(f"o campo {nome!r} pede que a pasta raiz fique num repositório git")
        achados.append(_Campo(achado.start(), achado.end(), nome))
    return tuple(achados)


def _literal(texto):
    """A expressão de um pedaço do modelo: cada espaço ou quebra de linha aceita qualquer espaço ou quebra de linha."""
    return QUALQUER_ESPACO.join(re.escape(pedaco) for pedaco in ESPACOS.split(texto))


def _achador(texto, links, campos, com_quebra):
    """A expressão que acha o rodapé do modelo com qualquer caminho nos links e qualquer valor nos campos. Só o valor
    do projeto que tem uma quebra de linha pode ter mais de uma linha."""
    curingas = sorted([(link.alvo_inicio, link.alvo_fim, QUALQUER_LINHA) for link in links if link.destino is not None]
                      + [(campo.inicio, campo.fim, QUALQUER_TEXTO if campo.nome in com_quebra else QUALQUER_LINHA)
                         for campo in campos])
    pedacos, posicao = [], 0
    for inicio, fim, curinga in curingas:
        pedacos += [_literal(texto[posicao:inicio]), curinga]
        posicao = fim
    pedacos.append(_literal(texto[posicao:]))
    return re.compile("".join(pedacos) + SO_ESPACOS_ATE_O_FIM)


def _le_modelo(arquivo, lugar, tipo, caminho, campos):
    def erro(motivo):
        return ErroDeDados(f"{arquivo}: {lugar}: {caminho}: {motivo}")
    try:
        texto = _aparado(le_texto(caminho))
    except ErroDeDados as lido:
        raise erro(lido) from None
    if not texto:
        raise erro("o modelo fica vazio")
    for numero, linha in enumerate(texto.split(QUEBRA_DO_MODELO), 1):
        if tipo.marca is not None and linha.strip() == tipo.marca.strip():
            raise erro(f"linha {numero}: igual à marca")
        for chave in ("linha_de_escolha", "linha_de_secao", "linha_de_fim"):
            expressao = getattr(tipo, chave)
            if expressao is not None and expressao.search(linha):
                raise erro(f"linha {numero}: a {chave} acha esta linha")
    links = _links_do_modelo(texto, tipo, caminho, erro)
    campos_achados = _campos_do_modelo(texto, links, campos, erro)
    return _Modelo(Path(caminho), texto, links, campos_achados,
                   _achador(texto, links, campos_achados, campos["com_quebra"]))


def _le_rodape(arquivo, nome, dados, tipos, campos):
    modelos = {}
    for nome_do_tipo, escrito in sorted(dados["modelos"].items()):
        lugar = _lugar("rodapes", nome, "modelos", nome_do_tipo)
        tipo = tipos.get(nome_do_tipo)
        if tipo is None:
            raise ErroDeDados(f"{arquivo}: {lugar}: o tipo {nome_do_tipo!r} não está em tipos")
        if dados["lugar"] == SECAO and tipo.linha_de_secao is None:
            raise ErroDeDados(f"{arquivo}: {lugar}: o lugar {SECAO!r} pede a linha_de_secao no tipo {nome_do_tipo!r}")
        caminho = os.fspath(caminho_escrito(arquivo, escrito))
        modelos[nome_do_tipo] = _le_modelo(arquivo, lugar, tipo, caminho, campos)
    return _Rodape(nome, modelos, tuple(_padrao(texto) for texto in dados["documentos"]),
                   tuple(_padrao(texto) for texto in dados.get("fora", [])), dados["lugar"])


def _expressao_dos_campos(abre, fecha):
    """A expressão de um campo: o texto que abre, o nome, sem o que abre nem o que fecha, e o texto que fecha."""
    abre, fecha = re.escape(abre), re.escape(fecha)
    return re.compile(f"{abre}((?:(?!{abre})(?!{fecha})[\\s\\S])*){fecha}")


def le_rodapes(caminho, raiz):
    """Os rodapés do arquivo, já conferidos, com os caminhos dos documentos contados a partir da pasta raiz.
    Erro (ErroDeDados) nos casos que o README lista para o arquivo dos rodapés."""
    arquivo, raiz = Path(os.path.abspath(caminho)), Path(os.path.abspath(raiz))
    dados = le_conferido(arquivo, MOLDE)
    _sem_padrao_repetido(arquivo, dados)
    tipos = {nome: _le_tipo(arquivo, nome, tipo) for nome, tipo in sorted(dados["tipos"].items())}
    campos = dados.get("campos", {})
    valores = dict(campos.get("valores", {}))
    for nome in sorted(valores):
        if nome in CAMPOS_DA_PECA:
            raise ErroDeDados(f"{arquivo}: {_lugar('campos', 'valores', nome)}: o campo {nome!r} é dado pela peça")
    sem_rodape = dados.get("sem_rodape")
    if sem_rodape is not None and sem_rodape in dados["rodapes"]:
        raise ErroDeDados(f"{arquivo}: {_lugar('sem_rodape')}: {sem_rodape!r} é também o nome de um rodapé")
    sobre_os_campos = {
        "expressao": _expressao_dos_campos(campos["abre"], campos["fecha"]) if campos else None,
        "nomes": set(valores) | set(CAMPOS_DA_PECA),
        "com_quebra": {nome for nome, valor in valores.items() if QUEBRA.search(valor)},
        "com_data": "formato_da_data" in dados,
        "no_git": no_repositorio(raiz),
    }
    rodapes = {nome: _le_rodape(arquivo, nome, rodape, tipos, sobre_os_campos)
               for nome, rodape in sorted(dados["rodapes"].items())}
    nao_documentos = {arquivo.resolve()} | {modelo.arquivo.resolve() for rodape in rodapes.values()
                                            for modelo in rodape.modelos.values()}
    return Rodapes(arquivo, raiz, tipos, rodapes, valores, dados.get("formato_da_data"), sem_rodape,
                   frozenset(nao_documentos))


# ---------------------------------------------------------------- o documento


def _tipo_do(rodapes, caminho):
    """O tipo do documento, ou None quando o arquivo não é um documento."""
    if Path(os.path.join(rodapes.raiz, caminho)).resolve() in rodapes.nao_documentos:
        return None
    tipos = [tipo for tipo in rodapes.tipos.values() if any(_pega(padrao, caminho) for padrao in tipo.arquivos)]
    if len(tipos) > 1:
        raise ErroDeDados(f"{caminho}: segue os padrões de dois tipos: {tipos[0].nome!r} e {tipos[1].nome!r}")
    return tipos[0] if tipos else None


def eh_documento(rodapes, caminho):
    """Se o arquivo, com o caminho a partir da pasta raiz, é um documento. Erro quando ele segue dois tipos."""
    return _tipo_do(rodapes, caminho) is not None


def _linhas(texto):
    """De cada linha: (o começo, o fim sem a quebra, o fim com a quebra)."""
    linhas, posicao = [], 0
    for quebra in QUEBRA.finditer(texto):
        linhas.append((posicao, quebra.start(), quebra.end()))
        posicao = quebra.end()
    if posicao < len(texto):
        linhas.append((posicao, len(texto), len(texto)))
    return tuple(linhas)


def _da_parte(analise, indice):
    """Os rodapés achados na parte, na ordem."""
    return [achado for achado in analise.achados if achado.parte == indice]


def _separador(analise):
    """O separador do tipo, com a quebra de linha do documento."""
    return QUEBRA.sub(analise.quebra, analise.tipo.separador)


def _numero(analise, posicao):
    """O número da linha em que fica a posição, contado a partir de 1."""
    return max(1, bisect.bisect_right([inicio for inicio, _, _ in analise.linhas], posicao))


def _partes(tipo, texto, linhas):
    """As partes do documento e onde começa o que fica depois da última."""
    def acha(expressao, ate):
        return [inicio for inicio, fim, _ in linhas if inicio < ate and expressao.search(texto[inicio:fim])]
    cauda = len(texto)
    if tipo.linha_de_fim is not None:
        cauda = (acha(tipo.linha_de_fim, cauda) or [cauda])[-1]
    secoes = acha(tipo.linha_de_secao, cauda) if tipo.linha_de_secao is not None else []
    inicios, fins = [0] + secoes, secoes + [cauda]
    partes = []
    for indice, (inicio, fim) in enumerate(zip(inicios, fins)):
        if indice == 0:
            capacidade = 0 if secoes else 1
        else:
            capacidade = 2 if indice == len(secoes) else 1
        partes.append(_Parte(inicio, fim, capacidade))
    return tuple(partes), cauda


def _por_lugar(rodapes_levados, caminho):
    por_lugar = {}
    for rodape in rodapes_levados:
        outro = por_lugar.setdefault(rodape.lugar, rodape)
        if outro.nome != rodape.nome:
            raise ErroDeDados(f"{caminho}: os rodapés {outro.nome!r} e {rodape.nome!r} são do mesmo lugar "
                              f"({rodape.lugar!r})")
    return por_lugar


def _escolhidos(rodapes, tipo, caminho, escolhas):
    nomes = [nome for _, nome in escolhas]
    if rodapes.sem_rodape is not None and rodapes.sem_rodape in nomes:
        outros = [(numero, nome) for numero, nome in escolhas if nome != rodapes.sem_rodape]
        if outros:
            raise ErroDeDados(f"{caminho}: linha {outros[0][0]}: {outros[0][1]!r} vem junto de "
                              f"{rodapes.sem_rodape!r}")
        return {}
    escolhidos = []
    for numero, nome in escolhas:
        rodape = rodapes.rodapes.get(nome)
        if rodape is None:
            raise ErroDeDados(f"{caminho}: linha {numero}: {nome!r} não é o nome de um rodapé")
        if tipo.nome not in rodape.modelos:
            raise ErroDeDados(f"{caminho}: linha {numero}: o rodapé {nome!r} não tem modelo para o tipo "
                              f"{tipo.nome!r}")
        escolhidos.append(rodape)
    return _por_lugar(escolhidos, caminho)


def _levados(rodapes, tipo, caminho, texto, linhas):
    """{lugar: rodapé} dos rodapés que o documento leva."""
    if tipo.linha_de_escolha is not None:
        escolhas = []
        for numero, (inicio, fim, _) in enumerate(linhas, 1):
            achado = tipo.linha_de_escolha.search(texto[inicio:fim])
            if achado:
                escolhas.append((numero, achado.group(NOME_ESCOLHIDO) or ""))
        if escolhas:
            return _escolhidos(rodapes, tipo, caminho, escolhas)
    cobrem = [rodape for _, rodape in sorted(rodapes.rodapes.items()) if tipo.nome in rodape.modelos
              and any(_pega(padrao, caminho) for padrao in rodape.documentos)
              and not any(_pega(padrao, caminho) for padrao in rodape.fora)]
    return _por_lugar(cobrem, caminho)


def _lugares_da_parte(partes, indice, levados):
    """Os lugares dos rodapés que o documento leva nesta parte, na ordem em que ficam."""
    secao, ultima = indice > 0, indice == len(partes) - 1
    return tuple(lugar for lugar in LUGARES if lugar in levados and (secao if lugar == SECAO else ultima))


def _lugares_com_marca(indice, total, quantos, lugares_da_parte):
    """Os lugares dos rodapés achados pela marca numa parte, na ordem."""
    if quantos == 0:
        return ()
    if indice == 0:
        return (FIM,)
    if indice < total - 1:
        return (SECAO,)
    if quantos == 2:
        return LUGARES
    return (FIM,) if lugares_da_parte == (FIM,) else (SECAO,)


def _achados_da_parte(indice, parte, inicios, lugares):
    fins = inicios[1:] + [parte.fim]
    return [_Achado(indice, lugar, inicio, fim) for lugar, inicio, fim in zip(lugares, inicios, fins)]


def _achados_com_marca(tipo, caminho, texto, linhas, partes, levados):
    marca, achados = tipo.marca.strip(), []
    for indice, parte in enumerate(partes):
        inicios = [inicio for inicio, fim, _ in linhas if parte.inicio <= inicio < parte.fim
                   and texto[inicio:fim].strip() == marca]
        if len(inicios) > parte.capacidade:
            numero = [inicio for inicio, _, _ in linhas].index(inicios[parte.capacidade]) + 1
            raise ErroDeDados(f"{caminho}: linha {numero}: mais linhas iguais à marca do que rodapés que cabem "
                              f"nesta parte")
        lugares = _lugares_com_marca(indice, len(partes), len(inicios),
                                     _lugares_da_parte(partes, indice, levados))
        achados += _achados_da_parte(indice, parte, inicios, lugares)
    return achados


def _acha_sem_marca(rodapes, tipo, lugar, texto, linhas, inicio, limite):
    """O começo do rodapé do lugar que termina a parte até o limite, ou None."""
    achadores = [rodape.modelos[tipo.nome].achador for _, rodape in sorted(rodapes.rodapes.items())
                 if rodape.lugar == lugar and tipo.nome in rodape.modelos]
    for comeco, _, _ in reversed(linhas):
        if comeco < inicio or comeco >= limite:
            continue
        if any(achador.match(texto, comeco, limite) for achador in achadores):
            return comeco
    return None


def _achados_sem_marca(rodapes, tipo, texto, linhas, partes, levados):
    achados = []
    for indice, parte in enumerate(partes):
        limite, inicios, lugares = parte.fim, [], []
        for lugar in reversed(_lugares_da_parte(partes, indice, levados)):
            comeco = _acha_sem_marca(rodapes, tipo, lugar, texto, linhas, parte.inicio, limite)
            if comeco is not None:
                inicios.insert(0, comeco)
                lugares.insert(0, lugar)
                limite = comeco
        achados += _achados_da_parte(indice, parte, inicios, lugares)
    return achados


def _analise(rodapes, caminho, texto):
    tipo = _tipo_do(rodapes, caminho)
    if tipo is None:
        raise ErroDeDados(f"{caminho}: não é um documento")
    linhas = _linhas(texto)
    partes, cauda = _partes(tipo, texto, linhas)
    levados = _levados(rodapes, tipo, caminho, texto, linhas)
    if tipo.marca is not None:
        achados = _achados_com_marca(tipo, caminho, texto, linhas, partes, levados)
    else:
        achados = _achados_sem_marca(rodapes, tipo, texto, linhas, partes, levados)
    primeira = QUEBRA.search(texto)
    quebra = primeira.group() if primeira else QUEBRA_DO_MODELO
    return _Analise(rodapes, caminho, texto, tipo, quebra, linhas, partes, cauda, levados, tuple(achados))


# ---------------------------------------------------------------- a data da última mudança


def _guardado(rodapes, chave, pergunta):
    if chave not in rodapes.git:
        rodapes.git[chave] = pergunta()
    return rodapes.git[chave]


def _git(rodapes, *palavras):
    return texto_do_comando([GIT, *palavras], rodapes.raiz)


def _resposta(rodapes, *palavras):
    resposta = _git(rodapes, *palavras)
    if resposta is None:
        raise ErroDeDados(f"{rodapes.raiz}: o git não respondeu a {' '.join(palavras[:2])!r}")
    return resposta


def _prefixo(rodapes):
    """O caminho da pasta raiz a partir da pasta de cima do repositório, com "/" no fim, ou vazio."""
    return _resposta(rodapes, "rev-parse", "--show-prefix").removesuffix(QUEBRA_DO_MODELO)


def _renomeados(rodapes):
    """{caminho novo: caminho no último commit} dos arquivos que mudaram de nome e ainda não entraram num commit."""
    pedacos = _resposta(rodapes, "status", "--porcelain=v2", "-z", "--untracked-files=no", "--renames").split("\0")
    renomeados, indice = {}, 0
    while indice < len(pedacos):
        if pedacos[indice].startswith(RENOMEADO):
            campos = pedacos[indice].split(" ", CAMPOS_DO_RENOMEADO)
            if campos[CAMPOS_DO_RENOMEADO - 1].startswith(TROCA_DE_NOME):
                renomeados[campos[CAMPOS_DO_RENOMEADO]] = pedacos[indice + 1]
            indice += 2
        else:
            indice += 1
    return renomeados


def _historico(rodapes, caminho):
    """De cada commit em que o arquivo mudou, do último ao primeiro, seguindo as trocas de nome:
    (o commit, a data dele, o caminho do arquivo nele)."""
    saida = _resposta(rodapes, "log", "--follow", "--first-parent", "-m", "--format=%x00%H%x00%cI", "--name-only",
                      "-z", "--", f":(top,literal){caminho}")
    pedacos = saida.split("\0")
    fora_da_forma = ErroDeDados(f"{rodapes.raiz}: o git respondeu ao histórico de {caminho!r} fora da forma esperada")
    if pedacos[0] or (len(pedacos) - 1) % 4:
        raise fora_da_forma
    historico = []
    for indice in range(1, len(pedacos) - 1, 4):
        commit, data, nome, vazio = pedacos[indice:indice + 4]
        if not nome.startswith(QUEBRA_DO_MODELO) or vazio:
            raise fora_da_forma
        historico.append((commit, datetime.datetime.fromisoformat(data), nome[len(QUEBRA_DO_MODELO):]))
    return historico


def _conteudos(analise):
    """O texto de cada parte, sem os rodapés, e o que fica depois da última, sem os espaços do fim. É o que conta
    como o texto do documento na data da última mudança."""
    conteudos = []
    for indice, parte in enumerate(analise.partes):
        da_parte = _da_parte(analise, indice)
        fim = da_parte[0].inicio if da_parte else parte.fim
        conteudos.append(QUEBRA.sub(QUEBRA_DO_MODELO, analise.texto[parte.inicio:fim]).rstrip())
    conteudos.append(QUEBRA.sub(QUEBRA_DO_MODELO, analise.texto[analise.cauda:]).rstrip())
    return tuple(conteudos)


def _conteudos_da_versao(rodapes, prefixo, caminho, texto):
    """Os conteúdos de uma versão do arquivo, guardada no git com o caminho a partir da pasta de cima do repositório.
    A versão que hoje não é documento, ou que hoje dá erro, conta pelo texto inteiro."""
    if texto is None:
        return None
    if caminho.startswith(prefixo):
        try:
            if _tipo_do(rodapes, caminho[len(prefixo):]) is not None:
                return _conteudos(_analise(rodapes, caminho[len(prefixo):], texto))
        except ErroDeDados:
            pass
    return (QUEBRA.sub(QUEBRA_DO_MODELO, texto).rstrip(),)


def _hoje(rodapes):
    return datetime.datetime.now().astimezone().strftime(rodapes.formato_da_data)


def _mudanca(analise):
    """A data da última mudança do texto do documento, sem os rodapés."""
    rodapes = analise.rodapes
    prefixo = _guardado(rodapes, "prefixo", lambda: _prefixo(rodapes))
    renomeados = _guardado(rodapes, "renomeados", lambda: _renomeados(rodapes))
    caminho = renomeados.get(prefixo + analise.caminho, prefixo + analise.caminho)

    def versao(commit, nome):
        return _conteudos_da_versao(rodapes, prefixo, nome, _git(rodapes, "show", f"{commit}:{nome}"))
    if versao(HEAD, caminho) != _conteudos(analise):
        return _hoje(rodapes)
    historico = _historico(rodapes, caminho)
    seguinte = versao(*historico[0][::2]) if historico else None
    for indice, (_, data, _) in enumerate(historico):
        esta = seguinte
        seguinte = versao(*historico[indice + 1][::2]) if indice + 1 < len(historico) else None
        if esta != seguinte:
            return data.strftime(rodapes.formato_da_data)
    return _hoje(rodapes)


# ---------------------------------------------------------------- a montagem


def _alvo_novo(link, pasta):
    relativo = os.path.relpath(link.destino, pasta).replace(os.sep, BARRA)
    if link.barra and not relativo.endswith(BARRA):
        relativo += BARRA
    return relativo + link.lugar


def _confere_links(analise, modelo, novos):
    """Cada link refeito tem de ser achado inteiro pela expressão dele, com o caminho novo no alvo."""
    trocas = [(link.alvo_inicio, link.alvo_fim, novo) for link, novo in zip(modelo.links, novos) if novo is not None]
    refeito, posicao = [], 0
    for inicio, fim, novo in trocas:
        refeito += [modelo.texto[posicao:inicio], novo]
        posicao = fim
    refeito = "".join(refeito + [modelo.texto[posicao:]])

    def nova(posicao_no_modelo):
        return posicao_no_modelo + sum(len(novo) - (fim - inicio) for inicio, fim, novo in trocas
                                       if fim <= posicao_no_modelo)
    for link, novo in zip(modelo.links, novos):
        achado = link.expressao.match(refeito, nova(link.inicio))
        if achado is None or achado.end() != nova(link.fim) or (novo is not None and achado.group(ALVO) != novo):
            raise ErroDeDados(f"{analise.caminho}: o link refeito de {modelo.arquivo} não é mais achado inteiro "
                              f"pela expressão {link.expressao.pattern!r}")


def _bloco(analise, rodape, valores, quebra, com_marca):
    """O rodapé montado para o documento, em pedaços: (texto, se é o valor do campo hoje)."""
    modelo = rodape.modelos[analise.tipo.nome]
    pasta = os.path.dirname(os.path.normpath(os.path.join(analise.rodapes.raiz, analise.caminho)))
    novos = [None if link.destino is None else _alvo_novo(link, pasta) for link in modelo.links]
    _confere_links(analise, modelo, novos)
    trocas = sorted([(link.alvo_inicio, link.alvo_fim, novo, False) for link, novo in zip(modelo.links, novos)
                     if novo is not None]
                    + [(campo.inicio, campo.fim, valores[campo.nome], campo.nome == HOJE) for campo in modelo.campos])
    pedacos, posicao = [], 0
    for inicio, fim, valor, eh_hoje in trocas:
        pedacos += [(modelo.texto[posicao:inicio], False), (valor, eh_hoje)]
        posicao = fim
    pedacos.append((modelo.texto[posicao:], False))
    if com_marca and analise.tipo.marca is not None:
        pedacos.insert(0, (analise.tipo.marca + QUEBRA_DO_MODELO, False))
    return [(QUEBRA.sub(quebra, texto), eh_hoje) for texto, eh_hoje in pedacos if texto]


def _blocos(analise, quebra, com_marca):
    """{lugar: rodapé montado} dos rodapés que o documento leva."""
    valores = dict(analise.rodapes.valores)
    valores[CAMINHO] = analise.caminho
    valores[NOME] = analise.caminho.rsplit(BARRA, 1)[-1]
    precisa = {campo.nome for rodape in analise.levados.values() for campo in rodape.modelos[analise.tipo.nome].campos}
    if HOJE in precisa:
        valores[HOJE] = _hoje(analise.rodapes)
    if MUDANCA in precisa:
        valores[MUDANCA] = _mudanca(analise)
    return {lugar: _bloco(analise, rodape, valores, quebra, com_marca) for lugar, rodape in analise.levados.items()}


def _tem_seguinte(analise, indice):
    return indice < len(analise.partes) - 1 or analise.cauda < len(analise.texto)


def _documento_montado(analise, blocos):
    """O documento, em pedaços, com os blocos nos lugares deles e sem os rodapés achados."""
    texto, pedacos, mexeu = analise.texto, [], False
    separador = _separador(analise)
    for indice, parte in enumerate(analise.partes):
        da_parte = _da_parte(analise, indice)
        postos = [blocos[lugar] for lugar in _lugares_da_parte(analise.partes, indice, analise.levados)
                  if lugar in blocos]
        if not da_parte and not postos:
            pedacos.append((texto[parte.inicio:parte.fim], False))
            continue
        mexeu = True
        conteudo = texto[parte.inicio:da_parte[0].inicio if da_parte else parte.fim].rstrip()
        feito = [(conteudo, False)] if conteudo else []
        for bloco in postos:
            if feito:
                feito.append((separador, False))
            feito += bloco
        if feito:
            feito.append((separador if _tem_seguinte(analise, indice) else analise.quebra, False))
        pedacos += feito
    pedacos.append((texto[analise.cauda:], False))
    junto = _texto_de(pedacos)
    if mexeu and junto and not QUEBRA.fullmatch(junto[-1]):
        pedacos.append((analise.quebra, False))
    return pedacos


def _texto_de(pedacos):
    return "".join(texto for texto, _ in pedacos)


def _eh_data(texto, formato):
    try:
        return datetime.datetime.strptime(texto, formato).strftime(formato) == texto
    except ValueError:
        return False


def _bate(pedacos, real, formato):
    """Se o texto real é o dos pedaços, com qualquer data escrita no formato no lugar do valor do campo hoje."""
    if not any(eh_hoje for _, eh_hoje in pedacos):
        return _texto_de(pedacos) == real
    expressao = "".join(f"({QUALQUER_LINHA})" if eh_hoje else re.escape(texto) for texto, eh_hoje in pedacos)
    achado = re.fullmatch(expressao, real)
    return achado is not None and all(_eh_data(data, formato) for data in achado.groups())


# ---------------------------------------------------------------- os pedidos


def com_rodapes(rodapes, caminho, texto):
    """O texto do documento com cada rodapé que ele leva no lugar e sem os que ele não leva mais."""
    analise = _analise(rodapes, caminho, texto)
    return _texto_de(_documento_montado(analise, _blocos(analise, analise.quebra, True)))


def _ultima_linha_com_texto(analise, parte):
    for inicio, fim, _ in reversed(analise.linhas):
        if parte.inicio <= inicio < parte.fim and analise.texto[inicio:fim].strip():
            return _numero(analise, inicio)
    return _numero(analise, parte.inicio)


def _no_jeito(analise, achado, da_parte, bloco):
    """Se o rodapé achado é o do bloco, no jeito certo: com o separador antes e o que deve vir depois dele."""
    parte, texto = analise.partes[achado.parte], analise.texto
    separador = _separador(analise)
    if achado is da_parte[0]:
        antes = parte.inicio + len(texto[parte.inicio:achado.inicio].rstrip())
        if texto[antes:achado.inicio] != (separador if antes > parte.inicio else ""):
            return False
    ultimo = achado is da_parte[-1]
    depois = separador if not ultimo or _tem_seguinte(analise, achado.parte) else analise.quebra
    return _bate(bloco + [(depois, False)], texto[achado.inicio:achado.fim], analise.rodapes.formato_da_data)


def problemas(rodapes, caminho, texto):
    """Os rodapés do documento fora do dia, em ordem de linha: (lugar, linha, motivo). Vazia quando está em dia."""
    analise = _analise(rodapes, caminho, texto)
    blocos = _blocos(analise, analise.quebra, True)
    fora_do_dia = []
    for indice, parte in enumerate(analise.partes):
        lugares = _lugares_da_parte(analise.partes, indice, analise.levados)
        da_parte = _da_parte(analise, indice)
        por_lugar = {achado.lugar: achado for achado in da_parte}
        for lugar in LUGARES:
            achado = por_lugar.get(lugar)
            if achado is None and lugar in lugares:
                fora_do_dia.append(Problema(lugar, _ultima_linha_com_texto(analise, parte), FALTA))
            elif achado is not None and lugar not in lugares:
                fora_do_dia.append(Problema(lugar, _numero(analise, achado.inicio), SOBRA))
            elif achado is not None and not _no_jeito(analise, achado, da_parte, blocos[lugar]):
                fora_do_dia.append(Problema(lugar, _numero(analise, achado.inicio), DIFERENTE))
    if not fora_do_dia and not _bate(_documento_montado(analise, blocos), texto, rodapes.formato_da_data):
        ultimo = analise.achados[-1]
        fora_do_dia.append(Problema(ultimo.lugar, _numero(analise, ultimo.inicio), DIFERENTE))
    return sorted(fora_do_dia, key=lambda problema: (problema.linha, LUGARES.index(problema.lugar)))


def rodapes_montados(rodapes, caminho, texto):
    """{lugar: texto} de cada rodapé que o documento leva, montado para ele, sem a linha da marca."""
    analise = _analise(rodapes, caminho, texto)
    blocos = _blocos(analise, QUEBRA_DO_MODELO, False)
    return {lugar: _texto_de(blocos[lugar]) for lugar in LUGARES if lugar in blocos}


def separa(rodapes, caminho, texto):
    """(o texto sem os rodapés que o documento tem, [(lugar, primeira linha, última linha)] de cada rodapé)."""
    analise = _analise(rodapes, caminho, texto)
    trechos = []
    for achado in analise.achados:
        ultimo = achado.inicio + len(analise.texto[achado.inicio:achado.fim].rstrip()) - 1
        trechos.append(Trecho(achado.lugar, _numero(analise, achado.inicio), _numero(analise, ultimo)))
    return _texto_de(_documento_montado(analise, {})), trechos
