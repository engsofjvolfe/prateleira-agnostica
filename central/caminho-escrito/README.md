# caminho-escrito

A peça da central que dá, inteiro, o caminho que um arquivo de dados escreve.

## Para que serve

Um arquivo de dados, como a configuração de uma peça, pode escrever caminhos de arquivos e de
pastas. Caminho é o endereço de um arquivo no disco. O caminho que começa no início do disco já
está inteiro. O que não começa conta a partir da pasta do arquivo que o escreve. Esta peça dá o
caminho inteiro. Assim, a peça que lê o arquivo acha o mesmo lugar, seja qual for a pasta de onde
o comando rodou.

Por exemplo: a configuração de uma peça escreve só o nome de um arquivo que fica na mesma pasta
que ela. Esta peça dá o caminho inteiro desse arquivo: o da pasta da configuração, seguido do
nome.

## Como funciona

- Recebe o caminho do arquivo de dados e o caminho que ele escreve.
- Quando o caminho escrito começa no início do disco, fica com ele.
- Quando não começa, junta-o ao caminho da pasta do arquivo de dados.
- Tira do resultado os `.` e os `..`, que querem dizer "esta pasta" e "a pasta de cima".

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que ela dá

#### caminho_escrito

`caminho_escrito` é o nome do pedido para ter, inteiro, o caminho que um arquivo de dados
escreve.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `arquivo`: o caminho do arquivo de dados.
2. `escrito`: o caminho que o arquivo escreve.

A resposta é o caminho inteiro, escrito desde o início do disco.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
