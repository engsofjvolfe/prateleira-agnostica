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
que só o computador resolve.

Para o computador impedir, é preciso um ajuste. O ajuste cria um usuário só para a IA: o usuário
da IA. Faz o programa da IA rodar com o usuário da IA. E fecha para o usuário da IA os arquivos
das peças que ficam de olho nela. Fechar quer dizer que o usuário da IA lê o arquivo, mas não o
altera.

Cada sistema faz esse ajuste com comandos próprios. Esta peça faz o ajuste inteiro: a pessoa
roda um comando, e a peça faz o que o sistema dela pede.

Exemplo: a pessoa roda esta peça. A peça cria o usuário da IA, fecha para o usuário da IA os
arquivos das peças que ficam de olho na IA e deixa pronto o comando que abre a IA com o usuário
da IA. Dali em diante, a pessoa abre a IA por esse comando. Quando a IA tenta alterar as
anotações de uma peça que fica de olho nela, o computador recusa.

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
arquivo em que uma peça anota o que a IA fez é um item. É a mesma lista que a
conferencia-de-protecao usa para conferir o ajuste. Assim, o que esta peça fecha é o que a
conferência testa.

A configuração diz quais são as pastas de trabalho. A pasta de trabalho é a pasta em que a IA
faz o trabalho dela, como a pasta do projeto.

Todo arquivo tem um dono, que é um usuário. O dono decide os direitos do arquivo: quem lê e quem
altera. Por isso, o dono de um arquivo sempre consegue voltar a alterá-lo. A configuração diz
quem fica dono dos itens: o dono dos itens. Ele é o único usuário que altera os itens fechados.
Cada peça que fica de olho na IA tem uma parte que escreve nos arquivos dela: a parte que anota.
A parte que anota roda com o dono dos itens.

O dono dos itens pode ser o usuário da pessoa ou um usuário só para as peças. A diferença está
nos programas da pessoa. Alguns deles, como o editor de código, rodam sozinhos certos arquivos da
pasta de trabalho, por exemplo ao abrir a pasta. A IA escreve na pasta de trabalho. Então, o que
a IA escreve ali pode acabar rodando com o usuário da pessoa.

| O dono dos itens | O que acontece |
| --- | --- |
| o usuário da pessoa | o que a IA escreveu, se um programa da pessoa o rodar, consegue alterar os itens fechados |
| um usuário só para as peças | nem a pessoa altera os itens fechados, e esse caminho não chega a eles; para mexer num item, a pessoa usa o administrador |

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
programa roda. Para tratar a IA de um jeito diferente da pessoa, a IA precisa de um usuário só
dela.

**Na prática.** A peça cria o usuário da IA. Nenhuma pessoa entra no computador com ele: ele
existe para o programa da IA rodar com ele. Se o dono dos itens for um usuário só para as peças,
a peça cria esse usuário também. Um usuário que já existe a peça não cria de novo.

### Passo 2: fechar os itens

**O que é.** Fechar um item é fazer o dono dos itens virar o dono dele e deixar só o dono
alterá-lo. Quem lia o item continua lendo. O usuário da IA também lê: se antes ele não lia, a peça
lhe dá o direito de ler, e só esse. É que as peças que ficam de olho na IA rodam com o usuário da
IA e leem os próprios arquivos.

**Por quê.** É este passo que impede a IA de mexer nos arquivos das peças que ficam de olho
nela. O dono tem de ser outro usuário, e não o da IA, porque o dono sempre consegue voltar a
alterar o arquivo.

**Na prática.** Depois deste passo, quando o programa da IA tenta alterar um item, o computador
recusa. A peça só troca o dono de um item que pertence à pessoa ou ao usuário da IA. Um item de
outro dono, como um arquivo do próprio sistema, ela deixa com o dono que tem (ver "O que a peça
confere antes do ajuste").

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
Assim, o passo tem a pasta para fechar, e a parte que anota encontra a pasta pronta para criar o
arquivo nela.

Para um atalho que está dentro de uma pasta da lista, a peça não vai atrás do arquivo para onde
ele leva (ver "O que a peça confere antes do ajuste").

### Passo 3: proteger a lista

**O que é.** A lista é o arquivo que diz quais itens ficam fechados.

**Por quê.** Quem alterasse a lista poderia tirar um item dela. Esse item deixaria de ser
fechado e de ser testado pela conferência, sem que ninguém percebesse.

**Na prática.** A peça faz o administrador virar o dono da lista e deixa só ele alterá-la. Para
mudar a lista, a pessoa usa o administrador. O usuário da IA continua lendo a lista, porque as
peças que ficam de olho na IA a passam à conferencia-de-protecao.

### Passo 4: proteger esta peça

**O que é.** Esta peça é feita de arquivos: a configuração dela, a pasta com o código dela e a
pasta da central. A central é a pasta da prateleira que guarda o código que mais de uma peça
usa, e esta peça usa código de lá.

**Por quê.** Esta peça roda como administrador, que pode tudo. Se alguém alterasse um desses
arquivos, na próxima vez que a pessoa rodasse a peça, o que esse alguém escreveu também rodaria
podendo tudo.

**Na prática.** A peça faz o administrador virar o dono da configuração dela, da pasta dela e da
pasta da central, e deixa só ele alterá-las. O usuário da IA continua lendo a central, porque as
peças que ficam de olho na IA usam o código dela.

### Passo 5: abrir o caminho até os arquivos

**O que é.** Todo arquivo fica dentro de pastas, uma dentro da outra. Para chegar a um arquivo,
um usuário precisa ter o direito de entrar em cada pasta do caminho até ele. Entrar numa pasta
não é alterá-la: quem só entra não cria, não apaga e não troca nada nela.

**Por quê.** As peças que ficam de olho na IA rodam com o usuário da IA e precisam ler os
próprios arquivos, a lista e a central. A IA precisa chegar às pastas de trabalho. Com o caminho
fechado, elas não chegam, e nada funciona.

**Na prática.** A peça dá ao usuário da IA o direito de entrar nas pastas desses caminhos, e só
esse direito. Quando um caminho passa por um atalho, a peça abre também as pastas do lugar a que o
atalho leva, porque é por elas que o computador passa.

Quando uma pasta de trabalho fica dentro da pasta própria da pessoa, o usuário da IA passa a entrar
nessa pasta. Lá dentro, ele lê tudo o que o computador deixa qualquer usuário ler. Por isso, é
melhor a pasta de trabalho ficar fora da pasta própria da pessoa.

### Passo 6: abrir as pastas de trabalho

**O que é.** Abrir uma pasta para um usuário é dar a ele o direito de alterar o que está nela.

**Por quê.** A IA precisa alterar os arquivos do projeto, porque esse é o trabalho dela. O
usuário da IA é novo e, sem este passo, não altera nenhum arquivo da pessoa.

**Na prática.** A peça abre as pastas de trabalho para o usuário da IA, com tudo o que está
nelas e o que surgir nelas depois. A pessoa continua alterando tudo o que está nelas, também o
que a IA criar.

Há um limite. Um programa pode criar um arquivo já fechado, só para o dono dele. O direito da
pessoa não passa do que esse arquivo deixa. Se um programa da IA criar um arquivo assim, a pessoa
só mexe nele usando o administrador.

A peça faz este passo com o usuário da pessoa, e não como administrador. Assim, ela só mexe no que
já é da pessoa, mesmo que algo mude nas pastas enquanto ela trabalha.

### Passo 7: deixar pronto o jeito de abrir a IA

**O que é.** Para o programa da IA rodar com o usuário da IA, a pessoa precisa abri-lo por um
comando que diz isso ao computador.

**Por quê.** Se o programa da IA rodar com o usuário da pessoa, a IA tem os direitos da pessoa,
e os passos anteriores não servem para nada.

**Na prática.** A peça monta esse comando com as palavras da configuração e o mostra no fim. A
pessoa o usa com o mesmo poder de administrador com que roda esta peça. Dali em diante, a pessoa
abre a IA por esse comando.

### Passo 8: conferir o ajuste

**O que é.** A conferencia-de-protecao testa se o computador está mesmo recusando. Com o usuário
da IA, ela tenta alterar cada item, por tentativas que não mudam nada. Ela testa também a lista, a
configuração desta peça, a pasta desta peça e a pasta da central: a lista diz o que fica fechado,
e o resto roda como administrador na próxima vez que a pessoa rodar esta peça.

**Por quê.** Um ajuste pode parecer feito e não estar valendo. Só a tentativa mostra se o
computador recusa.

**Na prática.** Se o computador recusar todas as tentativas, o ajuste está valendo. Se aceitar
alguma, a peça mostra onde. No fim, a peça mostra o que fez, o comando que abre a IA e o que a
conferência encontrou.

### Depois do ajuste

Quando a lista muda, a pessoa roda a peça de novo. O usuário da IA e o dono dos itens que já
existem continuam os mesmos.

Se a pessoa abrir o programa da IA de outro jeito, a IA roda com o usuário da pessoa e tem os
direitos dela. A conferência testa com esse usuário: o que ele conseguir alterar aparece como
aberto, e as peças que ficam de olho na IA não deixam a IA agir.

Com o usuário da IA, o programa da IA começa sem a configuração que tinha com o usuário da
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

Quando o usuário da IA ainda não existe, a peça confere o que um usuário novo conseguiria fazer,
que é o que o computador deixa qualquer usuário fazer.

As pastas acima de um item contam pelo caminho escrito e, quando esse caminho passa por um atalho,
também pelo lugar a que o atalho leva, porque é por ali que o computador passa.

| Para o passo | A peça confere que | Se não estivesse certo |
| --- | --- | --- |
| todos | ela está rodando como administrador | o computador recusaria a primeira mudança |
| 1 | o usuário da IA não tem o nome da pessoa nem o do dono dos itens | a IA teria os direitos desse usuário, e nada ficaria fechado para ela |
| 1 | o usuário da IA, se já existe, não vira administrador sem senha | como administrador, a IA abriria de novo o que a peça fechasse |
| 2 | nenhum item está dentro de uma pasta de trabalho | a IA poderia trocar a pasta do item por outra (ver abaixo) |
| 2 | nenhuma pasta acima de um item está aberta para o usuário da IA | o mesmo risco, numa pasta que não é de trabalho, como uma que todos os usuários alteram |
| 2 | cada atalho de dentro das pastas da lista leva a um arquivo que também está na lista | o arquivo do outro lado ficaria aberto; a peça não vai atrás dele sozinha, porque ele pode ser um arquivo do sistema |
| 2 | cada item de outro dono, como um arquivo do sistema, já está fechado para o usuário da IA | ele ficaria aberto; a peça não troca o dono de um arquivo que não é da pessoa nem do usuário da IA |
| 2 | a pasta em que um item que ainda não existe vai aparecer guarda só itens e as pastas que levam a eles | fechar essa pasta tiraria da pessoa o direito de criar coisas nela, e o que não é item ficaria lá dentro sem ser fechado |
| 6 | nenhuma pasta de trabalho está dentro de um item | fechar o item fecharia junto a pasta de trabalho, e a IA não conseguiria trabalhar |
| 6 | tudo o que está nas pastas de trabalho é da pessoa ou do usuário da IA | o passo 6 daria à IA o direito de alterar um arquivo de outro dono, como um arquivo do sistema |

**Por que a pasta de cima importa.** Quem consegue alterar uma pasta consegue trocar o nome do que
está dentro dela e pôr outra coisa no lugar, com o nome antigo. Se a IA alterasse a pasta em que
está um item, ela trocaria o nome da pasta do item e criaria outra com o mesmo nome. A peça que
fica de olho na IA passaria a usar a pasta que a IA criou. Por isso, a prateleira e os dados das
peças ficam fora das pastas de trabalho. A peça não fecha sozinha uma pasta de cima que está
aberta: fechar uma pasta muda as regras para tudo o que está nela, e não só para o item.

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
| `usuario_da_ia` | o nome do usuário com que o programa da IA roda |
| `usuario_da_pessoa` | o nome do usuário da pessoa, que abre a IA e altera as pastas de trabalho junto com ela |
| `dono_dos_itens` | o nome do usuário dono dos itens fechados, o único que os altera; pode ser o usuário da pessoa ou um usuário só para as peças |
| `pastas_de_trabalho` | os caminhos das pastas que a IA altera |
| `comando_da_ia` | as palavras do comando que abre o programa da IA; a primeira palavra é o programa |
| `pedido_de_outro_usuario` | as palavras do comando que, neste computador, roda outro comando com outro usuário; a primeira palavra é o programa, e a palavra `{usuario}` marca o lugar do nome do usuário |
| `textos` | os textos que a peça mostra: um para cada conferência que falha, um para o que ela fez, um para o que ela faria, na prévia, e um para o que a conferência encontrou (ver [Os textos](#os-textos)) |

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
| `ia_com_nome_repetido` | o usuário da IA tem o nome da pessoa ou o do dono dos itens | `{usuario}` |
| `ia_vira_administrador` | o usuário da IA vira administrador sem senha | `{usuario}` |
| `item_em_pasta_de_trabalho` | um item está dentro de uma pasta de trabalho | `{item}`, `{pasta}` |
| `pasta_acima_aberta` | uma pasta acima de um item está aberta para o usuário da IA | `{pasta}`, `{item}` |
| `atalho_para_fora` | um atalho de dentro de uma pasta da lista leva a um arquivo que não está na lista | `{atalho}`, `{destino}` |
| `item_de_outro_dono_aberto` | um item de outro dono está aberto para o usuário da IA | `{item}`, `{dono}` |
| `onde_vai_aparecer_com_outros` | a pasta em que um item que ainda não existe vai aparecer guarda algo que não é item nem leva a um | `{pasta}`, `{caminho}` |
| `pasta_de_trabalho_em_item` | uma pasta de trabalho está dentro de um item | `{pasta}`, `{item}` |
| `pasta_de_trabalho_com_outro_dono` | algo numa pasta de trabalho é de outro dono | `{caminho}`, `{dono}` |
| `fez` | cada coisa que a peça fez | `{passo}`, `{alvo}` |
| `faria` | na prévia, cada coisa que a peça faria | `{passo}`, `{alvo}` |
| `encontrou` | cada tentativa que a conferência do passo 8 achou | `{caminho}`, `{tipo}` |

O `{passo}` é o número do passo. O `{alvo}` é o usuário criado, o caminho que mudou ou o comando
que abre a IA. O `{caminho}` e o `{tipo}` são os da tentativa, como a
[conferencia-de-protecao](../../central/conferencia-de-protecao/README.md#desprotegidos) os
entrega; na tentativa de virar administrador, que não é de nenhum arquivo, o `{caminho}` fica
vazio.

### Os sistemas

Cada tipo de sistema tem a sua parte da peça, que usa só as ferramentas que esse sistema já traz.
O que muda dentro de um mesmo tipo de sistema vem da configuração, como o jeito de rodar um
comando com outro usuário. Num sistema que a peça não atende, ou em que falta uma dessas
ferramentas, ela para sem mudar nada e diz o que falta.

| Sistema | As ferramentas que ele tem de ter |
| --- | --- |
| Linux | `useradd`, que cria usuários, e `setfacl`, que dá direitos a um usuário só |

### Os arquivos de código

| Arquivo | O que faz |
| --- | --- |
| `ajuste_de_protecao.py` | lê a configuração e a lista, faz as conferências de antes do ajuste e os oito passos, ou a prévia, e mostra os textos |
| `linux.py` | a parte do Linux: o que o ajuste faz com o que o Linux traz, como criar os usuários, fechar e abrir os caminhos e rodar a conferência com o usuário da IA |

O arquivo da parte de um sistema tem o nome que o Python dá a esse sistema. A parte de outro
sistema dá os mesmos nomes que a do Linux, cada um com o mesmo serviço.

### O que dá erro

A peça dá erro, sem mudar nada, quando a configuração ou a lista não seguem o molde. O erro diz
o arquivo e o lugar do valor errado.

Dá erro também, sem mudar nada, quando o usuário da pessoa não existe no computador, quando uma
pasta de trabalho não existe, quando o pedido de outro usuário não traz o lugar `{usuario}` em
nenhuma palavra ou traz um lugar com outro nome, e quando um texto traz um lugar que não é dele.
Se um passo não dá certo, a peça para nele, mostra o que já fez e dá o erro do passo.

### Como a peça termina

Quando acaba, o comando entrega um número, o código de saída, que diz como foi:

| Código de saída | Quando |
| --- | --- |
| 0 | o ajuste foi feito e a conferência do passo 8 não achou nada; na prévia, as conferências de antes passaram |
| 1 | uma conferência de antes do ajuste não passou, ou a do passo 8 achou alguma tentativa |
| outro | a peça não conseguiu fazer o trabalho: erro nos dados, um passo que não deu certo ou uma quebra da própria peça |

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
