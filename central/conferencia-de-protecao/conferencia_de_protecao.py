"""
Confere se o computador está impedindo a IA de alterar os arquivos das peças que ficam de olho nela.

Lê a lista do que fica fechado para a IA e testa cada item dela com o usuário da IA, por tentativas que não
alteram nada: abrir o arquivo para escrever, criar e apagar um arquivo nas pastas em que ele está, pedir para o
caminho os direitos que ele já tem e pedir para rodar como administrador sem digitar senha. A tentativa que o
computador aceita é um achado; a que ele recusa por direitos é a prova de que aquilo está fechado; a que não
chega a ser feita entra como achado indeterminado, porque na dúvida aquilo conta como aberto.

As tentativas rodam num programa à parte, o tentativas.py, que o desprotegidos roda com o usuário da IA pelo
pedido de outro usuário. Antes, o desprotegidos confere se está rodando com o usuário do programa.

Dá às peças: le_fechados, desprotegidos, pedido_para e achados_da_lista. Dá ao tentativas.py: achados_daqui, CAMINHOS
e PEDIDO.

Todo erro é um ErroDeDados.
"""
import errno
import json
import os
import stat
import sys
import tempfile
from collections import namedtuple
from functools import partial
from pathlib import Path

try:
    import pwd  # o cadastro dos usuários, nos sistemas que o têm
except ImportError:
    pwd = None

from conferencia_de_molde import le_conferido
from erro_de_dados import ErroDeDados
from leitura_de_json import de_json
from modelo_de_texto import campos, preenche
from repetidos import repetidos
from resultado_de_comando import NAO_PASSOU, PASSOU, resultado

PECA = Path(__file__).resolve().parent  # a pasta desta peça
MOLDE = PECA / "esquemas" / "conferencia-de-protecao.schema.json"  # o molde da lista
TENTATIVAS = PECA / "tentativas.py"  # o programa à parte que faz as tentativas
RODA = PECA.parent / "roda" / "roda.py"  # o roda.py, na pasta vizinha desta, como diz o README do roda
FECHADOS = "fechados"  # na lista, a chave dos caminhos que ficam fechados para a IA
PEDIDO = "pedido_de_administrador"  # na lista e no pedido ao tentativas.py, a chave do pedido de administrador
USUARIO_DA_IA = "usuario_da_ia"  # na lista, a chave do nome do usuário da IA
USUARIO_DO_PROGRAMA = "usuario_do_programa"  # na lista, a chave do nome do usuário do programa
PEDIDO_DE_OUTRO = "pedido_de_outro_usuario"  # na lista, a chave do pedido para rodar com outro usuário
LUGAR_DO_USUARIO = "usuario"  # o nome do lugar marcado do pedido de outro usuário
CAMINHOS = "caminhos"  # no pedido ao tentativas.py, a chave dos caminhos
ESCRITA = "escrita"  # o tipo do achado de abrir o arquivo para escrever
PASTA = "pasta"  # o tipo do achado de criar e apagar um arquivo numa pasta
DIREITOS = "direitos"  # o tipo do achado de mudar os direitos do caminho para os mesmos que ele já tinha
ADMINISTRADOR = "administrador"  # o tipo do achado de rodar como administrador sem senha
INDETERMINADO = "indeterminado"  # o tipo do achado da tentativa que não chegou a ser feita
OUTRO_USUARIO = "outro_usuario"  # o tipo do achado de quando esta peça roda com outro usuário que não o do programa
DAS_TENTATIVAS = frozenset({ESCRITA, PASTA, DIREITOS, ADMINISTRADOR, INDETERMINADO})  # o que o tentativas.py entrega
RECUSAS = frozenset({errno.EACCES, errno.EPERM, errno.EROFS})  # com que motivos o computador recusa por direitos
SEM_ESPERAR = getattr(os, "O_NONBLOCK", 0)  # abrir sem ficar à espera, onde o sistema tem esse jeito de abrir
ENTRE_CAMINHO_E_TIPO = ": "  # o que separa o caminho do tipo, na linha de um achado do achados_da_lista
ACEITOU = "aceitou"  # a tentativa que o computador deixou passar
RECUSOU = "recusou"  # a tentativa que o computador recusou por direitos
NAO_DEU = "nao_deu"  # a tentativa que não chegou a ser feita

# O que a lista guarda: os caminhos que ficam fechados para a IA, as palavras do pedido de administrador, os nomes
# do usuário da IA e do usuário do programa e as palavras do pedido de outro usuário.
Lista = namedtuple("Lista", "caminhos pedido_de_administrador usuario_da_ia usuario_do_programa "
                            "pedido_de_outro_usuario")

# Um achado: o caminho em que o computador aceitou a tentativa (nenhum, quando não é de um arquivo) e o tipo dela.
Achado = namedtuple("Achado", "caminho tipo")

# Um lugar a testar: o caminho dele; se ele é um atalho e se é uma pasta, que são o que decide as tentativas que
# valem nele; e se ele se deixou olhar por dentro, que só é falso na pasta que não se lê.
Lugar = namedtuple("Lugar", "caminho atalho pasta olhado")


def _abre_para_escrever(caminho):
    """Abre o arquivo para escrever e fecha logo depois. Não pede para esvaziar o arquivo, que é o que o jeito
    comum de abrir para escrever faria, nem fica à espera de quem leia o que ele tem a dizer."""
    os.close(os.open(caminho, os.O_WRONLY | SEM_ESPERAR))


def _cria_e_apaga(pasta):
    """Cria um arquivo na pasta, com um nome que o próprio sistema dá e que ainda não existe ali, e o apaga logo
    depois. O nome não aparece na resposta, e por isso não muda o que a peça entrega."""
    descritor, arquivo = tempfile.mkstemp(dir=pasta)
    try:
        os.close(descritor)
    finally:
        os.unlink(arquivo)


def _pede_os_mesmos_direitos(caminho, segue_o_atalho):
    """Pede, para o caminho, os direitos que ele tem agora, para nada mudar nem quando o computador aceita. O
    segue_o_atalho diz se os direitos são os do arquivo apontado ou os do próprio atalho."""
    direitos = stat.S_IMODE(os.stat(caminho, follow_symlinks=segue_o_atalho).st_mode)
    os.chmod(caminho, direitos, follow_symlinks=segue_o_atalho)


def _fim_da_tentativa(tentativa):
    """Como uma tentativa acabou: RECUSOU quando o computador a negou por direitos, NAO_DEU quando ela não chegou
    a ser feita, por um motivo que não tem a ver com direitos, e ACEITOU quando ela passou."""
    try:
        tentativa()
    except OSError as erro:
        return RECUSOU if erro.errno in RECUSAS else NAO_DEU
    return ACEITOU


def _primeiro_que_existe(caminho):
    """O caminho, quando ele existe, ou a primeira pasta acima dele que existe. O que ainda não existe se testa na
    pasta em que vai aparecer, porque é ali que a IA criaria um arquivo com o nome que a peça usa."""
    while not os.path.lexists(caminho) and caminho.parent != caminho:
        caminho = caminho.parent
    return caminho


def _dentro(pasta):
    """O que está dentro da pasta, em ordem, ou None quando ela não se deixa olhar por dentro."""
    try:
        return sorted(pasta.iterdir())
    except OSError:
        return None


def _apontado(atalho):
    """O caminho que o atalho aponta, escrito desde o início do disco. O atalho que aponta para outro atalho leva
    ao seguinte, um por vez, porque cada um deles é um lugar em que a IA desviaria a leitura."""
    return Path(os.path.normpath(atalho.parent / atalho.readlink()))


def _lugares(item, vistos):
    """Os lugares que um item da lista manda testar, em ordem: ele mesmo, ou a primeira pasta acima que existe; o
    que ele aponta, quando é um atalho; e cada arquivo e cada pasta de dentro, quando é uma pasta. O lugar já
    visto não volta, o que também fecha a volta do atalho que leva a si mesmo. A volta se dá por uma fila, e não
    por chamadas uma dentro da outra, para a pasta muito funda e a fila comprida de atalhos não pararem a peça."""
    por_ver = [Path(item)]
    while por_ver:
        lugar = _primeiro_que_existe(por_ver.pop(0))
        if lugar in vistos:
            continue
        vistos.add(lugar)
        atalho = lugar.is_symlink()
        pasta = not atalho and lugar.is_dir()
        if atalho:
            yield Lugar(lugar, True, False, True)
            por_ver.insert(0, _apontado(lugar))
        elif not pasta:
            yield Lugar(lugar, False, False, True)
        else:
            dentro = _dentro(lugar)
            yield Lugar(lugar, False, True, dentro is not None)
            por_ver[:0] = dentro or ()


def _tentativas(lugar, pastas_testadas):
    """(achado, tentativa) de cada tentativa que vale para um lugar, na ordem em que o README as põe: a de
    escrever, as de criar e apagar e a de mudar os direitos. A pasta e o atalho não guardam conteúdo para abrir, e
    o atalho só tem direitos próprios onde o sistema deixa mudá-los. A pasta em que já se criou e apagou um
    arquivo não volta, porque a resposta dela seria a mesma."""
    caminho = lugar.caminho
    if not lugar.atalho and not lugar.pasta:
        yield Achado(str(caminho), ESCRITA), partial(_abre_para_escrever, caminho)
    for onde in ([caminho] if lugar.pasta else []) + list(caminho.parents):
        if onde not in pastas_testadas:
            pastas_testadas.add(onde)
            yield Achado(str(onde), PASTA), partial(_cria_e_apaga, onde)
    if not lugar.atalho or os.chmod in os.supports_follow_symlinks:
        yield Achado(str(caminho), DIREITOS), partial(_pede_os_mesmos_direitos, caminho, not lugar.atalho)


def _achados_do_lugar(lugar, pastas_testadas):
    """Os achados de um lugar: a tentativa que o computador aceitou entra com o tipo dela, e a que não chegou a
    ser feita entra como indeterminada. A pasta que não se deixou olhar por dentro também entra como
    indeterminada, porque o que está dentro dela não se testou."""
    achados = []
    for achado, tentativa in _tentativas(lugar, pastas_testadas):
        fim = _fim_da_tentativa(tentativa)
        if fim == ACEITOU:
            achados.append(achado)
        elif fim == NAO_DEU:
            achados.append(Achado(achado.caminho, INDETERMINADO))
    if not lugar.olhado:
        achados.append(Achado(str(lugar.caminho), INDETERMINADO))
    return achados


def _achados_do_administrador(pedido_de_administrador):
    """O achado do pedido de administrador: o que o computador aceitou entra como achado; o que ele recusou não
    entra; e o que não chegou a ser feito entra como indeterminado. Só conta como ele ter acabado, e não o que ele
    escreveu, que muda de programa para programa e de idioma para idioma."""
    try:
        fim = resultado(pedido_de_administrador, Path.cwd()).fim
    except (ErroDeDados, OSError):
        return [Achado(None, INDETERMINADO)]
    if fim == PASSOU:
        return [Achado(None, ADMINISTRADOR)]
    return [] if fim == NAO_PASSOU else [Achado(None, INDETERMINADO)]


def achados_daqui(caminhos, pedido_de_administrador):
    """Os achados dos caminhos, na ordem deles, com o do pedido de administrador por último, pelas tentativas
    feitas com o usuário com que este código roda. É o que o tentativas.py faz com o usuário da IA."""
    achados, vistos, pastas_testadas = [], set(), set()
    for caminho in caminhos:
        for lugar in _lugares(caminho, vistos):
            achados += _achados_do_lugar(lugar, pastas_testadas)
    return achados + _achados_do_administrador(pedido_de_administrador)


def _confere_usuarios(usuario_da_ia, usuario_do_programa, pedido_de_outro_usuario, origem):
    """Erro (ErroDeDados) quando um dos dois nomes de usuário é vazio, quando os dois são iguais e quando o pedido
    de outro usuário não traz o lugar marcado do nome do usuário em nenhuma palavra ou traz outro lugar marcado. A
    origem, quando há, abre a mensagem do erro."""
    if not usuario_da_ia or not usuario_do_programa:
        raise ErroDeDados(f"{origem}nome de usuário vazio")
    if usuario_da_ia == usuario_do_programa:
        raise ErroDeDados(f"{origem}o usuário da IA e o do programa têm o mesmo nome: {usuario_da_ia}")
    lugares = {lugar for palavra in pedido_de_outro_usuario for lugar in campos(palavra)}
    if lugares != {LUGAR_DO_USUARIO}:
        raise ErroDeDados(f"{origem}o pedido de outro usuário tem de marcar só o lugar "
                          f"{{{LUGAR_DO_USUARIO}}}: {list(pedido_de_outro_usuario)}")


def pedido_para(pedido_de_outro_usuario, usuario):
    """As palavras do pedido de outro usuário, na mesma ordem, com o nome do usuário no lugar marcado: o pedido para
    rodar um comando com esse usuário."""
    return [preenche(palavra, {LUGAR_DO_USUARIO: usuario}) for palavra in pedido_de_outro_usuario]


def _usuario_atual():
    """O nome do usuário com que esta peça roda, pelo cadastro do sistema, ou None onde o sistema não o tem."""
    if pwd is None:
        return None
    try:
        return pwd.getpwuid(os.geteuid()).pw_name
    except KeyError:
        return None


def _sem_resposta(caminhos):
    """O que entra quando o pedido de outro usuário não consegue rodar as tentativas: cada caminho recebido como
    indeterminado, e a tentativa de virar administrador também."""
    return [Achado(caminho, INDETERMINADO) for caminho in caminhos] + [Achado(None, INDETERMINADO)]


def _achado_da_saida(item):
    """O Achado de um item que o tentativas.py escreveu, ou None quando o item não tem a forma combinada: um par
    com o caminho, ou nada, e um dos tipos das tentativas."""
    if not isinstance(item, list) or len(item) != 2:
        return None
    caminho, tipo = item
    if not (caminho is None or isinstance(caminho, str)) or not isinstance(tipo, str) or tipo not in DAS_TENTATIVAS:
        return None
    return Achado(caminho, tipo)


def _achados_da_saida(saida):
    """Os achados que o tentativas.py escreveu, ou None quando a saída não tem a forma combinada."""
    try:
        dados = de_json(saida, str(TENTATIVAS))
    except ErroDeDados:
        return None
    if not isinstance(dados, list):
        return None
    achados = [_achado_da_saida(item) for item in dados]
    return None if None in achados else achados


def _tentativas_com_o_usuario_da_ia(caminhos, pedido_de_administrador, usuario_da_ia, pedido_de_outro_usuario):
    """Os achados das tentativas feitas pelo tentativas.py, que roda com o usuário da IA pelo pedido de outro
    usuário, a partir da pasta desta peça. O que não roda, não acaba bem ou não escreve na forma combinada vale
    como pedido que não conseguiu rodar as tentativas."""
    pedido = pedido_para(pedido_de_outro_usuario, usuario_da_ia)
    entrada = json.dumps({CAMINHOS: list(caminhos), PEDIDO: list(pedido_de_administrador)}, ensure_ascii=False)
    comando = pedido + [sys.executable, "-I", str(RODA), str(TENTATIVAS), entrada]
    try:
        rodado = resultado(comando, PECA)
    except ErroDeDados:
        return _sem_resposta(caminhos)
    achados = _achados_da_saida(rodado.saida) if rodado.fim == PASSOU else None
    return _sem_resposta(caminhos) if achados is None else achados


def le_fechados(caminho):
    """A Lista do arquivo: os caminhos que ficam fechados para a IA, na ordem em que estão e cada um escrito desde
    o início do disco; as palavras do pedido de administrador; os nomes do usuário da IA e do usuário do programa;
    e as palavras do pedido de outro usuário. O caminho que não começa no início do disco conta a partir da pasta
    em que o arquivo está. Erro (ErroDeDados) quando o arquivo não se lê, não segue o molde, traz dois caminhos que
    levam ao mesmo lugar, traz os dois nomes de usuário iguais ou traz o pedido de outro usuário sem o lugar
    marcado do nome do usuário ou com outro lugar marcado."""
    lista = le_conferido(caminho, MOLDE)
    pasta = os.path.dirname(os.path.abspath(caminho))
    caminhos = [os.path.abspath(os.path.join(pasta, escrito)) for escrito in lista[FECHADOS]]
    repetido = repetidos(caminhos)
    if repetido:
        raise ErroDeDados(f"{caminho}: caminho repetido: {repetido}")
    _confere_usuarios(lista[USUARIO_DA_IA], lista[USUARIO_DO_PROGRAMA], lista[PEDIDO_DE_OUTRO], f"{caminho}: ")
    return Lista(caminhos, lista[PEDIDO], lista[USUARIO_DA_IA], lista[USUARIO_DO_PROGRAMA], lista[PEDIDO_DE_OUTRO])


def desprotegidos(caminhos, pedido_de_administrador, usuario_da_ia, usuario_do_programa, pedido_de_outro_usuario):
    """Os achados dos caminhos, na ordem deles, com o do pedido de administrador por último: as tentativas que o
    computador aceitou ao usuário da IA e as que não chegaram a ser feitas. Lista vazia quer dizer que ele recusou
    todas. Quando esta peça não roda com o usuário do programa, a resposta é só o achado de OUTRO_USUARIO, e
    nenhuma tentativa se faz. Erro (ErroDeDados) quando não vem nenhum caminho, quando um caminho não começa no
    início do disco, quando o pedido de administrador não tem nenhuma palavra, quando um dos dois nomes de usuário
    é vazio, quando os dois são iguais e quando o pedido de outro usuário não traz o lugar marcado do nome do
    usuário ou traz outro lugar marcado."""
    if not caminhos:
        raise ErroDeDados("nenhum caminho para conferir")
    soltos = [caminho for caminho in caminhos if not os.path.isabs(caminho)]
    if soltos:
        raise ErroDeDados(f"caminho que não começa no início do disco: {soltos}")
    if not pedido_de_administrador:
        raise ErroDeDados("pedido de administrador sem nenhuma palavra")
    _confere_usuarios(usuario_da_ia, usuario_do_programa, pedido_de_outro_usuario, "")
    if _usuario_atual() != usuario_do_programa:
        return [Achado(None, OUTRO_USUARIO)]
    return _tentativas_com_o_usuario_da_ia(caminhos, pedido_de_administrador, usuario_da_ia, pedido_de_outro_usuario)


def achados_da_lista(caminho):
    """Cada achado da conferência dos itens da lista do arquivo, lida pelo le_fechados e testada pelo desprotegidos,
    como uma linha de texto: o caminho, vazio no que não é de um arquivo, e o tipo, separados por ENTRE_CAMINHO_E_TIPO,
    na ordem do desprotegidos. Lista vazia quer dizer que o computador recusou todas as tentativas. Erro
    (ErroDeDados) nos casos do le_fechados e do desprotegidos."""
    return [f"{achado.caminho or ''}{ENTRE_CAMINHO_E_TIPO}{achado.tipo}"
            for achado in desprotegidos(*le_fechados(caminho))]
