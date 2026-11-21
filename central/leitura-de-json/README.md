# leitura-de-json

A peça da central que lê dados em JSON.

## Para que serve

Os dados da prateleira são escritos em JSON, um jeito de escrever dados em texto, com nomes
e valores. Esta peça lê um texto ou um arquivo em JSON e entrega os dados. Ela dá erro
também no que dois leitores poderiam ler de jeitos diferentes: assim, os dados são sempre os
mesmos, seja quem for que os leia.

Por exemplo: um arquivo traz o nome `pasta` duas vezes, cada vez com um valor. Um leitor
ficaria com o primeiro valor, e outro com o último. Esta peça dá erro, e diz o arquivo e o
nome.

## Como funciona

- Lê o arquivo como texto, com a [leitura-de-texto](../leitura-de-texto/README.md).
- Lê o texto como dados.
- Confere o que dois leitores poderiam ler de jeitos diferentes.
- Entrega os dados ou dá um erro, que diz de onde o texto veio e o que está errado.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que dá erro

- O texto que não é JSON.
- O `NaN` e o `Infinity`, que alguns leitores aceitam como números.
- O texto com só metade de um caractere (um substituto UTF-16 solto), que não se grava em
  UTF-8.
- O objeto com o mesmo nome mais de uma vez.
- O texto com valores demais, um dentro do outro, para o Python ler.

Todo erro é um `ErroDeDados` (ver [erro-de-dados](../erro-de-dados/README.md)).

### O que ela dá

#### de_json

`de_json` é o nome do pedido para ler um texto em JSON.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `texto`: o texto em JSON.
2. `origem`: de onde o texto veio, como o caminho do arquivo que o traz. É o que aparece na
   mensagem do erro.

A resposta são os dados do texto.

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro).

#### le_json

`le_json` é o nome do pedido para ler um arquivo em JSON.

Quem pede diz uma coisa só, que no código se chama `caminho`: o caminho do arquivo.

A resposta são os dados do arquivo.

O pedido dá erro quando o arquivo não existe ou não se lê como texto em UTF-8, e nos casos
de [O que dá erro](#o-que-dá-erro). A mensagem do erro traz o caminho do arquivo.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
