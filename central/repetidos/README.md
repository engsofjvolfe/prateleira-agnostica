# repetidos

A peça da central que acha os valores repetidos de uma lista.

## Para que serve

Há listas em que cada valor só pode aparecer uma vez, como os nomes das ferramentas numa
configuração. Esta peça diz quais valores de uma lista aparecem mais de uma vez, para a peça
que a usa avisar do erro com os nomes certos.

Por exemplo: numa lista com `a`, `b`, `a` e `c`, o repetido é o `a`.

## Como funciona

- Conta quantas vezes cada valor aparece na lista.
- Entrega os que aparecem mais de uma vez, cada um uma vez só, em ordem.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que ela dá

#### repetidos

`repetidos` é o nome do pedido para achar os valores repetidos de uma lista. Serve para
conferir o que o molde de um arquivo de dados não confere, como dois nomes iguais em
lugares diferentes dos dados.

Quem pede diz uma coisa só, que no código se chama `valores`: a lista.

A resposta é a lista dos valores que aparecem mais de uma vez, cada um uma vez só, em
ordem. Quando nada se repete, a resposta é uma lista vazia.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
