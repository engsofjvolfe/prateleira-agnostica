"""
Faz no computador o ajuste que impede a IA de alterar os arquivos das peças que ficam de olho nela.

Lê a configuração e a lista e carrega a parte do sistema em que roda. Antes de mudar qualquer coisa, confere se o
computador está pronto para o ajuste: com algo errado, mostra o quê e para. Com tudo certo, faz os oito passos do
README, um por vez, e mostra cada coisa que fez; com a prévia, só mostra o que faria. No passo 7, depois de pôr a
regra da permissão, prova-a por três tentativas e tira a regra que pôs quando uma não dá o resultado certo. Cada
texto que mostra vem da configuração.

O código de saída diz como acabou: VALENDO, NAO_VALENDO ou NAO_CONSEGUIU.
"""
import argparse
import importlib.util
import os
import sys
from collections import namedtuple
from functools import partial
from pathlib import Path

import conferencia_de_protecao
from caminho_escrito import caminho_escrito
from caminhos_cobertos import ARQUIVO, ATALHO, FALTA, ONDE_VAI_APARECER, PASTA, cobertos, destino_do_atalho, lugar_real
from conferencia_de_molde import le_conferido
from conferencia_de_protecao import desprotegidos, le_fechados, pedido_para
from erro_de_dados import ErroDeDados
from leitura_de_texto import le_texto
from modelo_de_texto import campos, preenche
from resultado_de_comando import NAO_PASSOU, PASSOU, resultado

PECA = Path(__file__).resolve().parent  # a pasta desta peça
CENTRAL = Path(conferencia_de_protecao.__file__).resolve().parent.parent  # a pasta que guarda as peças da central
MOLDE = PECA / "esquemas" / f"{PECA.name}.schema.json"  # o molde da configuração, que tem o nome da pasta da peça
EXTENSAO = ".py"  # o fim do nome do arquivo da parte de um sistema; o começo é o nome que o Python dá ao sistema
USUARIO_DO_PROGRAMA = "usuario_do_programa"  # o lugar, na regra da permissão, do nome do usuário do programa
USUARIO_DA_IA = "usuario_da_ia"  # o lugar, na regra da permissão, do nome do usuário da IA
ARQUIVO_CONFERIDO = "arquivo"  # o lugar, no comando que confere a regra, do caminho do arquivo conferido
NADA = [sys.executable, "-I", "-c", ""]  # um comando que roda e acaba bem sem fazer nada: o das tentativas do passo 7
PROGRAMA_COMO_IA = "programa_como_ia"  # a tentativa do passo 7 de o usuário do programa rodar com o usuário da IA
IA_COMO_PROGRAMA = "ia_como_programa"  # a tentativa do passo 7 de o usuário da IA rodar com o usuário do programa
PROGRAMA_COMO_ADMINISTRADOR = "programa_como_administrador"  # a do usuário do programa rodar como administrador
PASTAS = (PASTA, ONDE_VAI_APARECER, FALTA)  # os tipos de caminho coberto que são pastas que o ajuste fecha
GUARDAM_DONO = (ARQUIVO, PASTA, ONDE_VAI_APARECER)  # os tipos de caminho coberto cujo dono a peça olha
VALENDO = 0  # o código de saída do ajuste feito sem nada achado pela conferência, e da prévia que passou
NAO_VALENDO = 1  # o código de saída de uma conferência ou tentativa que não passou e da conferência que achou algo
NAO_CONSEGUIU = 2  # o código de saída da peça que não conseguiu fazer o trabalho, também quando ela quebra
LUGARES = {  # os lugares que cada texto da configuração pode trazer, como na tabela de "Os textos" do README
    "sistema_nao_atendido": ("sistema",),
    "falta_ferramenta": ("ferramenta",),
    "sem_administrador": (),
    "ia_com_nome_repetido": ("usuario",),
    "programa_com_nome_da_pessoa": ("usuario",),
    "vira_administrador": ("usuario",),
    "item_em_pasta_de_trabalho": ("item", "pasta"),
    "pasta_acima_aberta": ("pasta", "item", "usuario"),
    "atalho_para_fora": ("atalho", "destino"),
    "item_de_outro_dono_aberto": ("item", "dono", "usuario"),
    "escrito_de_outro_dono": ("item", "dono"),
    "item_dentro_de_escrito": ("item", "escrito"),
    "onde_vai_aparecer_com_outros": ("pasta", "caminho"),
    "pasta_de_trabalho_em_item": ("pasta", "item"),
    "pasta_de_trabalho_com_outro_dono": ("caminho", "dono"),
    "pasta_da_regra_aberta": ("pasta",),
    "arquivo_da_regra_sem_a_regra": ("arquivo", "regra"),
    "regra_recusada": ("arquivo",),
    "permissao_errada": ("tentativa",),
    "fez": ("passo", "alvo"),
    "faria": ("passo", "alvo"),
    "encontrou": ("caminho", "tipo"),
}

# A configuração, chave por chave, como no README, com os caminhos escritos desde o início do disco.
Configuracao = namedtuple("Configuracao", "usuario_da_pessoa pastas_de_trabalho escritos_pelas_pecas "
                                          "comando_do_programa regra_da_permissao arquivo_da_regra "
                                          "conferencia_da_regra textos")

# O que o ajuste usa: a configuração; a lista; o caminho da lista e o da configuração, desde o início do disco; e a
# parte do sistema.
Ajuste = namedtuple("Ajuste", "configuracao lista caminho_da_lista caminho_da_configuracao sistema")

# Uma conferência de antes do ajuste que não passou: a chave do texto dela e o valor de cada lugar do texto.
Falha = namedtuple("Falha", "chave valores")

# Uma coisa que um passo faz: o alvo, que o texto mostra, e o que a faz; nada, quando o passo só mostra o alvo.
Acao = namedtuple("Acao", "alvo faz")


class _RegraRecusada(Exception):
    """O comando que confere a regra a recusou: o passo 7 para, e o arquivo da regra fica como estava."""


def _mostra(textos, chave, **valores):
    """Mostra o texto da chave, com cada lugar trocado pelo valor dele. A saída vai na hora, para o que já se fez
    aparecer mesmo quando um passo seguinte não dá certo."""
    print(preenche(textos[chave], {nome: str(valor) for nome, valor in valores.items()}), flush=True)


def _lugares_de(palavras):
    """Os nomes dos lugares marcados de uma lista de palavras."""
    return {lugar for palavra in palavras for lugar in campos(palavra)}


def _configuracao(caminho):
    """A configuração do arquivo, conferida contra o molde, com os caminhos escritos desde o início do disco. Erro
    (ErroDeDados) quando o arquivo não segue o molde, quando um texto traz um lugar que não é dele, quando a regra da
    permissão não traz os dois lugares dos nomes, ou traz outro, quando o comando que confere a regra não traz o lugar
    do arquivo, ou traz outro, e quando uma pasta de trabalho não existe."""
    dados = le_conferido(caminho, MOLDE)
    configuracao = Configuracao._make(dados[chave] for chave in Configuracao._fields)
    for chave, modelo in configuracao.textos.items():
        estranhos = sorted(set(campos(modelo)) - set(LUGARES[chave]))
        if estranhos:
            raise ErroDeDados(f"{caminho}: /textos/{chave}: lugar que não é deste texto: {estranhos}")
    da_regra = set(campos(configuracao.regra_da_permissao))
    if da_regra != {USUARIO_DO_PROGRAMA, USUARIO_DA_IA}:
        raise ErroDeDados(f"{caminho}: /regra_da_permissao: os lugares têm de ser {{{USUARIO_DO_PROGRAMA}}} e "
                          f"{{{USUARIO_DA_IA}}}, os dois e nenhum outro; os que estão: {sorted(da_regra)}")
    da_conferencia = _lugares_de(configuracao.conferencia_da_regra)
    if da_conferencia != {ARQUIVO_CONFERIDO}:
        raise ErroDeDados(f"{caminho}: /conferencia_da_regra: o lugar {{{ARQUIVO_CONFERIDO}}} tem de estar em alguma "
                          f"palavra, e nenhum outro; os que estão: {sorted(da_conferencia)}")
    pastas = [caminho_escrito(caminho, escrita) for escrita in configuracao.pastas_de_trabalho]
    faltam = [pasta for pasta in pastas if not os.path.isdir(pasta)]
    if faltam:
        raise ErroDeDados(f"{caminho}: /pastas_de_trabalho: pasta que não existe: {faltam}")
    escritos = [caminho_escrito(caminho, escrita) for escrita in configuracao.escritos_pelas_pecas]
    return configuracao._replace(pastas_de_trabalho=pastas, escritos_pelas_pecas=escritos,
                                 arquivo_da_regra=caminho_escrito(caminho, configuracao.arquivo_da_regra))


def _parte_do_sistema():
    """A parte desta peça para o sistema em que ela roda: o arquivo, na pasta da peça, com o nome que o Python dá ao
    sistema. Nada (None) quando o sistema não tem a sua parte."""
    arquivo = PECA / (sys.platform + EXTENSAO)
    if not arquivo.is_file():
        return None
    especificacao = importlib.util.spec_from_file_location(sys.platform, arquivo)
    parte = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(parte)
    return parte


def _dentro_de(caminho, pasta):
    """Se o caminho é a pasta ou está dentro dela, pelo que está escrito ou pelo lugar a que os atalhos levam."""
    return (Path(caminho).is_relative_to(pasta)
            or Path(os.path.realpath(caminho)).is_relative_to(os.path.realpath(pasta)))


def _acima(caminho):
    """As pastas acima do caminho, em ordem: as do caminho escrito e as do lugar real da pasta em que ele fica, que
    são outras quando o caminho passa por um atalho."""
    real = os.path.realpath(os.path.dirname(caminho))
    return sorted({str(pasta) for pasta in Path(caminho).parents} | {real}
                  | {str(pasta) for pasta in Path(real).parents})


def _da_peca(ajuste):
    """A lista, a configuração desta peça, a pasta desta peça e a pasta da central."""
    return [ajuste.caminho_da_lista, ajuste.caminho_da_configuracao, str(PECA), str(CENTRAL)]


def _itens(ajuste):
    """Os itens da lista e, como diz o README, a lista, a configuração desta peça, a pasta desta peça e a pasta da
    central, que contam como itens nas conferências de antes do ajuste e na do passo 8."""
    return ajuste.lista.caminhos + _da_peca(ajuste)


def _usuarios(ajuste):
    """O usuário da IA e o usuário do programa, os dois usuários que o ajuste cria."""
    return (ajuste.lista.usuario_da_ia, ajuste.lista.usuario_do_programa)


def _nossos(ajuste):
    """Os usuários de quem a peça troca o dono de um caminho: a pessoa e os dois usuários do ajuste."""
    return {ajuste.configuracao.usuario_da_pessoa, *_usuarios(ajuste)}


def _regra(ajuste):
    """A regra da permissão, com os nomes do usuário do programa e do usuário da IA nos lugares marcados."""
    lista = ajuste.lista
    return preenche(ajuste.configuracao.regra_da_permissao,
                    {USUARIO_DO_PROGRAMA: lista.usuario_do_programa, USUARIO_DA_IA: lista.usuario_da_ia})


def _tem_a_regra(ajuste):
    """Se o arquivo da regra existe e já traz a regra."""
    arquivo = ajuste.configuracao.arquivo_da_regra
    return os.path.lexists(arquivo) and _regra(ajuste) in le_texto(arquivo)


def _nomes(ajuste):
    """As conferências dos dois usuários: o da IA não tem o nome da pessoa; o do programa também não; e nenhum dos
    dois, quando já existe, vira administrador sem senha."""
    configuracao, lista, sistema = ajuste.configuracao, ajuste.lista, ajuste.sistema
    falhas = []
    if lista.usuario_da_ia == configuracao.usuario_da_pessoa:
        falhas.append(Falha("ia_com_nome_repetido", {"usuario": lista.usuario_da_ia}))
    if lista.usuario_do_programa == configuracao.usuario_da_pessoa:
        falhas.append(Falha("programa_com_nome_da_pessoa", {"usuario": lista.usuario_do_programa}))
    for usuario in _usuarios(ajuste):
        if sistema.existe(usuario) and sistema.vira_administrador(usuario, lista.pedido_de_administrador):
            falhas.append(Falha("vira_administrador", {"usuario": usuario}))
    return falhas


def _acima_dos(alvos, fechadas):
    """As pastas que existem acima do que cada alvo cobre, fora o que está dentro dele, cada uma com o primeiro caminho
    que está embaixo dela. A pasta que o ajuste fecha não conta."""
    acima = {}
    for alvo in alvos:
        for coberto in cobertos(alvo, set()):
            if coberto.de_dentro:
                continue
            for pasta in _acima(coberto.caminho):
                if os.path.lexists(pasta) and os.path.realpath(pasta) not in fechadas:
                    acima.setdefault(pasta, coberto.caminho)
    return acima


def _pastas_acima_abertas(ajuste, todos):
    """As pastas acima dos itens que o usuário da IA consegue alterar, e as pastas acima dos itens em que as peças não
    escrevem que o usuário do programa consegue alterar, cada uma com o primeiro item que está embaixo dela e o
    usuário. Nos itens em que as peças escrevem, o usuário do programa já altera o item, e as pastas acima deles não
    contam para ele. A pasta que o ajuste fecha não conta."""
    fechadas = {os.path.realpath(coberto.caminho) for coberto in todos if coberto.tipo in PASTAS}
    itens, escritos = _itens(ajuste), ajuste.configuracao.escritos_pelas_pecas
    por_usuario = ((ajuste.lista.usuario_da_ia, _acima_dos(itens, fechadas)),
                   (ajuste.lista.usuario_do_programa,
                    _acima_dos([item for item in itens if item not in escritos], fechadas)))
    falhas = []
    for usuario, acima in por_usuario:
        for pasta in ajuste.sistema.alteraveis(usuario, sorted(acima)):
            falhas.append(Falha("pasta_acima_aberta", {"pasta": pasta, "item": acima[pasta], "usuario": usuario}))
    return falhas


def _atalhos_para_fora(todos, itens):
    """Os atalhos de dentro das pastas dos itens que levam a um caminho que não é um item nem está dentro de um."""
    falhas = []
    for coberto in todos:
        if coberto.tipo == ATALHO and coberto.de_dentro:
            destino = destino_do_atalho(coberto.caminho)
            if not any(_dentro_de(destino, item) for item in itens):
                falhas.append(Falha("atalho_para_fora", {"atalho": coberto.caminho, "destino": destino}))
    return falhas


def _de_outro_dono_abertos(ajuste, todos):
    """Os itens de outro dono que um dos dois usuários do ajuste consegue alterar, cada um com o dono e o usuário.
    Outro dono é quem não é a pessoa nem um dos dois usuários do ajuste: desses itens a peça não troca o dono."""
    sistema, nossos = ajuste.sistema, _nossos(ajuste)
    de_outro = {}
    for coberto in todos:
        if coberto.tipo in GUARDAM_DONO:
            dono = sistema.dono(coberto.caminho)
            if dono not in nossos:
                de_outro[coberto.caminho] = dono
    falhas = []
    for usuario in _usuarios(ajuste):
        for caminho in sistema.alteraveis(usuario, list(de_outro)):
            falhas.append(Falha("item_de_outro_dono_aberto",
                                {"item": caminho, "dono": de_outro[caminho], "usuario": usuario}))
    return falhas


def _escritos_de_outro_dono(ajuste):
    """O que os itens em que as peças escrevem cobrem e não é da pessoa nem de um dos dois usuários do ajuste, cada
    um com o dono: esse caminho a peça não entregaria ao usuário do programa."""
    sistema, nossos, vistos = ajuste.sistema, _nossos(ajuste), set()
    falhas = []
    for escrito in ajuste.configuracao.escritos_pelas_pecas:
        for coberto in cobertos(escrito, vistos):
            if coberto.tipo in GUARDAM_DONO:
                dono = sistema.dono(coberto.caminho)
                if dono not in nossos:
                    falhas.append(Falha("escrito_de_outro_dono", {"item": coberto.caminho, "dono": dono}))
    return falhas


def _dentro_de_escritos(ajuste):
    """Os itens em que as peças não escrevem que estão dentro de um item em que elas escrevem, cada um com ele."""
    escritos = ajuste.configuracao.escritos_pelas_pecas
    return [Falha("item_dentro_de_escrito", {"item": item, "escrito": escrito})
            for item in _itens(ajuste) if item not in escritos
            for escrito in escritos if _dentro_de(item, escrito)]


def _onde_vai_aparecer_com_outros(todos):
    """O que está numa pasta em que um item que ainda não existe vai aparecer e não é um caminho que os itens cobrem
    nem uma pasta no caminho até um deles, como as que a peça cria quando faltam; cada um com a pasta."""
    reais = {lugar_real(coberto.caminho) for coberto in todos}
    dos_itens = reais | {str(pasta) for real in reais for pasta in Path(real).parents}
    falhas = []
    for coberto in todos:
        if coberto.tipo == ONDE_VAI_APARECER:
            for nome in sorted(os.listdir(coberto.caminho)):
                dentro = os.path.join(coberto.caminho, nome)
                if lugar_real(dentro) not in dos_itens:
                    falhas.append(Falha("onde_vai_aparecer_com_outros", {"pasta": coberto.caminho, "caminho": dentro}))
    return falhas


def _de_outro_dono_nas_pastas_de_trabalho(ajuste):
    """O que está nas pastas de trabalho e não é da pessoa nem de um dos dois usuários do ajuste, cada um com o dono.
    Do que já se achou, o que está dentro não se repete. O atalho não conta, porque a peça não o abre."""
    sistema, nossos = ajuste.sistema, _nossos(ajuste)
    falhas, achados = [], []
    for pasta in ajuste.configuracao.pastas_de_trabalho:
        for coberto in cobertos(pasta, set()):
            if coberto.tipo == ATALHO or any(Path(coberto.caminho).is_relative_to(achado) for achado in achados):
                continue
            dono = sistema.dono(coberto.caminho)
            if dono not in nossos:
                achados.append(coberto.caminho)
                falhas.append(Falha("pasta_de_trabalho_com_outro_dono", {"caminho": coberto.caminho, "dono": dono}))
    return falhas


def _regra_aberta(ajuste):
    """O arquivo da regra, quando já existe, e as pastas do caminho dele, pelo caminho escrito e pelo lugar real, que
    outro usuário que não o administrador consegue alterar."""
    arquivo = ajuste.configuracao.arquivo_da_regra
    caminhos = [pasta for pasta in _acima(arquivo) if os.path.lexists(pasta)]
    if os.path.exists(arquivo):
        caminhos.append(arquivo)
    return [Falha("pasta_da_regra_aberta", {"pasta": caminho}) for caminho in caminhos
            if not ajuste.sistema.so_o_administrador_altera(caminho)]


def _sem_a_regra(ajuste):
    """O arquivo da regra que já existe e não traz a regra: a peça não o escreve por cima."""
    arquivo = ajuste.configuracao.arquivo_da_regra
    if os.path.lexists(arquivo) and not _tem_a_regra(ajuste):
        return [Falha("arquivo_da_regra_sem_a_regra", {"arquivo": arquivo, "regra": _regra(ajuste)})]
    return []


def _conferencias(ajuste):
    """As conferências de antes do ajuste que não passaram, na ordem da tabela do README. Nenhuma muda nada."""
    pastas_de_trabalho = ajuste.configuracao.pastas_de_trabalho
    itens, vistos = _itens(ajuste), set()
    todos = [coberto for item in itens for coberto in cobertos(item, vistos)]
    principais = [coberto for coberto in todos if not coberto.de_dentro]
    falhas = _nomes(ajuste)
    falhas += [Falha("item_em_pasta_de_trabalho", {"item": coberto.caminho, "pasta": pasta})
               for coberto in principais for pasta in pastas_de_trabalho if _dentro_de(coberto.caminho, pasta)]
    falhas += _pastas_acima_abertas(ajuste, todos)
    falhas += _atalhos_para_fora(todos, itens)
    falhas += _de_outro_dono_abertos(ajuste, todos)
    falhas += _escritos_de_outro_dono(ajuste)
    falhas += _dentro_de_escritos(ajuste)
    falhas += _onde_vai_aparecer_com_outros(todos)
    falhas += [Falha("pasta_de_trabalho_em_item", {"pasta": pasta, "item": coberto.caminho})
               for pasta in pastas_de_trabalho for coberto in principais
               if coberto.tipo == PASTA and _dentro_de(pasta, coberto.caminho)]
    falhas += _de_outro_dono_nas_pastas_de_trabalho(ajuste)
    falhas += _regra_aberta(ajuste)
    falhas += _sem_a_regra(ajuste)
    return falhas


def _que_faltam(pasta):
    """As pastas que faltam no caminho até a pasta, a de cima primeiro."""
    faltam = []
    while not os.path.lexists(pasta):
        faltam.insert(0, pasta)
        pasta = os.path.dirname(pasta)
    return faltam


def _faz_todos(fazeres):
    """Faz cada coisa, na ordem."""
    for faz in fazeres:
        faz()


def _da_leitura_onde_falta(sistema, leitor, caminhos):
    """Dá ao leitor a leitura de cada caminho que ele não lê."""
    for caminho in sistema.sem_leitura(leitor, caminhos):
        sistema.da_leitura(leitor, caminho)


def _fechamentos(sistema, vistos, criadas, novo_dono, trocaveis, leitores, alvo):
    """O que fecha, com o novo dono, cada caminho que o alvo cobre. A pasta que falta nasce fechada, junto com as que
    faltam acima dela, e a que já se vai criar não se cria de novo. O caminho que ainda não está fechado se fecha.
    Cada leitor ganha, depois de tudo fechado, a leitura do que não lê. Com os donos trocáveis, só muda o caminho que
    é de um deles; sem eles (None), muda todo caminho."""
    fazeres, para_ler = [], []
    for coberto in cobertos(alvo, vistos):
        if coberto.tipo == FALTA:
            novas = [pasta for pasta in _que_faltam(coberto.caminho) if pasta not in criadas]
            criadas.update(novas)
            fazeres += [partial(sistema.cria_pasta_fechada, pasta, novo_dono) for pasta in novas]
            continue
        if trocaveis is not None and sistema.dono(coberto.caminho) not in trocaveis:
            continue
        if not sistema.fechado(coberto.caminho, novo_dono):
            fazeres.append(partial(sistema.fecha, coberto.caminho, novo_dono, trocaveis))
        if coberto.tipo != ATALHO:
            para_ler.append(coberto.caminho)
    mudou = bool(fazeres)
    for leitor in leitores:
        if para_ler and (mudou or sistema.sem_leitura(leitor, para_ler)):
            fazeres.append(partial(_da_leitura_onde_falta, sistema, leitor, para_ler))
    return fazeres


def _acoes_de_fechar(alvos, fechamentos):
    """Uma ação por alvo que tem o que fechar, com tudo o que fecha o que ele cobre."""
    acoes = []
    for alvo in alvos:
        fazeres = fechamentos(alvo)
        if fazeres:
            acoes.append(Acao(alvo, partial(_faz_todos, fazeres)))
    return acoes


def _passo_1(ajuste):
    """Criar os usuários: o da IA e o do programa. O usuário que já existe não se cria de novo."""
    sistema = ajuste.sistema
    return [Acao(nome, partial(sistema.cria_usuario, nome)) for nome in _usuarios(ajuste) if not sistema.existe(nome)]


def _passo_2(ajuste):
    """Fechar os itens da lista: os itens em que as peças escrevem ficam com o usuário do programa como dono, e os
    outros com o administrador; os dois usuários do ajuste leem todos. Os itens em que as peças escrevem se fecham
    primeiro, para o que um item de fora cobre e já está num deles não mudar de novo. Só muda o caminho que é da
    pessoa ou de um dos dois usuários do ajuste; o de outro dono fica como está."""
    configuracao, lista, sistema = ajuste.configuracao, ajuste.lista, ajuste.sistema
    vistos, criadas, trocaveis, leitores = set(), set(), _nossos(ajuste), _usuarios(ajuste)
    escritos = configuracao.escritos_pelas_pecas
    outros = [caminho for caminho in lista.caminhos if caminho not in escritos]
    do_programa = partial(_fechamentos, sistema, vistos, criadas, lista.usuario_do_programa, trocaveis, leitores)
    do_administrador = partial(_fechamentos, sistema, vistos, criadas, sistema.administrador(), trocaveis, leitores)
    return _acoes_de_fechar(escritos, do_programa) + _acoes_de_fechar(outros, do_administrador)


def _passo_3(ajuste):
    """Proteger a lista: o administrador vira o dono dela e só ele a altera; o usuário do programa a lê, porque as
    peças, que rodam com ele, a passam à conferência."""
    sistema = ajuste.sistema
    fechamentos = partial(_fechamentos, sistema, set(), set(), sistema.administrador(), None,
                          (ajuste.lista.usuario_do_programa,))
    return _acoes_de_fechar([ajuste.caminho_da_lista], fechamentos)


def _passo_4(ajuste):
    """Proteger esta peça: o administrador vira o dono da configuração dela, da pasta dela e da pasta da central, e
    só ele as altera; os dois usuários do ajuste leem a central, porque as peças e a conferência usam o código dela."""
    sistema = ajuste.sistema
    so_o_administrador = partial(_fechamentos, sistema, set(), set(), sistema.administrador(), None, ())
    com_leitura = partial(_fechamentos, sistema, set(), set(), sistema.administrador(), None, _usuarios(ajuste))
    return (_acoes_de_fechar([ajuste.caminho_da_configuracao, str(PECA)], so_o_administrador)
            + _acoes_de_fechar([str(CENTRAL)], com_leitura))


def _pastas_para_entrar(alvos, pastas_de_trabalho):
    """As pastas que existem acima dos alvos e das pastas de trabalho, pelo caminho escrito e pelo lugar real, e as
    pastas que os alvos cobrem, em ordem."""
    vistos, pastas = set(), set()
    for alvo in alvos:
        for coberto in cobertos(alvo, vistos):
            pastas.update(_acima(coberto.caminho))
            if coberto.tipo in PASTAS:
                pastas.add(coberto.caminho)
    for pasta in pastas_de_trabalho:
        pastas.update(_acima(pasta))
    return sorted(pasta for pasta in pastas if os.path.isdir(pasta))


def _passo_5(ajuste):
    """Abrir o caminho: o usuário do programa ganha o direito de entrar nas pastas até os itens, a lista, a central e
    as pastas de trabalho; o usuário da IA, nas pastas até os itens, a central e as pastas de trabalho. Só nas pastas
    em que ele ainda não entra."""
    configuracao, lista, sistema = ajuste.configuracao, ajuste.lista, ajuste.sistema
    pastas_de_trabalho = configuracao.pastas_de_trabalho
    caminhos = {
        lista.usuario_do_programa: _pastas_para_entrar(lista.caminhos + [ajuste.caminho_da_lista, str(CENTRAL)],
                                                       pastas_de_trabalho),
        lista.usuario_da_ia: _pastas_para_entrar(lista.caminhos + [str(CENTRAL)], pastas_de_trabalho),
    }
    return [Acao(pasta, partial(sistema.abre_entrada, usuario, pasta))
            for usuario, pastas in caminhos.items() for pasta in sistema.sem_entrada(usuario, pastas)]


def _passo_6(ajuste):
    """Abrir as pastas de trabalho para os dois usuários do ajuste, com o que está nelas e o que nascer nelas, e
    manter a pessoa alterando tudo o que está nelas."""
    configuracao = ajuste.configuracao
    abre = partial(ajuste.sistema.abre_pasta_de_trabalho, _usuarios(ajuste), configuracao.usuario_da_pessoa)
    return [Acao(pasta, partial(abre, pasta)) for pasta in configuracao.pastas_de_trabalho]


def _confere_a_regra(ajuste, novo):
    """Se o comando da configuração aceita o arquivo novo da regra: ele roda a partir da pasta do arquivo novo e acaba
    bem. O comando que não roda conta como recusa."""
    comando = [preenche(palavra, {ARQUIVO_CONFERIDO: novo}) for palavra in ajuste.configuracao.conferencia_da_regra]
    try:
        return resultado(comando, os.path.dirname(novo)).fim == PASSOU
    except ErroDeDados:
        return False


def _poe_a_regra(ajuste, regra):
    """Põe a regra no arquivo dela, conferida antes. Erro (_RegraRecusada) quando a conferência a recusa."""
    if not ajuste.sistema.poe_regra(ajuste.configuracao.arquivo_da_regra, regra, partial(_confere_a_regra, ajuste)):
        raise _RegraRecusada()


def _passo_7(ajuste):
    """Deixar pronto o jeito de abrir o programa: pôr a regra da permissão, quando o arquivo dela ainda não a traz;
    montar o comando que abre o programa com o usuário do programa; e montar as palavras com que o programa roda uma
    ação com o usuário da IA. O comando e as palavras só se mostram."""
    configuracao, lista, sistema = ajuste.configuracao, ajuste.lista, ajuste.sistema
    acoes = []
    if not _tem_a_regra(ajuste):
        regra = _regra(ajuste)
        acoes.append(Acao(regra, partial(_poe_a_regra, ajuste, regra)))
    comando = pedido_para(lista.pedido_de_outro_usuario, lista.usuario_do_programa) + configuracao.comando_do_programa
    acoes.append(Acao(sistema.mostra_comando(comando), None))
    acoes.append(Acao(sistema.mostra_comando(pedido_para(lista.pedido_de_outro_usuario, lista.usuario_da_ia)), None))
    return acoes


PASSOS = (_passo_1, _passo_2, _passo_3, _passo_4, _passo_5, _passo_6, _passo_7)  # os passos de 1 a 7, na ordem do README


def _faz_os_passos(ajuste, previa):
    """Faz os passos de 1 a 7, na ordem, e mostra cada coisa que fez; com a prévia, só mostra o que faria. Cada passo
    olha o computador como os passos de antes o deixaram."""
    chave = "faria" if previa else "fez"
    for numero, passo in enumerate(PASSOS, start=1):
        for acao in passo(ajuste):
            if acao.faz and not previa:
                acao.faz()
            _mostra(ajuste.configuracao.textos, chave, passo=numero, alvo=acao.alvo)


def _prova_a_permissao(ajuste):
    """As tentativas do passo 7 que não deram o resultado certo, pelo nome de cada uma, na ordem do README: o usuário
    do programa roda com o usuário da IA; o usuário da IA não roda com o usuário do programa; e o usuário do programa
    não roda como administrador. Cada uma roda com o usuário de quem tenta."""
    lista, sistema = ajuste.lista, ajuste.sistema
    ia, programa = lista.usuario_da_ia, lista.usuario_do_programa
    erradas = []
    if sistema.fim_com_o_usuario(programa, pedido_para(lista.pedido_de_outro_usuario, ia) + NADA) != PASSOU:
        erradas.append(PROGRAMA_COMO_IA)
    if sistema.fim_com_o_usuario(ia, pedido_para(lista.pedido_de_outro_usuario, programa) + NADA) != NAO_PASSOU:
        erradas.append(IA_COMO_PROGRAMA)
    if sistema.vira_administrador(programa, lista.pedido_de_administrador):
        erradas.append(PROGRAMA_COMO_ADMINISTRADOR)
    return erradas


def _confere(ajuste, previa):
    """O passo 8: com o usuário do programa, como as peças, a conferência tenta alterar cada item com o usuário da IA,
    e também a lista, a configuração desta peça, a pasta desta peça e a pasta da central; a peça mostra cada linha que
    a conferência entregou. Com a prévia, só mostra que faria. Dá o código de saída."""
    numero, textos, lista = len(PASSOS) + 1, ajuste.configuracao.textos, ajuste.lista
    if previa:
        _mostra(textos, "faria", passo=numero, alvo=ajuste.caminho_da_lista)
        return VALENDO
    achados = ajuste.sistema.com_o_usuario(lista.usuario_do_programa, desprotegidos, _itens(ajuste),
                                           lista.pedido_de_administrador, lista.usuario_da_ia,
                                           lista.usuario_do_programa, lista.pedido_de_outro_usuario)
    _mostra(textos, "fez", passo=numero, alvo=ajuste.caminho_da_lista)
    for caminho, tipo in achados:
        _mostra(textos, "encontrou", caminho=caminho or "", tipo=tipo)
    return NAO_VALENDO if achados else VALENDO


def _ajusta(opcoes):
    """Faz o ajuste, ou a prévia dele, e dá o código de saída."""
    configuracao = _configuracao(opcoes.config)
    lista = le_fechados(opcoes.lista)
    fora_da_lista = [escrito for escrito in configuracao.escritos_pelas_pecas if escrito not in lista.caminhos]
    if fora_da_lista:
        raise ErroDeDados(f"{opcoes.config}: /escritos_pelas_pecas: caminho que não está na lista: {fora_da_lista}")
    textos = configuracao.textos
    sistema = _parte_do_sistema()
    if sistema is None:
        _mostra(textos, "sistema_nao_atendido", sistema=sys.platform)
        return NAO_VALENDO
    if not sistema.existe(configuracao.usuario_da_pessoa):
        raise ErroDeDados(f"{opcoes.config}: /usuario_da_pessoa: usuário que não existe neste computador: "
                          f"{configuracao.usuario_da_pessoa}")
    if not sistema.eh_administrador():
        _mostra(textos, "sem_administrador")
        return NAO_VALENDO
    faltam = sistema.ferramentas_que_faltam()
    for ferramenta in faltam:
        _mostra(textos, "falta_ferramenta", ferramenta=ferramenta)
    if faltam:
        return NAO_VALENDO
    ajuste = Ajuste(configuracao, lista, os.path.abspath(opcoes.lista), os.path.abspath(opcoes.config), sistema)
    falhas = _conferencias(ajuste)
    for falha in falhas:
        _mostra(textos, falha.chave, **falha.valores)
    if falhas:
        return NAO_VALENDO
    posta = not opcoes.previa and not _tem_a_regra(ajuste)
    try:
        _faz_os_passos(ajuste, opcoes.previa)
    except _RegraRecusada:
        _mostra(textos, "regra_recusada", arquivo=configuracao.arquivo_da_regra)
        return NAO_CONSEGUIU
    if not opcoes.previa:
        erradas = _prova_a_permissao(ajuste)
        if erradas:
            if posta:
                sistema.tira_regra(configuracao.arquivo_da_regra)
            for tentativa in erradas:
                _mostra(textos, "permissao_errada", tentativa=tentativa)
            return NAO_VALENDO
    return _confere(ajuste, opcoes.previa)


def _opcoes():
    """As opções do comando, como em "As opções do comando" do README."""
    leitor = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    leitor.add_argument("--config", required=True)
    leitor.add_argument("--lista", required=True)
    leitor.add_argument("--previa", action="store_true")
    return leitor.parse_args()


def main():
    """Roda a peça. Toda quebra sai com NAO_CONSEGUIU, e não com o 1 que o Python daria, que quer dizer NAO_VALENDO."""
    opcoes = _opcoes()
    try:
        return _ajusta(opcoes)
    except Exception as erro:
        print(erro if isinstance(erro, (ErroDeDados, OSError)) else repr(erro), file=sys.stderr)
        return NAO_CONSEGUIU


if __name__ == "__main__":
    sys.exit(main())
