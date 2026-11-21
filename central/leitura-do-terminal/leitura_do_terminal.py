"""
Lê uma linha do terminal como o terminal lê, para a peça que precisa saber o que ela roda.

Separa a linha em palavras e sinais, com as aspas, a barra que protege um caractere e os
comentários; junta as palavras de cada comando, sem o arquivo para onde ele manda a saída ou
de onde ele lê; acha as palavras que rodam como comando; acha um comando de uma ou mais
palavras; e diz se uma opção aparece numa palavra. Lê também os comandos de dentro de $( ) e
de crases. A linha com aspa, crase ou $( sem fechar dá ComandoIlegivel.

Lê ainda, como uma linha, o texto que vai para um comando que roda o texto que recebe.

Os prefixos, as palavras depois das quais as outras também rodam como comando, e os comandos
que rodam o texto que recebem vêm da configuração, lida pelo molde em
esquemas/leitura-do-terminal.schema.json.

Dá às peças: lidos, configuracao_do_terminal, posicoes_de_comando, depois_do_comando,
comandos_achados, opcao_bate, eh_redirecionamento, ComandoIlegivel e os sinais do terminal,
com nome, logo abaixo.
"""
import re
from collections import namedtuple
from pathlib import Path

from conferencia_de_molde import le_conferido

MOLDE = Path(__file__).resolve().parent / "esquemas" / "leitura-do-terminal.schema.json"

# Os sinais do terminal.
ESCRITA = ">"  # manda a saída para um arquivo
LEITURA = "<"  # lê de um arquivo
TEXTO_EMBUTIDO = "<<"  # traz, nas linhas seguintes, um texto para o comando ler
ABRE = "("  # abre um grupo de comandos
FECHA = ")"  # fecha um grupo de comandos
DUPLICACAO = "&"  # depois de > ou de <, aponta para outra saída ou entrada, pelo número dela
FECHA_DESCRITOR = "-"  # depois de >& ou de <&, fecha a saída ou a entrada
TROCA = "$"  # começa o que o terminal troca por outra coisa
SUBSTITUICAO = TROCA + ABRE  # abre um comando de dentro, que o terminal troca pelo que ele escreve
CRASE = "`"  # abre e fecha um comando de dentro
ASPA_SIMPLES = "'"  # abre e fecha um texto que fica como está
ASPA_DUPLA = '"'  # abre e fecha um texto em que o terminal ainda troca o que começa por $ ou crase
ESCAPE = "\\"  # a barra que protege o caractere seguinte
COMENTARIO = "#"  # no começo de uma palavra, abre um comentário, que vai até o fim da linha
QUEBRA = "\n"  # a quebra de linha
ATRIBUICAO = "="  # separa um nome do valor dele
OPCAO = "-"  # começa uma opção curta
OPCAO_LONGA = "--"  # começa uma opção longa

# Os sinais que juntam comandos e os que mandam a saída para um arquivo ou leem de um, os mais compridos primeiro:
# na linha, vale o mais comprido que couber.
_SINAIS = sorted("&& || ; ;; ;& ;;& & | |& ( ) <( >( > >> >| >& &> &>> < << <<< <& <>".split() + [QUEBRA],
                 key=lambda sinal: (-len(sinal), sinal))
_COMECOS = frozenset(sinal[0] for sinal in _SINAIS)  # os caracteres que começam um sinal
# os caracteres que a barra protege entre aspas duplas; antes de outro caractere, ela é só uma barra
_PROTEGIDOS_ENTRE_ASPAS = frozenset((TROCA, CRASE, ASPA_DUPLA, ESCAPE, QUEBRA))
# o que, colado antes de um sinal que manda a saída para um arquivo ou lê de um, é do sinal: o número da saída ou
# da entrada, ou o nome que a guarda, entre chaves
_DESCRITOR = re.compile(r"\d+|\{[^\W\d]\w*\}")
# o começo de uma atribuição: o nome, também com um índice entre colchetes e com o + de quem acrescenta
_ATRIBUICAO = re.compile(r"[^\W\d]\w*(\[[^\]]*\])?\+?" + re.escape(ATRIBUICAO))

# A configuração lida: os prefixos e os comandos que rodam o texto que recebem.
Terminal = namedtuple("Terminal", "prefixos rodam_texto")


class ComandoIlegivel(ValueError):
    """A linha que não se lê, por ter aspa, crase ou $( sem fechar; a mensagem é o sinal que ficou aberto."""


def _fim_do_par(linha, inicio, sinal):
    """A posição do sinal que fecha o par aberto logo antes de inicio; ComandoIlegivel quando ele não fecha."""
    fim = linha.find(sinal, inicio)
    if fim < 0:
        raise ComandoIlegivel(sinal)
    return fim


def _le_substituicao(linha, inicio):
    """De inicio, logo depois de $(, até o ) que fecha: (a posição seguinte, o comando de dentro)."""
    nivel, i = 1, inicio
    while i < len(linha):
        c = linha[i]
        if c == ESCAPE:
            i += 2
        elif c == ASPA_SIMPLES:
            i = _fim_do_par(linha, i + 1, ASPA_SIMPLES) + 1
        elif c == ASPA_DUPLA:
            i, _, _ = _le_aspas_duplas(linha, i + 1)
        elif c == ABRE:
            nivel, i = nivel + 1, i + 1
        elif c == FECHA:
            nivel -= 1
            if nivel == 0:
                return i + 1, linha[inicio:i]
            i += 1
        else:
            i += 1
    raise ComandoIlegivel(SUBSTITUICAO)


def _le_aspas_duplas(linha, inicio):
    """De inicio, logo depois da aspa, até a aspa que fecha: (a posição seguinte, o texto, os comandos de dentro).
    O comando de dentro fica no texto como está escrito."""
    texto, de_dentro, i = [], [], inicio
    while i < len(linha):
        c = linha[i]
        if c == ASPA_DUPLA:
            return i + 1, "".join(texto), de_dentro
        if c == ESCAPE and linha[i + 1:i + 2] in _PROTEGIDOS_ENTRE_ASPAS:
            if linha[i + 1] != QUEBRA:  # a barra antes da quebra de linha junta as duas linhas
                texto.append(linha[i + 1])
            i += 2
        elif linha.startswith(SUBSTITUICAO, i):
            fim, dentro = _le_substituicao(linha, i + len(SUBSTITUICAO))
            de_dentro.append(dentro)
            texto.append(linha[i:fim])
            i = fim
        elif c == CRASE:
            fim = _fim_do_par(linha, i + 1, CRASE)
            de_dentro.append(linha[i + 1:fim])
            texto.append(linha[i:fim + 1])
            i = fim + 1
        else:
            texto.append(c)
            i += 1
    raise ComandoIlegivel(ASPA_DUPLA)


def eh_redirecionamento(sinal):
    """Se o sinal manda a saída para um arquivo ou lê de um arquivo."""
    return (ESCRITA in sinal or LEITURA in sinal) and ABRE not in sinal


def _separar(linha):
    """(partes, comandos de dentro) da linha: cada parte é (texto, se é sinal), e só há sinal fora de aspas; os
    comandos de dentro são os de $( ) e de crases, também entre aspas, e cada um fica na palavra dele como está
    escrito. O que vem colado antes de um sinal que manda a saída para um arquivo, ou lê de um, e é do sinal
    (_DESCRITOR) não é uma palavra."""
    partes, de_dentro = [], []
    palavra, crua, i = None, True, 0  # os pedaços da palavra aberta (None sem ela) e se ela não tem aspa nem barra

    def fecha(vale=True):
        nonlocal palavra, crua
        if palavra is not None and vale:
            partes.append(("".join(palavra), False))
        palavra, crua = None, True

    while i < len(linha):
        c = linha[i]
        if c in _COMECOS:
            sinal = next(s for s in _SINAIS if linha.startswith(s, i))
            do_sinal = (palavra is not None and crua and eh_redirecionamento(sinal)
                        and _DESCRITOR.fullmatch("".join(palavra)) is not None)
            fecha(vale=not do_sinal)
            partes.append((sinal, True))
            i += len(sinal)
        elif c.isspace():
            fecha()
            i += 1
        elif c == ESCAPE and linha.startswith(QUEBRA, i + 1):
            i += 2  # a barra antes da quebra de linha junta as duas linhas
        elif c == COMENTARIO and palavra is None:
            fim = linha.find(QUEBRA, i)
            i = len(linha) if fim < 0 else fim
        else:
            palavra = [] if palavra is None else palavra
            if c == ESCAPE:
                palavra.append(linha[i + 1:i + 2])
                crua, i = False, i + 2
            elif c == ASPA_SIMPLES:
                fim = _fim_do_par(linha, i + 1, ASPA_SIMPLES)
                palavra.append(linha[i + 1:fim])
                crua, i = False, fim + 1
            elif c == ASPA_DUPLA:
                i, texto, novos = _le_aspas_duplas(linha, i + 1)
                palavra.append(texto)
                de_dentro.extend(novos)
                crua = False
            elif c == CRASE:
                fim = _fim_do_par(linha, i + 1, CRASE)
                de_dentro.append(linha[i + 1:fim])
                palavra.append(linha[i:fim + 1])
                crua, i = False, fim + 1
            elif linha.startswith(SUBSTITUICAO, i):
                fim, dentro = _le_substituicao(linha, i + len(SUBSTITUICAO))
                de_dentro.append(dentro)
                palavra.append(linha[i:fim])
                crua, i = False, fim
            else:
                palavra.append(c)
                i += 1
    fecha()
    return partes, de_dentro


def _comandos_simples(partes):
    """As palavras de cada comando da linha, sem os sinais e sem o arquivo para onde o comando manda a saída ou de
    onde ele lê."""
    palavras, pula = [], False
    for texto, eh_sinal in partes:
        if not eh_sinal:
            if not pula:
                palavras.append(texto)
            pula = False
        elif eh_redirecionamento(texto):
            pula = True
        else:
            if palavras:
                yield palavras
            palavras, pula = [], False
    if palavras:
        yield palavras


def _primeiro(palavras, nomes):
    """A posição da primeira palavra cujo nome, sem o caminho, é um dos nomes; None quando não há."""
    return next((numero for numero, palavra in enumerate(palavras) if Path(palavra).name in nomes), None)


def lidos(comando, rodam_texto=frozenset()):
    """(partes, [as palavras de cada comando]) da linha; depois, de cada comando de dentro dela, na ordem, cada um
    seguido dos de dentro dele; e, por fim, de cada texto que um comando da linha roda: a palavra que vem depois
    de um dos comandos de rodam_texto e que, lida como uma linha, é mais que ela mesma. ComandoIlegivel quando um
    deles não se lê."""
    partes, de_dentro = _separar(comando)
    simples = list(_comandos_simples(partes))
    yield partes, simples
    for dentro in de_dentro:
        yield from lidos(dentro, rodam_texto)
    for palavras in simples:
        roda = _primeiro(palavras, rodam_texto)
        for palavra in ([] if roda is None else palavras[roda + 1:]):
            lido = list(lidos(palavra, rodam_texto))
            if len(lido) > 1 or lido[0][0] != [(palavra, False)]:
                yield from lido


def configuracao_do_terminal(arquivo):
    """A configuração (Terminal), lida pelo molde dela: os prefixos, as palavras depois das quais as outras também
    rodam como comando, e os comandos que rodam o texto que recebem. Erro (ErroDeDados) que diz o arquivo e o
    lugar de cada valor fora do molde."""
    dados = le_conferido(Path(arquivo), MOLDE)
    return Terminal(frozenset(dados["prefixos"]), frozenset(dados["rodam_texto"]))


def _pode_sumir(palavra):
    """Se o terminal troca a palavra, ou parte dela, por outra coisa, que pode ser nada."""
    return TROCA in palavra or CRASE in palavra


def posicoes_de_comando(palavras, prefixos):
    """As posições das palavras que rodam como comando: a primeira, menos uma atribuição; a que vem depois de uma
    que pode sumir; e toda palavra depois de um prefixo, pelo nome dele, sem o caminho."""
    prefixo, posicoes, comeco = _primeiro(palavras, prefixos), [], True
    for numero, palavra in enumerate(palavras):
        if comeco and _ATRIBUICAO.match(palavra):
            continue
        if comeco or (prefixo is not None and numero > prefixo):
            posicoes.append(numero)
        comeco = comeco and _pode_sumir(palavra)
    return posicoes


def depois_do_comando(comando, palavras):
    """As palavras depois do comando, de uma ou mais palavras, quando as palavras começam por ele: a primeira pelo
    nome, sem o caminho, e as outras na ordem, com outras palavras no meio; None quando não começam."""
    if not palavras or Path(palavras[0]).name != comando[0]:
        return None
    resto = palavras[1:]
    for esperada in comando[1:]:
        if esperada not in resto:
            return None
        resto = resto[resto.index(esperada) + 1:]
    return resto


def comandos_achados(comando, procurados, terminal):
    """(índice, seguintes, trecho) de cada vez que a linha, um comando de dentro dela ou um texto que ela manda
    rodar roda um dos procurados (cada um, a lista das palavras dele, uma ou mais), na ordem: o índice do procurado
    na lista, as palavras depois dele e o trecho do comando da palavra dele em diante. O terminal é a configuração
    lida (Terminal); depois de um comando que roda o texto que recebe, as palavras também rodam como comando.
    ComandoIlegivel quando um comando não se lê."""
    prefixos = terminal.prefixos | terminal.rodam_texto
    for _, simples in lidos(comando, terminal.rodam_texto):
        for palavras in simples:
            for posicao in posicoes_de_comando(palavras, prefixos):
                for indice, procurado in enumerate(procurados):
                    seguintes = depois_do_comando(procurado, palavras[posicao:])
                    if seguintes is not None:
                        yield indice, seguintes, " ".join(palavras[posicao:])


def _letras_iniciais(texto):
    """As letras do começo do texto, até o primeiro caractere que não é letra."""
    fim = 0
    while fim < len(texto) and texto[fim].isalpha():
        fim += 1
    return texto[:fim]


def opcao_bate(opcao, palavra):
    """Se a opção aparece na palavra: igual a ela; a longa, também com um valor depois de "="; e a curta, de uma
    letra só, também junto de outras curtas, entre as letras do começo da palavra."""
    if palavra == opcao:
        return True
    if opcao.startswith(OPCAO_LONGA):
        return palavra.startswith(opcao + ATRIBUICAO)
    curta = len(opcao) == len(OPCAO) + 1 and opcao.startswith(OPCAO)
    agrupada = palavra.startswith(OPCAO) and not palavra.startswith(OPCAO_LONGA)
    return curta and agrupada and opcao[len(OPCAO):] in _letras_iniciais(palavra[len(OPCAO):])
