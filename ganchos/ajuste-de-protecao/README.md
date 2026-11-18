# ajuste-de-protecao

Faz no computador o ajuste que impede a IA de alterar os arquivos das peças que ficam de olho
nela.

## Para que serve

Algumas peças da prateleira ficam de olho na IA. Cada uma tem arquivos próprios: as anotações
do que a IA fez, as regras que a peça cobra e a configuração dela. Se a IA alterar um desses
arquivos, a peça continua respondendo, mas a resposta já não vale.

Quem impede a IA de alterar os arquivos das peças é o próprio computador. No computador, todo
programa roda com um usuário. Cada arquivo guarda os direitos dele: quais usuários podem lê-lo e
quais podem alterá-lo. O
[README da conferencia-de-protecao](../../central/conferencia-de-protecao/README.md) explica por
que só o computador resolve e o que precisa estar feito nele.

Para o computador impedir, é preciso um ajuste. O ajuste cria dois usuários:

- **o usuário da IA:** com ele rodam as ações da IA. Ação da IA é o que ela manda o computador
  rodar, como um comando no terminal ou um programa que ela escreveu;
- **o usuário do programa:** com ele rodam o programa da IA e as peças que ficam de olho nela.

Depois, o ajuste fecha para o usuário da IA os arquivos dessas peças. Fechar quer dizer que o
usuário da IA lê o arquivo, mas não o altera.

Cada sistema faz esse ajuste com comandos próprios. Esta peça faz o ajuste inteiro: a pessoa
roda um comando, e a peça faz o que o sistema dela pede.

Exemplo: a pessoa roda esta peça. A peça cria os dois usuários, fecha os arquivos das peças que
ficam de olho na IA e deixa pronto o comando que abre o programa da IA com o usuário do
programa. Dali em diante, a pessoa abre o programa por esse comando. Quando a IA manda o
computador apagar as anotações de uma peça, o computador recusa.

## Como funciona

A pessoa roda esta peça como administrador. O administrador é o usuário que pode tudo no
computador. Só ele cria usuários e muda os direitos dos arquivos de outros usuários.

Antes de rodar a peça, a pessoa fecha o programa da IA. Antes do ajuste, a IA roda com o usuário
da pessoa e altera as pastas dela. Enquanto a peça troca donos e direitos, a IA poderia trocar uma
pasta por um atalho, que é um arquivo que leva a outro lugar. A peça, que pode tudo, mudaria então
o lugar para onde o atalho leva, que pode ser um arquivo do próprio sistema. Com a IA fechada,
nada troca as pastas enquanto a peça trabalha.

A peça recebe do projeto duas coisas: a configuração dela e a lista. A lista traz os arquivos e
as pastas que a IA não pode alterar. Cada arquivo ou pasta da lista é um item. Por exemplo, o
arquivo em que uma peça anota o que a IA fez é um item. A lista traz também o nome do usuário da
IA e o do usuário do programa. É a mesma lista que a conferencia-de-protecao usa para conferir o
ajuste. Assim, o que esta peça fecha é o que a conferência testa.

A configuração diz quais são as pastas de trabalho. A pasta de trabalho é a pasta em que a IA
faz o trabalho dela, como a pasta do projeto.

Todo arquivo tem um dono, que é um usuário. O dono decide os direitos do arquivo: quem lê e quem
altera. Por isso, o dono de um arquivo sempre consegue voltar a alterá-lo.

As peças que ficam de olho na IA escrevem em alguns itens, como o das anotações. A configuração
diz quais são. Esses itens ficam com o usuário do programa como dono, porque as peças rodam com
ele. Os outros itens, como o código e a configuração das peças, ficam com o administrador como
dono, porque ninguém precisa alterá-los no dia a dia.

O programa da IA roda com o usuário do programa, e não com o usuário da pessoa, por dois motivos:

- As ferramentas do próprio programa, como a de editar um arquivo, rodam com o mesmo usuário que
  ele. Com o usuário do programa, as ferramentas do programa só alteram as pastas de trabalho, os
  itens em que as peças escrevem e a pasta própria do usuário do programa. Os arquivos da pessoa
  ficam fora do alcance das ferramentas do programa.
- Alguns programas da pessoa, como o editor de código, rodam sozinhos certos arquivos da pasta de
  trabalho, por exemplo ao abrir a pasta. A IA escreve na pasta de trabalho. Então, o que a IA
  escreve ali pode acabar rodando com o usuário da pessoa. Como a pessoa não é dona de nenhum
  item, o que roda assim não altera os itens.

Depois do ajuste, o computador recusa a cada usuário o seguinte:

| O usuário | Com ele rodam | O computador recusa |
| --- | --- | --- |
| o usuário da IA | as ações da IA | alterar qualquer item |
| o usuário do programa | o programa da IA, as ferramentas dele e as peças que ficam de olho na IA | alterar os itens em que as peças não escrevem |
| o usuário da pessoa | os programas da pessoa | alterar qualquer item |

Nos itens em que as peças escrevem, o computador deixa o usuário do programa alterar, porque as
peças precisam escrever ali. Nesses itens, quem barra as ferramentas do programa são as próprias
peças, que o programa chama antes de cada uso (ver
[o que precisa estar feito no computador](../../central/conferencia-de-protecao/README.md#o-que-precisa-estar-feito-no-computador)).

Antes do passo 1, a peça confere se o computador está pronto para o ajuste. Se algo não está
certo, ela para sem mudar nada e diz o quê (ver "O que a peça confere antes do ajuste").

Com a opção de prévia, a peça faz só as conferências e mostra o que faria, sem mudar nada. Assim,
a pessoa vê o ajuste antes de ele ser feito.

Com tudo certo, a peça faz o ajuste em oito passos, nesta ordem.

### Passo 1: criar os usuários

**O que é.** Um usuário é uma conta do computador, como a conta com que uma pessoa entra nele.
Ele tem um nome e uma pasta própria. Criar um usuário é fazer o computador passar a ter mais uma
dessas contas.

**Por quê.** O computador decide o que um programa pode fazer olhando o usuário com que o
programa roda. Para o computador tratar de um jeito as ações da IA, de outro o programa com as
peças e de outro a pessoa, cada um precisa de um usuário só seu.

**Na prática.** A peça cria o usuário da IA e o usuário do programa. Nenhuma pessoa entra no
computador com eles: o usuário da IA existe para as ações da IA, e o usuário do programa, para o
programa da IA e as peças. Um usuário que já existe a peça não cria de novo.

### Passo 2: fechar os itens

**O que é.** Fechar um item é deixar só o dono alterá-lo, com o dono certo: o usuário do
programa, nos itens em que as peças escrevem, e o administrador, nos outros. Quem lia o item
continua lendo. O usuário do programa também lê todos os itens, porque as peças, que rodam com
ele, leem os próprios arquivos. O usuário da IA também lê, porque é com ele que a
conferencia-de-protecao percorre os itens para testá-los. Se o usuário do programa ou o usuário
da IA não lia, a peça lhe dá o direito de ler, e só esse.

**Por quê.** É este passo que impede a IA de mexer nos arquivos das peças que ficam de olho
nela. O dono não pode ser o usuário da IA, porque o dono sempre consegue voltar a alterar o
arquivo. E o dono dos itens em que as peças não escrevem é o administrador para que nem as
ferramentas do programa os alterem.

**Na prática.** Depois deste passo, quando uma ação da IA tenta alterar um item, o computador
recusa. Quando uma ferramenta do programa tenta alterar um item em que as peças não escrevem, o
computador também recusa. A peça só troca o dono de um item que pertence à pessoa, ao usuário da
IA ou ao usuário do programa. Um item de outro dono, como um arquivo do próprio sistema, ela deixa
com o dono que tem (ver "O que a peça confere antes do ajuste").

Cada tipo de item pede um cuidado. Um dos tipos é o atalho, que funciona como os atalhos da área
de trabalho: um arquivo pequeno que leva a outro arquivo, guardado em outro lugar. Quem abre o
atalho abre, na verdade, o outro arquivo.

| O item | O que a peça fecha | Por quê |
| --- | --- | --- |
| um arquivo | o arquivo | é ele que a IA alteraria |
| uma pasta | a pasta e tudo o que está dentro dela | cada arquivo de dentro tem os seus próprios direitos, e um pode estar aberto sem que os outros estejam |
| um arquivo que ainda não existe | a pasta em que ele vai aparecer, sem o que já está dentro dela; essa pasta passa a contar como o item | com a pasta aberta, a IA criaria ali um arquivo com o nome que a peça que fica de olho nela vai usar, e essa peça o leria como seu |
| um atalho | o atalho e o arquivo para onde ele leva, que também conta como item | fechar só o atalho deixaria aberto o arquivo para onde ele leva |

Às vezes, a pasta em que o arquivo que ainda não existe vai aparecer também não existe. Nesse
caso, a peça cria essa pasta já fechada, junto com as pastas que faltam no caminho até ela.
Assim, o passo tem a pasta para fechar, e a peça que vai escrever o arquivo encontra a pasta
pronta para criá-lo.

Para um atalho que está dentro de uma pasta da lista, a peça não vai atrás do arquivo para onde
ele leva (ver "O que a peça confere antes do ajuste").

### Passo 3: proteger a lista

**O que é.** A lista é o arquivo que diz quais itens ficam fechados e quais são o usuário da IA
e o usuário do programa.

**Por quê.** Quem alterasse a lista poderia tirar um item dela. Esse item deixaria de ser
fechado e de ser testado pela conferência, sem que ninguém percebesse. Poderia também trocar o
nome de um dos usuários, e a conferência passaria a testar outro usuário.

**Na prática.** A peça faz o administrador virar o dono da lista e deixa só ele alterá-la. Para
mudar a lista, a pessoa usa o administrador. O usuário do programa lê a lista, porque as peças,
que rodam com ele, a passam à conferencia-de-protecao.

### Passo 4: proteger esta peça

**O que é.** Esta peça é feita de arquivos: a configuração dela, a pasta com o código dela e a
pasta da central. A central é a pasta da prateleira que guarda o código que mais de uma peça
usa, e esta peça usa código de lá.

**Por quê.** Esta peça roda como administrador, que pode tudo. Se alguém alterasse um desses
arquivos, na próxima vez que a pessoa rodasse a peça, o que esse alguém escreveu também rodaria
podendo tudo.

**Na prática.** A peça faz o administrador virar o dono da configuração dela, da pasta dela e da
pasta da central, e deixa só ele alterá-las. O usuário do programa e o usuário da IA leem a
central: as peças, que rodam com o usuário do programa, usam o código dela, e a
conferencia-de-protecao, que fica nela, faz as tentativas com o usuário da IA.

### Passo 5: abrir o caminho até os arquivos

**O que é.** Todo arquivo fica dentro de pastas, uma dentro da outra. Para chegar a um arquivo,
um usuário precisa ter o direito de entrar em cada pasta do caminho até ele. Entrar numa pasta
não é alterá-la: quem só entra não cria, não apaga e não troca nada nela.

**Por quê.** O usuário do programa e o usuário da IA precisam chegar a certos arquivos para fazer
o seu trabalho. Com o caminho fechado, os dois não chegam, e nada funciona.

**Na prática.** A peça dá a cada usuário o direito de entrar nas pastas dos caminhos de que ele
precisa, e só esse direito:

| O usuário | Chega a | Para quê |
| --- | --- | --- |
| o usuário do programa | os itens, a lista, a central e as pastas de trabalho | as peças usam os próprios arquivos; as ferramentas do programa trabalham nas pastas de trabalho |
| o usuário da IA | os itens, a central e as pastas de trabalho | a conferência faz as tentativas nos itens; a IA trabalha nas pastas de trabalho |

Quando um caminho passa por um atalho, a peça abre também as pastas do lugar a que o atalho leva,
porque é por elas que o computador passa.

Quando uma pasta de trabalho fica dentro da pasta própria da pessoa, o usuário do programa e o
usuário da IA passam a entrar nessa pasta. Lá dentro, os dois leem tudo o que o computador deixa
qualquer usuário ler. Por isso, é melhor a pasta de trabalho ficar fora da pasta própria da
pessoa.

### Passo 6: abrir as pastas de trabalho

**O que é.** Abrir uma pasta para um usuário é dar a ele o direito de alterar o que está nela.

**Por quê.** A IA precisa alterar os arquivos do projeto, porque esse é o trabalho dela. As
ferramentas do programa também, como a de editar um arquivo. O usuário da IA e o usuário do
programa são novos e, sem este passo, não alteram nenhum arquivo da pessoa.

**Na prática.** A peça abre as pastas de trabalho para o usuário da IA e para o usuário do
programa, com tudo o que está nelas e o que surgir nelas depois. A pessoa continua alterando tudo
o que está nelas, também o que a IA e o programa criarem.

Há um limite. Um programa pode criar um arquivo já fechado, só para o dono dele. O direito da
pessoa não passa do que esse arquivo deixa. Se a IA ou o programa criar um arquivo assim, a pessoa
só mexe nele usando o administrador.

A peça faz este passo com o usuário da pessoa, e não como administrador. Assim, ela só mexe no que
já é da pessoa, mesmo que algo mude nas pastas enquanto ela trabalha.

### Passo 7: deixar pronto o jeito de abrir o programa

**O que é.** Depois do ajuste, o programa da IA roda com o usuário do programa e pede ao
computador que rode cada ação da IA com o usuário da IA. Para isso, três coisas ficam prontas: o
comando que abre o programa com o usuário do programa; a permissão de o usuário do programa rodar
um comando com o usuário da IA sem digitar senha; e as palavras com que o programa faz esse
pedido.

**Por quê.** Se o programa rodar com o usuário da pessoa, as ferramentas dele alteram tudo o que
a pessoa altera. Se as ações da IA rodarem com o usuário do programa, a IA altera os itens em que
as peças escrevem. Nos dois casos, os passos anteriores não bastam. A permissão é sem senha
porque o programa faz o pedido a cada ação da IA, e ninguém está ali para digitar a senha.

**Na prática.** Cada computador dá essa permissão com uma ferramenta própria, e cada ferramenta
tem o seu arquivo de regras e o seu jeito de escrever uma regra. Por isso, a configuração traz a
regra, já escrita no jeito da ferramenta do computador, o caminho do arquivo em que ela fica e o
comando que confere a regra antes de ela valer.

A peça grava a regra num arquivo novo, que já nasce fechado, numa pasta que só o administrador
altera e que não é a pasta do arquivo da regra. Depois, confere esse arquivo novo com o comando
da configuração e só então o põe no lugar. Se o comando recusa a regra, nada muda, e a peça para
no passo. Se o arquivo da regra já existe e já traz a regra, a peça não mexe nele.

A permissão vale num sentido só: o usuário do programa roda um comando com o usuário da IA, que
pode menos. Com a regra no lugar, a peça prova isso por três tentativas:

| A tentativa | O resultado certo |
| --- | --- |
| o usuário do programa roda um comando com o usuário da IA, sem senha | o computador aceita |
| o usuário da IA roda um comando com o usuário do programa, sem senha | o computador recusa |
| o usuário do programa roda como administrador, sem senha | o computador recusa |

Se uma tentativa não dá o resultado certo, a peça tira a regra que pôs, mostra qual tentativa foi
e para. A conferencia-de-protecao usa a mesma permissão para fazer as tentativas com o usuário da
IA.

A peça monta o comando que abre o programa e as palavras do pedido, e os mostra no fim. A pessoa
põe as palavras na configuração do programa da IA, uma vez, porque cada programa se configura do
seu jeito. Onde fica essa configuração, e o que mais o programa precisa ter, como barrar a ação
quando uma peça não responde, está em
[o que precisa estar feito no computador](../../central/conferencia-de-protecao/README.md#o-que-precisa-estar-feito-no-computador).

O comando, a pessoa o usa com o mesmo poder de administrador com que roda esta peça. Assim, o que
roda com o usuário da pessoa, como um arquivo que a IA escreveu e um programa da pessoa rodou
sozinho, não consegue rodar com o usuário do programa.

### Passo 8: conferir o ajuste

**O que é.** A conferencia-de-protecao testa se o computador está mesmo recusando. Com o usuário
da IA, ela tenta alterar cada item, por tentativas que não mudam nada. Ela testa também a lista, a
configuração desta peça, a pasta desta peça e a pasta da central: a lista diz o que fica fechado,
e o resto roda como administrador na próxima vez que a pessoa rodar esta peça.

A peça roda a conferência com o usuário do programa, do mesmo jeito que as peças a rodam. Assim, a
conferência passa também pela permissão do passo 7.

**Por quê.** Um ajuste pode parecer feito e não estar valendo. Só a tentativa mostra se o
computador recusa.

**Na prática.** Se o computador recusar todas as tentativas, o ajuste está valendo. Se aceitar
alguma, ou se alguma não chegar a ser feita, a peça mostra onde. No fim, a peça mostra o que fez,
o comando que abre o programa, as palavras do pedido e o que a conferência encontrou.

### Depois do ajuste

Quando a lista muda, a pessoa roda a peça de novo. O usuário da IA e o usuário do programa, que
já existem, continuam os mesmos.

Para mudar um item, a pessoa usa o administrador.

Se a pessoa abrir o programa da IA de outro jeito, ele roda com o usuário dela. A conferência
percebe que não está rodando com o usuário do programa, e as peças que ficam de olho na IA não
deixam a IA agir.

Com o usuário do programa, o programa da IA começa sem a configuração que tinha com o usuário da
pessoa, e pode pedi-la de novo.

### A primeira vez

Na primeira vez, o código desta peça pode já ter sido alterado. Antes do ajuste, a IA roda com o
usuário da pessoa e alcança os arquivos dela, e esta peça roda como administrador o que estiver
ali. Por isso, na primeira vez, a pessoa baixa a prateleira de novo, de onde ela veio, numa pasta
que só o administrador altera, e roda esta peça de lá.

## O que a peça confere antes do ajuste

Antes do passo 1, a peça olha o computador e confere cada linha da tabela abaixo. Nessa hora, ela
não muda nada. Se uma linha não está certa, a peça para e diz qual e onde. A pessoa acerta e roda
a peça de novo.

Nesta conferência, a lista, a configuração desta peça, a pasta desta peça e a pasta da central
também contam como itens.

Quando o usuário da IA ou o usuário do programa ainda não existe, a peça confere o que um usuário
novo conseguiria fazer, que é o que o computador deixa qualquer usuário fazer.

As pastas acima de um item contam pelo caminho escrito e, quando esse caminho passa por um atalho,
também pelo lugar a que o atalho leva, porque é por ali que o computador passa.

| Para o passo | A peça confere que | Se não estivesse certo |
| --- | --- | --- |
| todos | ela está rodando como administrador | o computador recusaria a primeira mudança |
| 1 | o usuário da IA não tem o nome da pessoa nem o do usuário do programa | a IA teria os direitos desse usuário, e nada ficaria fechado para ela |
| 1 | o usuário do programa não tem o nome da pessoa | as ferramentas do programa alterariam tudo o que a pessoa altera |
| 1 | o usuário da IA e o usuário do programa, se já existem, não viram administrador sem senha | como administrador, a IA ou o programa abriria de novo o que a peça fechasse |
| 2 | nenhum item está dentro de uma pasta de trabalho | a IA poderia trocar a pasta do item por outra (ver abaixo) |
| 2 | nenhuma pasta acima de um item está aberta para o usuário da IA, e nenhuma pasta acima de um item em que as peças não escrevem está aberta para o usuário do programa | o mesmo risco, numa pasta que não é de trabalho, como uma que todos os usuários alteram; nos itens em que as peças escrevem, o usuário do programa já altera o item |
| 2 | cada atalho de dentro das pastas da lista leva a um arquivo que também está na lista | o arquivo do outro lado ficaria aberto; a peça não vai atrás dele sozinha, porque ele pode ser um arquivo do sistema |
| 2 | cada item de outro dono, como um arquivo do sistema, já está fechado para o usuário da IA e para o usuário do programa | ele ficaria aberto; a peça não troca o dono de um arquivo que não é da pessoa, do usuário da IA nem do usuário do programa |
| 2 | cada item em que as peças escrevem é da pessoa, do usuário da IA ou do usuário do programa | a peça não entregaria ao usuário do programa um arquivo de outro dono, e as peças não conseguiriam escrever nele |
| 2 | nenhum item em que as peças não escrevem está dentro de um item em que elas escrevem | o usuário do programa, que altera o item de fora, trocaria o de dentro por outro |
| 2 | a pasta em que um item que ainda não existe vai aparecer guarda só itens e as pastas que levam a eles | fechar essa pasta tiraria da pessoa o direito de criar coisas nela, e o que não é item ficaria lá dentro sem ser fechado |
| 6 | nenhuma pasta de trabalho está dentro de um item | fechar o item fecharia junto a pasta de trabalho, e a IA não conseguiria trabalhar |
| 6 | tudo o que está nas pastas de trabalho é da pessoa, do usuário da IA ou do usuário do programa | o passo 6 daria à IA e ao programa o direito de alterar um arquivo de outro dono, como um arquivo do sistema |
| 7 | só o administrador altera o arquivo da regra, quando ele já existe, a pasta dele e as pastas acima dela | quem alterasse o arquivo mudaria a regra, e quem alterasse uma das pastas trocaria o arquivo por outro, com outra permissão |
| 7 | o arquivo da regra não existe, ou já traz a regra | o arquivo pode ter regras de outros programas, e a peça não o escreve por cima; a pessoa põe a regra nele à mão |

**Por que a pasta de cima importa.** Quem consegue alterar uma pasta consegue trocar o nome do que
está dentro dela e pôr outra coisa no lugar, com o nome antigo. Se a IA alterasse a pasta em que
está um item, ela trocaria o nome da pasta do item e criaria outra com o mesmo nome. A peça que
fica de olho na IA passaria a usar a pasta que a IA criou. O mesmo vale para as ferramentas do
programa. Por isso, a prateleira e os dados das peças ficam fora das pastas de trabalho. A peça não
fecha sozinha uma pasta de cima que está aberta: fechar uma pasta muda as regras para tudo o que
está nela, e não só para o item.

## Como ligar num projeto

O comando roda como administrador. Cada sistema tem o seu jeito de rodar um comando como
administrador, e o comando abaixo vem depois dele:

    python3 -I <pasta da central>/roda/roda.py <pasta desta peça>/ajuste_de_protecao.py --config <configuração> --lista <lista>

Para ver o ajuste antes, sem mudar nada, o mesmo comando leva também a opção `--previa`.

O projeto guarda, nas pastas de dados dele:

- a configuração desta peça;
- a lista dos itens fechados para a IA, a mesma que as peças que ficam de olho na IA passam à
  conferencia-de-protecao.

## Detalhes

### As opções do comando

| Opção | O que recebe |
| --- | --- |
| `--config` | o caminho da configuração desta peça |
| `--lista` | o caminho da lista, na forma que a [conferencia-de-protecao](../../central/conferencia-de-protecao/README.md#a-lista) pede |
| `--previa` | nada; com ela, a peça faz só as conferências e mostra o que faria, sem mudar nada |

### A configuração

Um arquivo em JSON, que é um jeito de escrever dados. A forma que ele tem de ter está no molde
`esquemas/ajuste-de-protecao.schema.json`.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `usuario_da_pessoa` | o nome do usuário da pessoa, que altera as pastas de trabalho junto com a IA e o programa |
| `pastas_de_trabalho` | os caminhos das pastas que a IA e o programa alteram |
| `escritos_pelas_pecas` | os caminhos dos itens em que as peças escrevem; cada um é também um caminho da lista |
| `comando_do_programa` | as palavras do comando que abre o programa da IA; a primeira palavra é o programa |
| `regra_da_permissao` | a regra que dá a permissão do passo 7, escrita no jeito da ferramenta deste computador; os lugares `{usuario_do_programa}` e `{usuario_da_ia}` marcam onde vão os nomes |
| `arquivo_da_regra` | o caminho do arquivo em que a regra fica |
| `conferencia_da_regra` | as palavras do comando que confere um arquivo de regra antes de ela valer; a primeira palavra é o programa, e a palavra `{arquivo}` marca o lugar do caminho do arquivo |
| `textos` | os textos que a peça mostra: um para cada conferência que falha, um para cada problema da permissão do passo 7, um para o que ela fez, um para o que ela faria, na prévia, e um para o que a conferência encontrou (ver [Os textos](#os-textos)) |

Os nomes do usuário da IA e do usuário do programa e as palavras do pedido para rodar um comando
com outro usuário vêm da lista, na forma que a
[conferencia-de-protecao](../../central/conferencia-de-protecao/README.md#a-lista) pede.

Caminho é o endereço de um arquivo no disco. O caminho que não começa no início do disco conta a
partir da pasta da configuração.

### Os textos

Cada texto é um modelo: um texto com lugares marcados entre chaves, que a peça preenche (ver
[modelo-de-texto](../../central/modelo-de-texto/README.md)).

| Chave | Quando a peça mostra | Lugares |
| --- | --- | --- |
| `sistema_nao_atendido` | o sistema não tem a sua parte da peça | `{sistema}` |
| `falta_ferramenta` | falta uma ferramenta que a parte do sistema usa | `{ferramenta}` |
| `sem_administrador` | a peça não está rodando como administrador | nenhum |
| `ia_com_nome_repetido` | o usuário da IA tem o nome da pessoa ou o do usuário do programa | `{usuario}` |
| `programa_com_nome_da_pessoa` | o usuário do programa tem o nome da pessoa | `{usuario}` |
| `vira_administrador` | o usuário da IA ou o usuário do programa vira administrador sem senha | `{usuario}` |
| `item_em_pasta_de_trabalho` | um item está dentro de uma pasta de trabalho | `{item}`, `{pasta}` |
| `pasta_acima_aberta` | uma pasta acima de um item está aberta para o usuário da IA ou, num item em que as peças não escrevem, para o usuário do programa | `{pasta}`, `{item}`, `{usuario}` |
| `atalho_para_fora` | um atalho de dentro de uma pasta da lista leva a um arquivo que não está na lista | `{atalho}`, `{destino}` |
| `item_de_outro_dono_aberto` | um item de outro dono está aberto para o usuário da IA ou para o usuário do programa | `{item}`, `{dono}`, `{usuario}` |
| `escrito_de_outro_dono` | um item em que as peças escrevem é de outro dono | `{item}`, `{dono}` |
| `item_dentro_de_escrito` | um item em que as peças não escrevem está dentro de um item em que elas escrevem | `{item}`, `{escrito}` |
| `onde_vai_aparecer_com_outros` | a pasta em que um item que ainda não existe vai aparecer guarda algo que não é item nem leva a um | `{pasta}`, `{caminho}` |
| `pasta_de_trabalho_em_item` | uma pasta de trabalho está dentro de um item | `{pasta}`, `{item}` |
| `pasta_de_trabalho_com_outro_dono` | algo numa pasta de trabalho é de outro dono | `{caminho}`, `{dono}` |
| `pasta_da_regra_aberta` | o arquivo da regra, ou uma pasta do caminho dele, é alterado por outro usuário que não o administrador | `{pasta}` |
| `arquivo_da_regra_sem_a_regra` | o arquivo da regra já existe e não traz a regra | `{arquivo}`, `{regra}` |
| `regra_recusada` | o comando que confere a regra a recusou | `{arquivo}` |
| `permissao_errada` | uma tentativa do passo 7 não deu o resultado certo, e a peça tirou a regra que pôs | `{tentativa}` |
| `fez` | cada coisa que a peça fez | `{passo}`, `{alvo}` |
| `faria` | na prévia, cada coisa que a peça faria | `{passo}`, `{alvo}` |
| `encontrou` | cada linha que a conferência do passo 8 entregou | `{caminho}`, `{tipo}` |

O `{passo}` é o número do passo. O `{alvo}` é o usuário criado, o caminho que mudou, a regra
posta, o comando que abre o programa ou as palavras do pedido. A `{regra}` é a regra da
configuração, com os nomes no lugar. A `{tentativa}` é uma das três do passo 7:
`programa_como_ia`, `ia_como_programa` ou `programa_como_administrador`. O `{caminho}` e o
`{tipo}` são os que a
[conferencia-de-protecao](../../central/conferencia-de-protecao/README.md#desprotegidos)
entrega; quando a linha não é de nenhum arquivo, como a tentativa de virar administrador, o
`{caminho}` fica vazio.

### Os sistemas

Cada tipo de sistema tem a sua parte da peça, que usa só as ferramentas que esse sistema já traz.
O que muda dentro de um mesmo tipo de sistema vem dos dados do projeto, como o pedido para rodar um
comando com outro usuário, que está na lista, e a regra da permissão, que está na configuração.
Num sistema que a peça não atende, ou em que falta uma dessas ferramentas, ela para sem mudar nada
e diz o que falta.

| Sistema | As ferramentas que ele tem de ter |
| --- | --- |
| Linux | `useradd`, que cria usuários, e `setfacl`, que dá direitos a um usuário só |

### Os arquivos de código

| Arquivo | O que faz |
| --- | --- |
| `ajuste_de_protecao.py` | lê a configuração e a lista, faz as conferências de antes do ajuste e os oito passos, ou a prévia, e mostra os textos |
| `linux.py` | a parte do Linux: o que o ajuste faz com o que o Linux traz, como criar os usuários e a permissão, fechar e abrir os caminhos e rodar a conferência com o usuário do programa |

O arquivo da parte de um sistema tem o nome que o Python dá a esse sistema. A parte de outro
sistema dá os mesmos nomes que a do Linux, cada um com o mesmo serviço.

### O que dá erro

A peça dá erro, sem mudar nada, quando a configuração ou a lista não seguem o molde. O erro diz
o arquivo e o lugar do valor errado.

Dá erro também, sem mudar nada, quando o usuário da pessoa não existe no computador, quando uma
pasta de trabalho não existe, quando um dos itens em que as peças escrevem não está na lista,
quando a regra da permissão não traz os lugares `{usuario_do_programa}` e `{usuario_da_ia}` ou
traz um lugar com outro nome, quando o comando que confere a regra não traz o lugar `{arquivo}`
ou traz outro, e quando um texto traz um lugar que não é dele. Se um passo não dá certo, a peça
para nele, mostra o que já fez e dá o erro do passo.

### Como a peça termina

Quando acaba, o comando entrega um número, o código de saída, que diz como foi:

| Código de saída | Quando |
| --- | --- |
| 0 | o ajuste foi feito e a conferência do passo 8 não achou nada; na prévia, as conferências de antes passaram |
| 1 | uma conferência de antes do ajuste não passou, uma tentativa do passo 7 não deu o resultado certo, ou a conferência do passo 8 achou alguma coisa |
| outro | a peça não conseguiu fazer o trabalho: erro nos dados, um passo que não deu certo ou uma quebra da própria peça |

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
