# conferencia-de-molde

A peça da central que confere dados contra o molde deles.

## Para que serve

O que muda de um uso para outro chega à peça em arquivos de dados, como a configuração que o
projeto escreve. Um arquivo desses pode vir errado: um nome digitado errado, uma chave que
falta, um número onde devia haver um texto. Usado assim mesmo, o erro só apareceria no meio
do trabalho, ou passaria calado.

Por isso, cada arquivo de dados tem um molde: outro arquivo, que diz a forma que os dados
têm de ter (quais chaves existem, quais são obrigatórias e o que cada uma leva). Esta peça
confere os dados contra o molde e só os entrega quando eles estão na forma. Quando não
estão, dá um erro que diz o arquivo e o lugar de cada valor errado.

Por exemplo: o molde pede a chave `nome` com um texto, e o arquivo traz um número nela. O
erro aponta a chave `nome` e diz que ali há um número, e não um texto.

## Como funciona

- Lê o arquivo de dados e o arquivo do molde, com a
  [leitura-de-json](../leitura-de-json/README.md).
- Confere o próprio molde: ele só pode usar as regras que esta peça sabe conferir. Assim,
  toda regra do molde é conferida.
- Confere os dados contra o molde, valor por valor, e junta tudo o que está errado.
- Entrega os dados ou, quando há algo errado, dá um erro só, com tudo o que achou.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa. O
arquivo de dados é da peça que o lê, e o README dela diz onde o projeto o guarda.

## Detalhes

### O molde

O molde é um JSON Schema. As palavras que esta peça confere, e o valor que cada uma aceita,
estão no molde dos moldes, `esquemas/molde.schema.json`.

- O `pattern` é uma expressão regular do Python, procurada no texto.
- O `$ref` aponta para o próprio molde (`#`), para um molde de dentro dele
  (`#/$defs/<nome>`) ou para um molde de dentro de um molde comum
  (`<arquivo>.schema.json#/$defs/<nome>`).
- O molde comum se procura na pasta do molde que aponta para ele e, depois, na pasta
  `esquemas` desta peça.

### Os moldes comuns

O `esquemas/comum.schema.json` traz o que vários moldes usam: `linha`, um texto numa linha
só, com algo além de espaços; e `texto`, um texto com algo além de espaços.

### O que dá erro

- Os dados fora do molde. A mensagem traz o nome dos dados, o arquivo do molde e, para cada
  valor errado, o lugar dele e o motivo. O lugar se escreve como um caminho: `/a/0/b` é a
  chave `b`, do primeiro item da lista, da chave `a`.
- O molde que usa uma palavra de fora do molde dos moldes ou um tipo desconhecido.
- O molde cujo `$ref` aponta para o que não existe ou volta a ele mesmo.
- O molde que aponta para um molde comum que falta.
- O molde cujo `pattern` não é uma expressão regular válida.

Todo erro é um `ErroDeDados` (ver [erro-de-dados](../erro-de-dados/README.md)).

### O que ela dá

#### conferido

`conferido` é o nome do pedido para conferir contra um molde os dados que a peça já tem.

Quem pede diz três coisas, nesta ordem. No código, cada uma tem um nome:

1. `dados`: os dados.
2. `molde`: o caminho do arquivo do molde.
3. `nome`: o nome dos dados. É o que aparece na mensagem do erro.

A resposta são os mesmos dados, quando estão na forma do molde.

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro).

#### le_conferido

`le_conferido` é o nome do pedido para ler um arquivo de dados e conferi-lo contra o molde
dele. É o que uma peça usa para ler a sua configuração.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `caminho`: o caminho do arquivo de dados, em JSON.
2. `molde`: o caminho do arquivo do molde.

A resposta são os dados do arquivo, já conferidos.

O pedido dá erro quando o arquivo de dados não se lê como JSON (ver
[leitura-de-json](../leitura-de-json/README.md)) e nos casos de
[O que dá erro](#o-que-dá-erro). A mensagem do erro traz o caminho do arquivo de dados.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
