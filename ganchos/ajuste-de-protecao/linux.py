"""
A parte do Linux do ajuste-de-protecao: o que o ajuste faz com o que o Linux traz.

Os usuários se criam com o useradd, cada um com um grupo só dele. O dono e os direitos de um caminho mudam pelo próprio
Python, pelo arquivo já aberto: assim, uma pasta trocada por um atalho no meio da mudança não desvia a peça para outro
lugar. O direito dado a um usuário só vem do setfacl, a ferramenta das listas de direitos do Linux. O que um usuário
consegue fazer se pergunta ao próprio computador, num pedaço desta peça que deixa de ser o administrador e passa a ser
esse usuário, sem volta; é também com o usuário da pessoa que as pastas de trabalho se abrem. A regra da permissão se
grava num arquivo novo, numa pasta nova só do administrador, e só se liga no lugar depois de conferida.

Dá à peça os nomes que a parte de todo sistema dá: ferramentas_que_faltam, eh_administrador, administrador, existe,
dono, cria_usuario, vira_administrador, fim_com_o_usuario, alteraveis, sem_entrada, sem_leitura, fechado, fecha,
cria_pasta_fechada, da_leitura, abre_entrada, abre_pasta_de_trabalho, so_o_administrador_altera, poe_regra, tira_regra,
mostra_comando e com_o_usuario.

Os erros são o ErroDeDados e os do próprio sistema, quando ele recusa uma mudança.
"""
import errno
import json
import os
import pwd
import shlex
import shutil
import stat
import struct
import tempfile

from erro_de_dados import ErroDeDados
from leitura_de_json import de_json
from leitura_de_texto import CODIFICACAO
from resultado_de_comando import NAO_PASSOU, PASSOU, QUEBROU, resultado

CRIA_USUARIO = ("useradd", "--create-home", "--user-group", "--")  # cria o usuário, com a pasta e um grupo só dele
DA_DIREITOS = "setfacl"  # a ferramenta que dá direitos a um usuário só, numa lista de direitos do caminho
FERRAMENTAS = (CRIA_USUARIO[0], DA_DIREITOS)  # as ferramentas que esta parte usa e que o sistema tem de ter
ADMINISTRADOR = 0  # o número do administrador no Linux
RAIZ = os.path.abspath(os.sep)  # o início do disco, a pasta que todo usuário alcança
ACESSO = "system.posix_acl_access"  # onde o caminho guarda a lista de direitos dada a usuários um a um
HERANCA = "system.posix_acl_default"  # onde a pasta guarda os direitos que passa ao que nasce nela
SEM_LISTA = frozenset({errno.ENODATA, errno.ENOTSUP, errno.EOPNOTSUPP})  # o caminho não tem a lista, ou o disco não a usa
LER, ALTERAR, ENTRAR = stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH  # os direitos de uma classe de usuários, um bit cada
LETRAS = (("r", LER), ("w", ALTERAR), ("x", ENTRAR))  # a letra de cada direito, como o setfacl a escreve
PEDIDOS = ((LER, os.R_OK), (ALTERAR, os.W_OK), (ENTRAR, os.X_OK))  # cada direito e o pedido dele ao os.access
DO_GRUPO = 3  # quantas casas o direito do grupo fica acima do direito dos outros, no número dos direitos
ESCRITA_DOS_OUTROS = stat.S_IWGRP | stat.S_IWOTH  # o direito de alterar, para quem não é o dono
SO_O_DONO = stat.S_IRWXU  # a pasta que só o dono alcança: é como uma pasta nasce, para nada nela estar aberto antes
PASTA_FECHADA = SO_O_DONO | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH  # só o dono altera; todos leem
TUDO = "rwX"  # para o setfacl, ler, alterar e entrar nas pastas, sem tornar programa um arquivo que não é
POR_VEZ = 256  # quantos caminhos vão num só comando do setfacl, para o comando não passar do tamanho que o sistema aceita
VERSAO_DA_LISTA = 2  # a versão com que o Linux grava a lista de direitos de um caminho
CABECA_DA_LISTA = struct.Struct("<I")  # o começo da lista de direitos gravada: a versão
LINHA_DA_LISTA = struct.Struct("<HHI")  # cada linha dela: a marca, os direitos e o número de quem os recebe
UM_USUARIO = 0x02  # a marca da linha da lista de direitos que dá direitos a um usuário só
MODO_DA_REGRA = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH  # a regra: todos leem, e só o administrador altera
FIM_DE_LINHA = "\n"  # o fim de toda linha de um arquivo de texto, também da última


def ferramentas_que_faltam():
    """As ferramentas desta parte que o sistema não tem, em ordem."""
    return [ferramenta for ferramenta in FERRAMENTAS if shutil.which(ferramenta) is None]


def eh_administrador():
    """Se a peça roda como administrador, o usuário que pode tudo."""
    return os.geteuid() == ADMINISTRADOR


def _nome(numero):
    """O nome do usuário do número; o próprio número, quando ele não tem nome."""
    try:
        return pwd.getpwuid(numero).pw_name
    except KeyError:
        return str(numero)


def administrador():
    """O nome do administrador."""
    return _nome(ADMINISTRADOR)


def existe(usuario):
    """Se o usuário existe no computador."""
    try:
        pwd.getpwnam(usuario)
    except KeyError:
        return False
    return True


def _numero(usuario):
    """O número com que o computador guarda o usuário."""
    return pwd.getpwnam(usuario).pw_uid


def dono(caminho):
    """O nome do dono do caminho, sem seguir atalho; o número, quando o dono não tem nome."""
    return _nome(os.lstat(caminho).st_uid)


def _roda(comando):
    """Roda o comando a partir do início do disco. Erro (ErroDeDados) quando ele não passa, com o que ele escreveu na
    saída de erro."""
    feito = resultado(comando, RAIZ)
    if feito.fim != PASSOU:
        raise ErroDeDados(f"{shlex.join(comando)}: {feito.erro.strip()}")


def cria_usuario(usuario):
    """Cria o usuário, com a pasta dele, um grupo só dele e sem senha com que alguém entre no computador com ele. Erro
    (ErroDeDados) quando o useradd não o cria."""
    _roda([*CRIA_USUARIO, usuario])


def _fim_do_pedido(pedido):
    """Como o pedido acabou, rodado a partir do início do disco: PASSOU, NAO_PASSOU ou QUEBROU. O pedido que não
    chega a rodar acaba como QUEBROU."""
    try:
        return resultado(pedido, RAIZ).fim
    except ErroDeDados:
        return QUEBROU


def fim_com_o_usuario(usuario, comando):
    """Como o comando acabou, rodado com o usuário: PASSOU, NAO_PASSOU ou QUEBROU."""
    return com_o_usuario(usuario, _fim_do_pedido, comando)


def vira_administrador(usuario, pedido_de_administrador):
    """Se o usuário consegue rodar como administrador sem senha, pelo pedido de administrador. Só conta como o pedido
    acabou: o que não acaba recusando conta como sim, porque na dúvida o usuário vira administrador."""
    return fim_com_o_usuario(usuario, pedido_de_administrador) != NAO_PASSOU


def _pedido_ao_access(direitos):
    """O pedido ao os.access com os mesmos direitos."""
    pedido = 0
    for direito, do_access in PEDIDOS:
        if direitos & direito:
            pedido |= do_access
    return pedido


def _com_os_direitos_aqui(pedidos):
    """Os caminhos em que quem roda tem os direitos pedidos, na ordem em que vêm. Quem responde é o próprio
    computador."""
    return [caminho for caminho, direitos in pedidos if os.access(caminho, _pedido_ao_access(direitos))]


def _com_os_direitos(usuario, pedidos):
    """Os caminhos em que o usuário tem os direitos pedidos, na ordem em que vêm. O usuário que ainda não existe tem
    só o que o computador deixa qualquer usuário fazer: os direitos dos outros."""
    if not existe(usuario):
        return [caminho for caminho, direitos in pedidos if os.stat(caminho).st_mode & direitos == direitos]
    return com_o_usuario(usuario, _com_os_direitos_aqui, list(pedidos))


def alteraveis(usuario, caminhos):
    """Os caminhos que o usuário consegue alterar, na ordem em que vêm."""
    return _com_os_direitos(usuario, [(caminho, ALTERAR) for caminho in caminhos])


def _sem(usuario, pedidos):
    """Os caminhos em que falta ao usuário algum dos direitos pedidos, na ordem em que vêm."""
    com = set(_com_os_direitos(usuario, pedidos))
    return [caminho for caminho, _ in pedidos if caminho not in com]


def sem_entrada(usuario, pastas):
    """As pastas em que o usuário não consegue entrar, na ordem em que vêm."""
    return _sem(usuario, [(pasta, ENTRAR) for pasta in pastas])


def _leitura(caminho):
    """O direito de ler o caminho: na pasta, ler e entrar, porque só se lê o que está numa pasta entrando nela."""
    return LER | ENTRAR if os.path.isdir(caminho) else LER


def sem_leitura(usuario, caminhos):
    """Os caminhos que o usuário não consegue ler, na ordem em que vêm."""
    return _sem(usuario, [(caminho, _leitura(caminho)) for caminho in caminhos])


def _tem_heranca(alvo):
    """Se o alvo, um caminho ou um arquivo aberto, é uma pasta que passa direitos ao que nasce nela."""
    try:
        return bool(os.getxattr(alvo, HERANCA))
    except OSError as erro:
        if erro.errno in SEM_LISTA:
            return False
        raise


def _tira(alvo, lista):
    """Tira do alvo, um caminho ou um arquivo aberto, a lista de direitos, quando ele a tem."""
    try:
        os.removexattr(alvo, lista)
    except OSError as erro:
        if erro.errno not in SEM_LISTA:
            raise


def fechado(caminho, novo_dono):
    """Se o caminho já está fechado com o novo dono: o novo dono é o dono dele e, fora o atalho, ninguém mais o altera
    nem herda o direito de alterar o que nasce nele."""
    if dono(caminho) != novo_dono:
        return False
    if os.path.islink(caminho):
        return True
    if os.lstat(caminho).st_mode & ESCRITA_DOS_OUTROS:
        return False
    return not (os.path.isdir(caminho) and _tem_heranca(caminho))


def _trocavel(estado, donos_trocaveis):
    """Se o caminho, pelo estado dele, é de um dos donos trocáveis; sem eles (None), todo caminho é."""
    return donos_trocaveis is None or _nome(estado.st_uid) in donos_trocaveis


def _abre_pasta(pasta):
    """A pasta aberta. O que está nela se muda pelo nome, a partir dela: assim, uma pasta do caminho trocada por um
    atalho no meio da mudança não leva a peça para outro lugar."""
    return os.open(pasta, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)


def fecha(caminho, novo_dono, donos_trocaveis):
    """Fecha o caminho: o novo dono vira o dono dele e, fora o atalho, que no Linux não tem direitos próprios, os
    outros deixam de poder alterá-lo, também os que tinham direito dado a eles um a um; a pasta deixa de passar
    direitos ao que nasce nela. A pasta de cima se abre primeiro, e o caminho se abre dentro dela sem seguir atalho: o
    que muda é o arquivo aberto. O caminho de um dono que não está entre os trocáveis fica como está."""
    novo = _numero(novo_dono)
    acima, nome = os.path.split(caminho)
    pasta = _abre_pasta(acima)
    try:
        estado = os.stat(nome, dir_fd=pasta, follow_symlinks=False)
        if not _trocavel(estado, donos_trocaveis):
            return
        if not (stat.S_ISREG(estado.st_mode) or stat.S_ISDIR(estado.st_mode)):
            os.chown(nome, novo, -1, dir_fd=pasta, follow_symlinks=False)
            if not stat.S_ISLNK(estado.st_mode):
                os.chmod(nome, stat.S_IMODE(estado.st_mode) & ~ESCRITA_DOS_OUTROS, dir_fd=pasta)
            return
        aberto = os.open(nome, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=pasta)
    finally:
        os.close(pasta)
    try:
        estado = os.fstat(aberto)
        if not _trocavel(estado, donos_trocaveis):
            return
        os.fchown(aberto, novo, -1)
        os.fchmod(aberto, stat.S_IMODE(estado.st_mode) & ~ESCRITA_DOS_OUTROS)
        if stat.S_ISDIR(estado.st_mode):
            _tira(aberto, HERANCA)
    finally:
        os.close(aberto)


def cria_pasta_fechada(pasta, novo_dono):
    """Cria a pasta já fechada: ela nasce só com o administrador, sem os direitos que a pasta de cima passa ao que nasce
    nela, e só então ganha a leitura de todos e o novo dono. A mudança se faz na pasta já aberta, e não pelo nome."""
    acima, nome = os.path.split(pasta)
    de_cima = _abre_pasta(acima)
    try:
        os.mkdir(nome, SO_O_DONO, dir_fd=de_cima)
        aberta = os.open(nome, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=de_cima)
    finally:
        os.close(de_cima)
    try:
        for lista in (ACESSO, HERANCA):
            _tira(aberta, lista)
        os.fchmod(aberta, PASTA_FECHADA)
        os.fchown(aberta, _numero(novo_dono), -1)
    finally:
        os.close(aberta)


def _letras(direitos):
    """Os direitos escritos como o setfacl os lê."""
    return "".join(letra if direitos & direito else "-" for letra, direito in LETRAS)


def _ja_dados(caminho, numero):
    """Os direitos que a lista de direitos do caminho já dá ao usuário do número, um a um; nenhum quando o caminho não
    tem a lista ou ela não o cita. Erro (ErroDeDados) quando a lista tem uma versão que esta parte não lê."""
    try:
        lista = os.getxattr(caminho, ACESSO)
    except OSError as erro:
        if erro.errno in SEM_LISTA:
            return 0
        raise
    (versao,) = CABECA_DA_LISTA.unpack_from(lista)
    if versao != VERSAO_DA_LISTA:
        raise ErroDeDados(f"{caminho}: lista de direitos de uma versão que esta parte não lê: {versao}")
    direitos = 0
    for inicio in range(CABECA_DA_LISTA.size, len(lista) - LINHA_DA_LISTA.size + 1, LINHA_DA_LISTA.size):
        marca, dados, quem = LINHA_DA_LISTA.unpack_from(lista, inicio)
        if marca == UM_USUARIO and quem == numero:
            direitos |= dados
    return direitos


def _da(usuario, caminho, direitos, mais, menos):
    """Dá ao usuário os direitos no caminho, somados aos que ele já tinha ali, dados a ele um a um. A lista de
    direitos tem um limite comum aos direitos dados um a um; ele parte do que é hoje, que o Linux guarda no lugar do
    direito do grupo, ganha os direitos a mais e perde os a menos. Assim, quem tinha um direito limitado continua
    limitado, e o direito que um passo deu não some no passo seguinte."""
    numero = _numero(usuario)
    hoje = (stat.S_IMODE(os.stat(caminho).st_mode) >> DO_GRUPO) & (LER | ALTERAR | ENTRAR)
    limite = (hoje | mais) & ~menos
    seus = _ja_dados(caminho, numero) | direitos
    _roda([DA_DIREITOS, "-n", "-m", f"u:{numero}:{_letras(seus)},m::{_letras(limite)}", "--", caminho])


def da_leitura(usuario, caminho):
    """Dá ao usuário o direito de ler o caminho, e de entrar nele quando é uma pasta. O limite comum não ganha o
    direito de alterar: o caminho já está fechado, e assim continua."""
    leitura = _leitura(caminho)
    _da(usuario, caminho, leitura, leitura, ALTERAR)


def abre_entrada(usuario, pasta):
    """Dá ao usuário o direito de entrar na pasta, sem tirar o de ler que ele já tinha ali. O limite comum ganha só o
    direito de entrar."""
    _da(usuario, pasta, ENTRAR, ENTRAR, 0)


def _lotes(caminhos):
    """Os caminhos, em partes de POR_VEZ, na ordem."""
    return [caminhos[inicio:inicio + POR_VEZ] for inicio in range(0, len(caminhos), POR_VEZ)]


def _quebra(erro):
    """Para a volta pelas pastas no primeiro erro."""
    raise erro


def _abre_aqui(pasta, direitos):
    """Abre, com quem roda, cada caminho da pasta que é dele: o arquivo e a pasta recebem os direitos, e cada pasta
    passa a dar os mesmos direitos ao que nascer nela. Não segue atalho, e o que é de outro dono fica como está."""
    meu = os.getuid()
    pastas, arquivos = [], []
    for atual, de_dentro, nomes in os.walk(pasta, onerror=_quebra):
        de_dentro.sort()
        if os.lstat(atual).st_uid == meu:
            pastas.append(atual)
        for nome in sorted(nomes):
            caminho = os.path.join(atual, nome)
            estado = os.lstat(caminho)
            if stat.S_ISREG(estado.st_mode) and estado.st_uid == meu:
                arquivos.append(caminho)
    for lote in _lotes(pastas + arquivos):
        _roda([DA_DIREITOS, "-m", direitos, "--", *lote])
    for lote in _lotes(pastas):
        _roda([DA_DIREITOS, "-d", "-m", direitos, "--", *lote])


def abre_pasta_de_trabalho(usuarios, usuario_da_pessoa, pasta):
    """Abre a pasta de trabalho para os usuários e para o da pessoa, com o que está nela e o que nascer nela depois. O
    trabalho se faz com o usuário da pessoa, e não como administrador: assim, só muda o que já é da pessoa, mesmo que
    algo mude na pasta enquanto a peça trabalha. A pasta se trata pelo lugar a que ela leva."""
    direitos = ",".join(f"u:{_numero(usuario)}:{TUDO}" for usuario in (*usuarios, usuario_da_pessoa))
    com_o_usuario(usuario_da_pessoa, _abre_aqui, os.path.realpath(pasta), direitos)


def so_o_administrador_altera(caminho):
    """Se só o administrador altera o caminho: ele é o dono, e nem o grupo nem os outros têm o direito de alterar. Com
    direitos dados a usuários um a um, o direito do grupo é o limite comum deles: sem ele, nenhum deles altera."""
    estado = os.stat(caminho)
    return estado.st_uid == ADMINISTRADOR and not estado.st_mode & ESCRITA_DOS_OUTROS


def _tira_se_existe(caminho):
    """Apaga o arquivo, quando ele existe."""
    try:
        os.unlink(caminho)
    except FileNotFoundError:
        pass


def poe_regra(arquivo, texto, passa):
    """Põe a regra no arquivo: grava o texto num arquivo novo, que já nasce fechado, numa pasta nova que só o
    administrador alcança, ao lado da pasta do arquivo, e confere o arquivo novo com o passa, que recebe o caminho dele
    e diz se a regra está certa. Só com a regra certa o arquivo novo se liga no lugar, de uma vez, e só se o lugar
    ainda estiver vazio. Devolve se a regra foi posta; a recusada não muda nada."""
    linhas = texto if texto.endswith(FIM_DE_LINHA) else texto + FIM_DE_LINHA
    pasta_nova = tempfile.mkdtemp(dir=os.path.dirname(os.path.dirname(arquivo)))
    novo = os.path.join(pasta_nova, os.path.basename(arquivo))
    try:
        descritor = os.open(novo, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, MODO_DA_REGRA)
        with os.fdopen(descritor, "w", encoding=CODIFICACAO) as saida:
            saida.write(linhas)
            saida.flush()
            os.fsync(saida.fileno())
        if not passa(novo):
            return False
        os.link(novo, arquivo)
        return True
    finally:
        _tira_se_existe(novo)
        os.rmdir(pasta_nova)


def tira_regra(arquivo):
    """Tira o arquivo da regra que a peça pôs."""
    os.unlink(arquivo)


def mostra_comando(comando):
    """O comando escrito como o terminal do Linux o lê."""
    return shlex.join(comando)


def _no_pedaco(conta, escrita, funcao, argumentos):
    """O que o pedaço faz: passa a ser o usuário da conta, roda a função a partir do início do disco e escreve a
    resposta em JSON, ou o erro. Sai sem voltar ao código de quem o criou."""
    codigo = 1
    try:
        os.setgroups(os.getgrouplist(conta.pw_name, conta.pw_gid))
        os.setgid(conta.pw_gid)
        os.setuid(conta.pw_uid)
        os.chdir(RAIZ)
        resposta = json.dumps(funcao(*argumentos))
        codigo = 0
    except BaseException as erro:
        resposta = str(erro)
    try:
        with os.fdopen(escrita, "w", encoding=CODIFICACAO) as saida:
            saida.write(resposta)
    finally:
        os._exit(codigo)


def com_o_usuario(usuario, funcao, *argumentos):
    """A resposta da função, rodada com o usuário. Quem a roda é um pedaço desta peça: uma cópia do que está rodando,
    que troca de usuário, roda a função e devolve a resposta. A troca não tem volta: o pedaço não volta a ser
    administrador. Erro (ErroDeDados) quando a função dá erro no pedaço."""
    conta = pwd.getpwnam(usuario)
    leitura, escrita = os.pipe()
    pedaco = os.fork()
    if pedaco == 0:
        os.close(leitura)
        _no_pedaco(conta, escrita, funcao, argumentos)
    os.close(escrita)
    with os.fdopen(leitura, encoding=CODIFICACAO) as entrada:
        resposta = entrada.read()
    _, fim = os.waitpid(pedaco, 0)
    origem = f"com o usuário {usuario}"
    if os.waitstatus_to_exitcode(fim) != 0:
        raise ErroDeDados(f"{origem}: {resposta}")
    return de_json(resposta, origem)
