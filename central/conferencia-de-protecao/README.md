# conferencia-de-protecao

Confere se o computador está mesmo impedindo a IA de alterar os arquivos das peças que ficam de
olho nela.

## Para que serve

Algumas peças da prateleira ficam de olho na IA. O programa em que a pessoa trabalha com a IA
chama essas peças antes de cada ação da IA, e elas respondem se a ação pode seguir.

Cada uma dessas peças tem arquivos próprios. Num deles ela anota o que a IA fez. Noutro estão as
regras que ela cobra. Noutro, a configuração dela.

A IA altera arquivos, porque é esse o trabalho dela. E ela alcança também esses arquivos. Se ela
alterar o arquivo das anotações, apaga o que fez. Se alterar o das regras, muda o que é cobrado.
Se alterar o da configuração, a peça deixa de ser chamada. Em nenhum desses casos alguém é
avisado: a peça continua respondendo, e a resposta já não vale.

Pedir à IA que não toque nesses arquivos não resolve, porque o pedido depende de ser obedecido
por ela mesma. Quem resolve é o computador.

No computador, todo programa roda com um usuário. É o mesmo tipo de usuário com que uma pessoa
entra na máquina. Cada arquivo, por sua vez, guarda quais usuários podem lê-lo e quais podem
alterá-lo. Toda vez que um programa tenta alterar um arquivo, o computador olha essas duas
coisas e recusa o que não está permitido.

Então uma pessoa faz um ajuste no computador, uma vez: cria um usuário só para a IA e deixa os
arquivos dessas peças fechados para esse usuário. Fechado quer dizer que esse usuário lê o
arquivo, mas não altera.

O ajuste pode ficar incompleto. Pode ser desfeito depois. Pode nunca ter sido feito. Nada avisa.
É para isso que esta peça serve: ela confere se o ajuste está valendo e informa o que encontrou.
Enquanto não estiver valendo, a peça que chamou esta não deixa a IA agir.

Exemplo: uma peça guarda as anotações dela dentro de uma pasta própria, e essa pasta ficou
aberta para o usuário da IA. Esta peça encontra a abertura. A peça que a chamou não deixa a IA
agir e informa qual pasta está aberta. Fechada a pasta, o trabalho segue.

## Como funciona

Esta peça recebe uma lista. Nela estão os arquivos e as pastas que a IA não pode alterar.

A peça pega um item da lista por vez e faz testes nele. Cada teste é uma tentativa de alterar
esse item, feita com o usuário da IA. Se o computador recusa a tentativa, aquele item está
protegido. Se aceita, não está.

Nenhuma tentativa altera nada. São quatro:

| A tentativa | O que a peça faz | O que a resposta do computador mostra |
| --- | --- | --- |
| escrever | abre o arquivo para escrever e não escreve nada | se a IA conseguiria escrever nesse arquivo |
| apagar | cria um arquivo na pasta em que o arquivo está e o apaga logo depois | se a IA conseguiria apagar o arquivo ou trocá-lo por outro, o que depende da pasta, e não do arquivo |
| mudar os direitos | pede, para o arquivo, os mesmos direitos que ele já tem | se a IA conseguiria se dar permissão de escrever nele |
| virar administrador | pede para rodar como administrador sem digitar senha | se a IA conseguiria virar o usuário que altera qualquer arquivo |

A tentativa de apagar é feita também em cada pasta acima, até a primeira do disco. Quem pode
mexer numa pasta pode trocar o nome dela e tirá-la do lugar, levando tudo o que está dentro.

A tentativa de virar administrador é feita uma vez só, e não em cada item. Ela não é sobre um
arquivo: é sobre o usuário da IA.

Cada sistema tem o seu jeito de pedir poderes de administrador. O nome do programa que faz esse
pedido muda de um sistema para outro. As palavras que impedem esse programa de parar para
perguntar a senha também mudam.

Por isso a peça não traz esse pedido escrito dentro dela. Quem o escreve é a pessoa que fez o
ajuste, na mesma lista dos caminhos fechados: são as palavras do pedido no computador dela.

Se o pedido estivesse escrito dentro da peça, ela serviria a um tipo de sistema só. E há um risco
pior. Em alguns sistemas, o programa com o nome esperado é outro programa: um que só encaminha o
pedido para um terceiro, ou um que termina dizendo que deu tudo certo em qualquer caso. A peça
estaria respondendo sobre esse outro programa, e não sobre o pedido que ela quer testar.

Desse pedido, a peça olha só como o comando terminou, e não o que ele escreveu. O texto que um
programa escreve muda de programa para programa e de idioma para idioma. O comando que terminou
bem mostra que o computador aceitou o pedido. O que terminou recusando mostra que o pedido está
fechado. Qualquer outro fim entra na lista como tentativa que não chegou a ser feita.

As tentativas valem para tudo o que roda com o usuário da IA: um comando no terminal, um
programa que a própria IA escreveu e mandou rodar, ou outro jeito qualquer. O computador olha o
usuário e os direitos em toda alteração, venha de onde vier. As ferramentas do próprio programa,
como a de editar um arquivo, rodam com outro usuário; para elas, quem barra são as peças (ver "O
que precisa estar feito no computador").

Três tipos de item pedem mais do que os quatro testes.

**Item que é uma pasta.** Quando a lista traz uma pasta, o que precisa estar protegido é tudo o
que está dentro dela. Cada arquivo tem os seus próprios direitos, e um deles pode estar aberto
sem que os outros estejam. A peça faz os quatro testes em cada arquivo de dentro da pasta, e
também nas pastas de dentro, uma por uma.

**Item que é um arquivo que ainda não existe.** Um programa cria os arquivos dele na hora em que
precisa deles. A peça que anota o que a IA fez, por exemplo, cria o arquivo das anotações quando
tem a primeira coisa para anotar; antes disso, esse arquivo não existe. Mesmo assim o nome dele
já está na lista, porque a pessoa faz o ajuste do computador antes de a peça rodar a primeira
vez.

Num arquivo que não existe não há o que testar: não há o que abrir, e não há direitos guardados.
Então a peça faz os testes na pasta em que esse arquivo vai aparecer.

O risco é este. Se a IA pode criar arquivos nessa pasta, ela cria ali um arquivo com o nome que
a peça vai usar; esse nome não é segredo, está na configuração da peça, que a IA lê. Depois,
quando a peça for anotar, ela encontra o arquivo já criado e trabalha com ele como se fosse o
dela.

**Item que é um atalho.** Atalho é um arquivo que não guarda conteúdo: ele guarda o endereço de
outro arquivo, que pode estar em qualquer lugar do disco. Quem abre o atalho abre esse outro
arquivo. Então proteger o atalho não protege o conteúdo: a IA alteraria o outro arquivo, e a
peça leria o que a IA escreveu. A peça faz os testes nos dois: no atalho e no arquivo que ele
aponta.

No fim, a peça entrega a lista das tentativas que o computador aceitou.

Lista vazia quer dizer que o computador recusou todas: o ajuste está valendo, e a peça que
chamou esta trabalha como sempre.

Lista com alguma tentativa quer dizer que o ajuste não está valendo. A peça que chamou esta não
deixa a IA agir e informa o que está na lista. A tentativa de virar administrador vale por todas
as outras: como administrador, a IA altera qualquer arquivo.

Uma tentativa pode não chegar a ser feita, por um motivo que não tem a ver com direitos, como o
disco estar cheio. Nesse caso o computador não recusou nada, e não há prova de que o item está
protegido. Essa tentativa entra na lista do mesmo jeito.

## O que precisa estar feito no computador

Esta peça só confere. Quem deixa o computador pronto é uma pessoa, e são cinco coisas, feitas
uma vez. Só pode fazê-las quem manda no computador, porque criar usuário não é coisa que
qualquer um faça.

1. **Criar um usuário para a IA.** Passa a existir no computador um usuário que é só da IA,
   separado do usuário da pessoa.
2. **Fazer as ações da IA rodarem com o usuário da IA, e só elas.** Ação da IA é o que ela manda
   o computador rodar, como um comando no terminal ou um programa que ela escreveu. Tudo isso sai
   com o usuário da IA, e é a ele que o computador recusa. O programa da IA e as peças que ficam
   de olho nela rodam fora, com outro usuário. Na prática:
   - a IA não consegue parar essas peças, porque um usuário só consegue parar os programas dele;
   - se a IA rodar uma cópia de uma peça com uma informação falsa, a cópia roda com o usuário da
     IA e não escreve nos arquivos da peça;
   - as ferramentas do próprio programa, como a de editar um arquivo, rodam fora, com o
     usuário que roda o programa. Nos arquivos em que as peças escrevem, o computador não as
     barra, porque as peças rodam com o mesmo usuário e precisam escrever ali. Por isso, cada
     peça barra essas ferramentas nos arquivos em que ela escreve, e o programa a chama antes
     de cada uso delas.

   Para pôr as ações da IA com o usuário da IA, o usuário que roda o programa precisa poder rodar
   um comando com o usuário da IA sem digitar senha.
3. **Fechar, para o usuário da IA, os arquivos das peças que ficam de olho nela.** Fechar quer
   dizer que o usuário da IA lê o arquivo e não altera. As pastas em que esses arquivos estão
   também ficam fechadas, porque quem mexe na pasta apaga ou troca o arquivo que está dentro.
   Quais arquivos são esses está logo abaixo.
4. **Não deixar o usuário da IA rodar como administrador sem senha.** Como administrador, a IA
   altera qualquer arquivo, e os outros ajustes deixam de valer.
5. **Fazer o programa da IA barrar a ação quando uma peça não responde.** Uma peça pode quebrar
   ou demorar demais. Se o programa seguisse em frente sem a resposta, a ação passaria sem ser
   conferida. Por isso, sem resposta, a ação fica barrada.

A pessoa escreve, na lista, cada arquivo e cada pasta que ela fechou. Na mesma lista, ela escreve
o nome do usuário da IA, o nome do usuário que roda o programa e, nas palavras do computador
dela, o pedido de administrador e o pedido para rodar um comando com outro usuário. É essa lista
que esta peça recebe para testar.

Entram na lista os arquivos em que cada peça anota, o programa de cada peça, a configuração de
cada peça, os arquivos do programa da IA e os arquivos que ainda não existem. O que ficar fora da
lista não é testado, e, se também não tiver sido fechado, é por ali que a IA desliga a peça, em
vez de alterar as anotações dela.

Entra também o lugar de onde o programa da IA lê a configuração dos itens 2 e 5: a que manda
chamar as peças, a que põe as ações da IA no usuário da IA e a que barra a ação quando uma peça
não responde. As ferramentas do programa rodam com o usuário que roda o programa e alteram a pasta
própria dele. Por isso, essa configuração fica num lugar que só o administrador altera, e a
configuração do usuário que roda o programa não consegue desfazê-la nem acrescentar a ela outro
programa para rodar. Um programa acrescentado ali rodaria com o usuário que roda o programa:
alteraria os arquivos em que as peças anotam e pararia as peças.

Falta dizer quem pede esta conferência. Quem pede é cada peça que fica de olho na IA, antes de
deixar a IA agir. Cada uma pede por si, porque o projeto pode ligar uma peça e não outra. As
peças que ficam de olho na IA rodam fora, com o usuário que roda o programa. Por isso, esta peça
faz as tentativas com o usuário da IA: o que o computador recusa ao usuário da IA é o que ele
recusaria à IA. Se as tentativas fossem feitas com o usuário que roda as peças, o computador
aceitaria as que caem nos arquivos em que elas anotam, e a lista não diria nada sobre a IA.

Para fazer as tentativas com o usuário da IA, esta peça usa o pedido para rodar um comando com
outro usuário, escrito na lista. É o mesmo poder do item 2: o usuário que roda as peças roda um
comando com o usuário da IA sem digitar senha.

Antes das tentativas, esta peça confere se está rodando com o usuário que roda o programa, cujo
nome está na lista. Se o programa da IA foi aberto de outro jeito, como com o usuário da pessoa,
as peças não rodam fora como o item 2 pede. Aí esta peça não faz as tentativas, e a resposta diz
que ela rodou com outro usuário.

Em computador em que a pessoa não manda, não há como criar o usuário da IA. Aí o ajuste não se
faz, e a conferência não passa.

## Como ligar num projeto

Esta peça não é chamada pelo programa da IA e não roda sozinha: ela é usada por dentro de uma
peça que fica de olho na IA. Ela chega ao projeto junto com essa peça, pelo caminho da central
que o comando dessa peça informa (ver [roda](../roda/README.md)).

O projeto guarda, nas pastas de dados dele, a lista dos arquivos e das pastas que ficam fechados
para a IA. O comando da peça que usa esta recebe o caminho dessa lista, e essa peça entrega o
caminho a esta. Uma lista só serve a todas as peças que ficam de olho na IA naquele projeto.

## Detalhes

### A lista

Um arquivo em JSON, que é um jeito de escrever dados. A forma que esse arquivo tem de ter está
no molde `esquemas/conferencia-de-protecao.schema.json`.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `fechados` | os caminhos, de arquivos ou de pastas, que ficam fechados para a IA |
| `pedido_de_administrador` | as palavras do comando que, neste computador, pede para rodar como administrador sem digitar senha; a primeira palavra é o programa |
| `usuario_da_ia` | o nome do usuário com que as ações da IA rodam |
| `usuario_do_programa` | o nome do usuário que roda o programa da IA e as peças que ficam de olho nela |
| `pedido_de_outro_usuario` | as palavras do comando que, neste computador, roda outro comando com outro usuário sem digitar senha; a primeira palavra é o programa, e a palavra `{usuario}` marca o lugar do nome do usuário |

Caminho é o endereço de um arquivo no disco. Cada caminho aparece uma vez, não é vazio e não tem
quebra de linha. O caminho que não começa no início do disco conta a partir da pasta em que a
lista está.

O pedido de administrador tem pelo menos uma palavra. Cada palavra não é vazia e não tem quebra
de linha. Os nomes do usuário da IA e do usuário do programa também não são vazios e não têm
quebra de linha, e são diferentes um do outro. O pedido de outro usuário segue a forma do pedido
de administrador e traz `{usuario}` em alguma palavra, sem outro lugar marcado entre chaves.

### Os arquivos de código

| Arquivo | O que faz |
| --- | --- |
| `conferencia_de_protecao.py` | lê a lista, confere os nomes e os pedidos, confere com que usuário a peça roda e roda as tentativas com o usuário da IA; dá o `le_fechados`, o `desprotegidos`, o `pedido_para` e o `achados_da_lista` |
| `tentativas.py` | faz as tentativas com o usuário com que roda e escreve o que achou; quem o roda é o `desprotegidos`, com o usuário da IA, pelo pedido de outro usuário |

### O que ela dá

#### le_fechados

Recebe o caminho da lista. Lê o arquivo e confere se ele segue o molde.

Entrega cinco coisas: os caminhos que estão na lista, na ordem em que aparecem, cada um escrito
desde o início do disco; as palavras do pedido de administrador, na ordem em que estão; o nome
do usuário da IA; o nome do usuário do programa; e as palavras do pedido de outro usuário, na
ordem em que estão.

Dá o [erro de dados](../erro-de-dados/README.md#errodedados) quando o arquivo não se lê, não
segue o molde, repete um caminho, traz os dois nomes de usuário iguais ou traz um pedido de outro
usuário sem `{usuario}` ou com outro lugar marcado.

#### desprotegidos

Recebe cinco coisas: os caminhos que ficam fechados para a IA, cada um escrito desde o início do
disco; as palavras do pedido de administrador; o nome do usuário da IA; o nome do usuário do
programa; e as palavras do pedido de outro usuário.

Primeiro, confere se está rodando com o usuário do programa. Se não está, entrega só uma linha,
do tipo `outro_usuario`, sem caminho, e não faz nenhuma tentativa.

Depois, faz as tentativas com o usuário da IA, pelo pedido de outro usuário. Quando o pedido de
outro usuário não consegue rodar as tentativas, cada caminho recebido entra na resposta como
`indeterminado`, e a tentativa de virar administrador também.

Entrega as tentativas que o computador aceitou, na ordem dos caminhos recebidos. Cada uma traz o
caminho e o tipo. O caminho é o lugar em que o computador aceitou a tentativa, que pode ser o
próprio caminho recebido, um arquivo ou uma pasta de dentro dele, ou uma pasta acima dele. A
tentativa de virar administrador vem por último, sem caminho, porque não é de nenhum arquivo.
Lista vazia quer dizer que o computador recusou todas.

| Tipo | A tentativa que o computador aceitou |
| --- | --- |
| `escrita` | abrir o arquivo para escrever |
| `pasta` | criar e apagar um arquivo na pasta em que o caminho está, numa pasta acima ou, quando o caminho é uma pasta, dentro dela |
| `direitos` | mudar os direitos do arquivo para os mesmos que ele já tinha |
| `administrador` | rodar como administrador sem senha |
| `indeterminado` | nenhuma: a tentativa não chegou a ser feita, por um motivo que não tem a ver com direitos |
| `outro_usuario` | nenhuma: esta peça rodou com um usuário que não é o do programa e não fez as tentativas |

Dá o erro de dados quando não recebe nenhum caminho, quando um caminho não começa no início do
disco, quando o pedido de administrador não tem nenhuma palavra, quando um dos dois nomes de
usuário é vazio, quando os dois são iguais e quando o pedido de outro usuário não traz
`{usuario}` ou traz outro lugar marcado.

#### pedido_para

Recebe duas coisas: as palavras do pedido de outro usuário e o nome de um usuário.

Entrega as palavras do pedido, na mesma ordem, com o nome no lugar de `{usuario}`. É o pedido
para rodar um comando com esse usuário.

#### achados_da_lista

Recebe o caminho da lista. Lê a lista, com o `le_fechados`, e faz o `desprotegidos` com o que
ela traz.

Entrega cada achado como uma linha de texto, `<caminho>: <tipo>`, na ordem do
`desprotegidos`; na linha que não é de nenhum arquivo, o caminho fica vazio. Lista vazia quer
dizer que o computador recusou todas as tentativas.

Dá os erros do `le_fechados` e do `desprotegidos`.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
