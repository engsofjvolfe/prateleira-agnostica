# copias-estragadas

A peça da central que prova que o teste de uma peça pega os defeitos dela.

## Para que serve

O teste de uma peça é o programa que a usa e confere se ela faz o que deve: passa quando
está tudo certo e falha quando acha um erro. Mas o próprio teste pode estar errado: um
teste que passa sempre, com a peça certa ou com a peça quebrada, não avisa de nada.

Esta peça confere o teste, e não a peça testada. Para isso, quebra a peça testada de
propósito, numa cópia, de cada jeito que uma lista diz, e vê se o teste falha.

Por exemplo: uma peça tem a regra "tira os espaços do começo do texto". Numa cópia dela, o
trecho do arquivo onde essa regra está escrita é trocado por outro, e a cópia deixa de
tirar os espaços. O teste roda contra essa cópia e tem de falhar: se ele passa, é porque
não confere essa regra.

## Como funciona

Cada regra da peça testada está escrita num arquivo dela. Para a peça deixar de cumprir uma
regra, basta trocar o trecho onde ela está escrita por outro, errado. Cada troca dessas é
um estrago, e a lista dos estragos de uma peça fica na pasta de testes dela.

Primeiro, esta peça faz uma cópia da peça testada, sem estrago nenhum, e roda o teste contra
essa cópia. O teste tem de passar. Se ele já falha aí, vai falhar também em todo estrago,
por um motivo que não é o estrago, e a prova não vale nada. Nesse caso, esta peça para e
avisa.

Depois, para cada estrago da lista, ela:

- faz uma cópia nova da peça testada;
- faz a troca nessa cópia;
- roda o teste contra a cópia.

Cada rodada do teste acaba de um de quatro jeitos:

- o teste falha, porque achou o erro: o estrago foi pego;
- o teste passa: o estrago escapou, e o teste não confere aquela regra;
- o teste quebra, isto é, para no meio sem conseguir conferir, como quando a troca impede a
  cópia de rodar: o estrago não conta como pego, porque o teste não mostrou que confere a
  regra;
- o teste não acaba dentro do tempo que foi dado: esta peça o corta, e o estrago também não
  conta como pego.

No fim, esta peça entrega o que aconteceu com cada estrago. O teste está provado quando
todos foram pegos.

A peça testada nunca muda: toda troca é feita numa cópia.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa. O
projeto não guarda nenhum arquivo para ela.

## Detalhes

### A lista de estragos

O molde está em `esquemas/copias-estragadas.schema.json`.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `estragos` | os estragos, pelo menos um. De cada um: o `nome`, em letras minúsculas e números, com as palavras separadas por hífen; o `arquivo`, com o caminho dele dentro da peça testada, escrito com `/` entre as pastas; o `de`, o trecho como está no arquivo; e o `para`, o trecho que entra no lugar |

O `arquivo` é qualquer arquivo de texto da peça testada. O trecho `para` pode ser vazio:
aí, o estrago só tira o trecho `de`.

O trecho `de` aparece no arquivo uma vez só: assim, a troca é sempre a mesma. Quando o
arquivo muda e o trecho deixa de existir, a lista dá erro, em vez de rodar um estrago que
não estraga nada.

### A cópia

A cópia leva tudo o que a pasta da peça testada tem, e tem o mesmo nome dela. O atalho, que
é um arquivo ou uma pasta que só aponta para outro lugar, vai como atalho. Nenhum estrago
mexe num atalho nem no que está dentro de uma pasta que é atalho: assim, nenhuma troca sai
da cópia.

### A pasta de trabalho

Cada rodada do teste tem a sua pasta dentro da pasta de trabalho: a `sem-estrago`, para a
cópia sem estrago, e a `estragos/<nome do estrago>`, para a de cada estrago. Tudo fica lá
depois da prova, para quem quiser ver o que aconteceu.

| Na pasta de uma rodada | O que é |
| --- | --- |
| `copia/<nome da peça testada>` | a cópia |
| `gravacao` | a pasta vazia que o teste recebe |
| `saida.txt` | o que o teste escreveu na saída padrão, que é onde um comando escreve o resultado dele |
| `erro.txt` | o que o teste escreveu na saída de erro, que é onde um comando escreve os avisos e os erros |

### Como o teste roda

O teste roda por um comando, que vem de quem pede a prova. Depois das palavras do comando, o
teste recebe a pasta da cópia e uma pasta nova, vazia, para o que ele precisar gravar, nessa
ordem. Ele não recebe nada pela entrada padrão, que é por onde um comando lê o que lhe
mandam enquanto roda.

O comando diz como o teste acabou pelo código de saída, que é o número que todo comando
entrega quando acaba:

| Código de saída | Como o teste acabou |
| --- | --- |
| 0 | passou |
| 1 | falhou: achou um erro |
| outro | quebrou: não conseguiu conferir |

Cada rodada tem um limite de tempo, em segundos, que vem de quem pede a prova. O teste que
passa do limite é cortado, com tudo o que ele pôs para rodar.

### Só alguns estragos

Quem pede a prova pode pedir só alguns estragos da lista, em vez de todos. Para isso, diz
uma ou mais escolhas. Cada escolha tem duas partes: um campo do estrago, que é o `nome`, o
`arquivo`, o `de` ou o `para`, e um valor. Ela escolhe os estragos que têm esse valor nesse
campo: com o campo `arquivo`, os estragos de um arquivo; com o campo `nome`, um estrago só.

Com mais de uma escolha, rodam os estragos que batem com qualquer uma. Os escolhidos rodam
na ordem da lista.

Serve para conferir depressa uma mudança no teste. A prova que vale é a de todos os
estragos.

### O que dá erro

- A peça testada que não é uma pasta.
- A lista fora do molde (ver [conferencia-de-molde](../conferencia-de-molde/README.md)).
- Dois estragos com o mesmo nome.
- O estrago cujo `arquivo` não é um arquivo de dentro da peça testada, é um atalho ou fica
  dentro de uma pasta que é atalho.
- O estrago cujo `arquivo` não se lê como texto (ver
  [leitura-de-texto](../leitura-de-texto/README.md)).
- O estrago cujo trecho `de` não aparece no arquivo ou aparece mais de uma vez.
- O estrago cujo trecho `para` é igual ao `de`.
- A escolha de um campo que os estragos não têm, ou que não bate com nenhum estrago.
- O limite de tempo que não é um número maior que zero.
- O comando do teste sem nenhuma palavra.
- A pasta de trabalho que não está vazia ou que fica dentro da peça testada.
- O comando do teste que não roda.
- O teste que não passa na cópia sem estrago.

Os dois últimos só aparecem na rodada da cópia sem estrago, antes do primeiro estrago. Todos
os outros se conferem antes de a primeira cópia ser feita. Todo erro é um `ErroDeDados` (ver
[erro-de-dados](../erro-de-dados/README.md)).

### O que ela dá

#### prova

`prova` é o nome do pedido para fazer a prova, do jeito de [Como funciona](#como-funciona).

Quem pede diz seis coisas, nesta ordem. No código, cada uma tem um nome:

1. `peca`: a pasta da peça testada.
2. `comando`: as palavras do comando do teste.
3. `estragos`: o caminho do arquivo da lista de estragos.
4. `trabalho`: a pasta de trabalho.
5. `limite`: o limite de tempo de cada rodada, em segundos.
6. `so`: quais estragos rodam, quando é para rodar só alguns (ver
   [Só alguns estragos](#só-alguns-estragos)).

As cinco primeiras têm de vir sempre. A sexta pode faltar: sem ela, rodam todos os estragos.

A resposta traz um item para cada estrago que rodou, na ordem em que eles estão na lista de
estragos. Cada item diz três coisas, nesta ordem:

1. O nome do estrago.
2. O resultado, que é uma das palavras da tabela abaixo.
3. A última linha que o teste escreveu, que ajuda a ver o motivo. É a da saída de erro ou,
   quando o teste não escreveu nada nela, a da saída padrão.

| Resultado | Como o teste acabou |
| --- | --- |
| `pego` | falhou |
| `escapou` | passou |
| `quebrou` | quebrou |
| `cortado` | passou do limite de tempo |

Quando acontece um dos casos de [O que dá erro](#o-que-dá-erro), não há resposta: o pedido
dá erro.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
