"""
Faz no computador o ajuste que impede a IA de alterar os arquivos das peças que ficam de olho nela.

Lê a configuração e a lista e carrega a parte do sistema em que roda. Antes de mudar qualquer coisa, confere se o
computador está pronto para o ajuste: com algo errado, mostra o quê e para. Com tudo certo, faz os oito passos do
README, um por vez, e mostra cada coisa que fez; com a prévia, só mostra o que faria. Cada texto que mostra vem da
configuração.

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
from conferencia_de_protecao import desprotegidos, le_fechados
from erro_de_dados import ErroDeDados
from modelo_de_texto import campos, preenche

PECA = Path(__file__).resolve().parent  # a pasta desta peça
CENTRAL = Path(conferencia_de_protecao.__file__).resolve().parent.parent  # a pasta que guarda as peças da central
MOLDE = PECA / "esquemas" / f"{PECA.name}.schema.json"  # o molde da configuração, que tem o nome da pasta da peça
EXTENSAO = ".py"  # o fim do nome do arquivo da parte de um sistema; o começo é o nome que o Python dá ao sistema
USUARIO = "usuario"  # o lugar, nas palavras do pedido de outro usuário, em que entra o nome do usuário da IA
PASTAS = (PASTA, ONDE_VAI_APARECER, FALTA)  # os tipos de caminho coberto que são pastas que o ajuste fecha
VALENDO = 0  # o código de saída do ajuste feito sem nada achado pela conferência, e da prévia que passou
NAO_VALENDO = 1  # o código de saída da conferência de antes que não passou e da conferência do passo 8 que achou algo
NAO_CONSEGUIU = 2  # o código de saída da peça que não conseguiu fazer o trabalho, também quando ela quebra
LUGARES = {  # os lugares que cada texto da configuração pode trazer, como na tabela de "Os textos" do README
    "sistema_nao_atendido": ("sistema",),
    "falta_ferramenta": ("ferramenta",),
    "sem_administrador": (),
    "ia_com_nome_repetido": ("usuario",),
    "ia_vira_administrador": ("usuario",),
    "item_em_pasta_de_trabalho": ("item", "pasta"),
    "pasta_acima_aberta": ("pasta", "item"),
    "atalho_para_fora": ("atalho", "destino"),
    "item_de_outro_dono_aberto": ("item", "dono"),
    "onde_vai_aparecer_com_outros": ("pasta", "caminho"),
    "pasta_de_trabalho_em_item": ("pasta", "item"),
    "pasta_de_trabalho_com_outro_dono": ("caminho", "dono"),
    "fez": ("passo", "alvo"),
    "faria": ("passo", "alvo"),
    "encontrou": ("caminho", "tipo"),
}

# A configuração, chave por chave, como no README, com as pastas de trabalho escritas desde o início do disco.
Configuracao = namedtuple("Configuracao", "usuario_da_ia usuario_da_pessoa dono_dos_itens pastas_de_trabalho "
                                          "comando_da_ia pedido_de_outro_usuario textos")

# O que o ajuste usa: a configuração; a lista; o caminho da lista e o da configuração, desde o início do disco; e a
# parte do sistema.
Ajuste = namedtuple("Ajuste", "configuracao lista caminho_da_lista caminho_da_configuracao sistema")

# Uma conferência de antes do ajuste que não passou: a chave do texto dela e o valor de cada lugar do texto.
Falha = namedtuple("Falha", "chave valores")

# Uma coisa que um passo faz: o alvo, que o texto mostra, e o que a faz; nada, quando o passo só mostra o alvo.
Acao = namedtuple("Acao", "alvo faz")


def _mostra(textos, chave, **valores):
    """Mostra o texto da chave, com cada lugar trocado pelo valor dele. A saída vai na hora, para o que já se fez
    aparecer mesmo quando um passo seguinte não dá certo."""
    print(preenche(textos[chave], {nome: str(valor) for nome, valor in valores.items()}), flush=True)


def _configuracao(caminho):
    """A configuração do arquivo, conferida contra o molde, com as pastas de trabalho escritas desde o início do
    disco. Erro (ErroDeDados) quando o arquivo não segue o molde, quando os lugares do pedido de outro usuário não são
    só o do usuário, quando um texto traz um lugar que não é dele e quando uma pasta de trabalho não existe."""
    dados = le_conferido(caminho, MOLDE)
    configuracao = Configuracao._make(dados[chave] for chave in Configuracao._fields)
    lugares = {lugar for palavra in configuracao.pedido_de_outro_usuario for lugar in campos(palavra)}
    if lugares != {USUARIO}:
        raise ErroDeDados(f"{caminho}: /pedido_de_outro_usuario: o lugar {{{USUARIO}}} tem de estar em alguma palavra, "
                          f"e nenhum outro; os lugares que estão: {sorted(lugares)}")
    for chave, modelo in configuracao.textos.items():
        estranhos = sorted(set(campos(modelo)) - set(LUGARES[chave]))
        if estranhos:
            raise ErroDeDados(f"{caminho}: /textos/{chave}: lugar que não é deste texto: {estranhos}")
    pastas = [caminho_escrito(caminho, escrita) for escrita in configuracao.pastas_de_trabalho]
    faltam = [pasta for pasta in pastas if not os.path.isdir(pasta)]
    if faltam:
        raise ErroDeDados(f"{caminho}: /pastas_de_trabalho: pasta que não existe: {faltam}")
    return configuracao._replace(pastas_de_trabalho=pastas)


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


def _pastas_acima_abertas(ajuste, todos, principais):
    """As pastas acima dos itens que o usuário da IA consegue alterar, cada uma com o primeiro item que está embaixo
    dela. A pasta que o ajuste fecha não conta."""
    fechadas = {os.path.realpath(coberto.caminho) for coberto in todos if coberto.tipo in PASTAS}
    acima = {}
    for coberto in principais:
        for pasta in _acima(coberto.caminho):
            if os.path.lexists(pasta) and os.path.realpath(pasta) not in fechadas:
                acima.setdefault(pasta, coberto.caminho)
    abertas = ajuste.sistema.alteraveis(ajuste.configuracao.usuario_da_ia, sorted(acima))
    return [Falha("pasta_acima_aberta", {"pasta": pasta, "item": acima[pasta]}) for pasta in abertas]


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
    """Os itens de outro dono que o usuário da IA consegue alterar, cada um com o dono. Outro dono é quem não é a
    pessoa, o usuário da IA nem o dono dos itens: desses itens a peça não troca o dono."""
    configuracao, sistema = ajuste.configuracao, ajuste.sistema
    nossos = {configuracao.usuario_da_pessoa, configuracao.usuario_da_ia, configuracao.dono_dos_itens}
    de_outro = {}
    for coberto in todos:
        if coberto.tipo in (ARQUIVO, PASTA, ONDE_VAI_APARECER):
            dono = sistema.dono(coberto.caminho)
            if dono not in nossos:
                de_outro[coberto.caminho] = dono
    abertos = sistema.alteraveis(configuracao.usuario_da_ia, list(de_outro))
    return [Falha("item_de_outro_dono_aberto", {"item": caminho, "dono": de_outro[caminho]}) for caminho in abertos]


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
    """O que está nas pastas de trabalho e não é da pessoa nem do usuário da IA, cada um com o dono. Do que já se
    achou, o que está dentro não se repete. O atalho não conta, porque a peça não o abre."""
    configuracao, sistema = ajuste.configuracao, ajuste.sistema
    nossos = {configuracao.usuario_da_pessoa, configuracao.usuario_da_ia}
    falhas, achados = [], []
    for pasta in configuracao.pastas_de_trabalho:
        for coberto in cobertos(pasta, set()):
            if coberto.tipo == ATALHO or any(Path(coberto.caminho).is_relative_to(achado) for achado in achados):
                continue
            dono = sistema.dono(coberto.caminho)
            if dono not in nossos:
                achados.append(coberto.caminho)
                falhas.append(Falha("pasta_de_trabalho_com_outro_dono", {"caminho": coberto.caminho, "dono": dono}))
    return falhas


def _conferencias(ajuste):
    """As conferências de antes do ajuste que não passaram, na ordem da tabela do README. Nenhuma muda nada."""
    configuracao, sistema = ajuste.configuracao, ajuste.sistema
    ia, pastas_de_trabalho = configuracao.usuario_da_ia, configuracao.pastas_de_trabalho
    itens, vistos = _itens(ajuste), set()
    todos = [coberto for item in itens for coberto in cobertos(item, vistos)]
    principais = [coberto for coberto in todos if not coberto.de_dentro]
    falhas = []
    if ia in (configuracao.usuario_da_pessoa, configuracao.dono_dos_itens):
        falhas.append(Falha("ia_com_nome_repetido", {"usuario": ia}))
    if sistema.existe(ia) and sistema.vira_administrador(ia, ajuste.lista.pedido_de_administrador):
        falhas.append(Falha("ia_vira_administrador", {"usuario": ia}))
    falhas += [Falha("item_em_pasta_de_trabalho", {"item": coberto.caminho, "pasta": pasta})
               for coberto in principais for pasta in pastas_de_trabalho if _dentro_de(coberto.caminho, pasta)]
    falhas += _pastas_acima_abertas(ajuste, todos, principais)
    falhas += _atalhos_para_fora(todos, itens)
    falhas += _de_outro_dono_abertos(ajuste, todos)
    falhas += _onde_vai_aparecer_com_outros(todos)
    falhas += [Falha("pasta_de_trabalho_em_item", {"pasta": pasta, "item": coberto.caminho})
               for pasta in pastas_de_trabalho for coberto in principais
               if coberto.tipo == PASTA and _dentro_de(pasta, coberto.caminho)]
    falhas += _de_outro_dono_nas_pastas_de_trabalho(ajuste)
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


def _fechamentos(sistema, vistos, criadas, novo_dono, trocaveis, leitor, alvo):
    """O que fecha, com o novo dono, cada caminho que o alvo cobre. A pasta que falta nasce fechada, junto com as que
    faltam acima dela, e a que já se vai criar não se cria de novo. O caminho que ainda não está fechado se fecha.
    Com um leitor, ele ganha, depois de tudo fechado, a leitura do que não lê. Com os donos trocáveis, só muda o
    caminho que é de um deles; sem eles (None), muda todo caminho."""
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
        if leitor is not None and coberto.tipo != ATALHO:
            para_ler.append(coberto.caminho)
    if para_ler and (fazeres or sistema.sem_leitura(leitor, para_ler)):
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
    """Criar os usuários: o da IA e, quando o dono dos itens não é o usuário da pessoa, o dono dos itens. O usuário
    que já existe não se cria de novo."""
    configuracao, sistema = ajuste.configuracao, ajuste.sistema
    nomes = [configuracao.usuario_da_ia]
    if configuracao.dono_dos_itens != configuracao.usuario_da_pessoa:
        nomes.append(configuracao.dono_dos_itens)
    return [Acao(nome, partial(sistema.cria_usuario, nome)) for nome in nomes if not sistema.existe(nome)]


def _passo_2(ajuste):
    """Fechar os itens da lista com o dono dos itens, e o usuário da IA lendo cada um. Só muda o caminho que é da
    pessoa, do usuário da IA ou do dono dos itens; o de outro dono fica como está."""
    configuracao = ajuste.configuracao
    trocaveis = {configuracao.usuario_da_pessoa, configuracao.usuario_da_ia, configuracao.dono_dos_itens}
    fechamentos = partial(_fechamentos, ajuste.sistema, set(), set(), configuracao.dono_dos_itens, trocaveis,
                          configuracao.usuario_da_ia)
    return _acoes_de_fechar(ajuste.lista.caminhos, fechamentos)


def _passo_3(ajuste):
    """Proteger a lista: o administrador vira o dono dela e só ele a altera; o usuário da IA a lê, porque as peças
    que ficam de olho na IA a passam à conferência."""
    sistema = ajuste.sistema
    fechamentos = partial(_fechamentos, sistema, set(), set(), sistema.administrador(), None,
                          ajuste.configuracao.usuario_da_ia)
    return _acoes_de_fechar([ajuste.caminho_da_lista], fechamentos)


def _passo_4(ajuste):
    """Proteger esta peça: o administrador vira o dono da configuração dela, da pasta dela e da pasta da central, e
    só ele as altera; o usuário da IA lê a central, porque as peças que ficam de olho na IA usam o código dela."""
    sistema = ajuste.sistema
    so_o_administrador = partial(_fechamentos, sistema, set(), set(), sistema.administrador(), None, None)
    com_leitura = partial(_fechamentos, sistema, set(), set(), sistema.administrador(), None,
                          ajuste.configuracao.usuario_da_ia)
    return (_acoes_de_fechar([ajuste.caminho_da_configuracao, str(PECA)], so_o_administrador)
            + _acoes_de_fechar([str(CENTRAL)], com_leitura))


def _passo_5(ajuste):
    """Abrir o caminho: o usuário da IA ganha o direito de entrar em cada pasta acima dos itens, da lista, da central
    e das pastas de trabalho, pelo caminho escrito e pelo lugar real, e em cada pasta que os itens, a lista e a
    central cobrem. Só nas pastas em que ele ainda não entra."""
    configuracao, sistema = ajuste.configuracao, ajuste.sistema
    vistos, pastas = set(), set()
    for alvo in ajuste.lista.caminhos + [ajuste.caminho_da_lista, str(CENTRAL)]:
        for coberto in cobertos(alvo, vistos):
            pastas.update(_acima(coberto.caminho))
            if coberto.tipo in PASTAS:
                pastas.add(coberto.caminho)
    for pasta in configuracao.pastas_de_trabalho:
        pastas.update(_acima(pasta))
    existentes = sorted(pasta for pasta in pastas if os.path.isdir(pasta))
    return [Acao(pasta, partial(sistema.abre_entrada, configuracao.usuario_da_ia, pasta))
            for pasta in sistema.sem_entrada(configuracao.usuario_da_ia, existentes)]


def _passo_6(ajuste):
    """Abrir as pastas de trabalho para o usuário da IA, com o que está nelas e o que nascer nelas, e manter a pessoa
    alterando tudo o que está nelas."""
    configuracao = ajuste.configuracao
    abre = partial(ajuste.sistema.abre_pasta_de_trabalho, configuracao.usuario_da_ia, configuracao.usuario_da_pessoa)
    return [Acao(pasta, partial(abre, pasta)) for pasta in configuracao.pastas_de_trabalho]


def _passo_7(ajuste):
    """Montar o comando que abre a IA com o usuário da IA: as palavras do pedido de outro usuário, com o nome do
    usuário da IA no lugar marcado, e depois as do comando da IA. O passo só mostra o comando."""
    configuracao = ajuste.configuracao
    pedido = [preenche(palavra, {USUARIO: configuracao.usuario_da_ia}) for palavra in configuracao.pedido_de_outro_usuario]
    return [Acao(ajuste.sistema.mostra_comando(pedido + configuracao.comando_da_ia), None)]


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


def _confere(ajuste, previa):
    """O passo 8: com o usuário da IA, a conferência tenta alterar cada item, e também a lista, a configuração desta
    peça, a pasta desta peça e a pasta da central; a peça mostra cada tentativa que o computador aceitou. Com a
    prévia, só mostra que faria. Dá o código de saída."""
    numero, textos = len(PASSOS) + 1, ajuste.configuracao.textos
    if previa:
        _mostra(textos, "faria", passo=numero, alvo=ajuste.caminho_da_lista)
        return VALENDO
    achados = ajuste.sistema.com_o_usuario(ajuste.configuracao.usuario_da_ia, desprotegidos, _itens(ajuste),
                                           ajuste.lista.pedido_de_administrador)
    _mostra(textos, "fez", passo=numero, alvo=ajuste.caminho_da_lista)
    for caminho, tipo in achados:
        _mostra(textos, "encontrou", caminho=caminho or "", tipo=tipo)
    return NAO_VALENDO if achados else VALENDO


def _ajusta(opcoes):
    """Faz o ajuste, ou a prévia dele, e dá o código de saída."""
    configuracao = _configuracao(opcoes.config)
    lista = le_fechados(opcoes.lista)
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
    _faz_os_passos(ajuste, opcoes.previa)
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
