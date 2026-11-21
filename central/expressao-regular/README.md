# expressao-regular

A peça da central que prepara uma expressão regular para o uso.

## Para que serve

Uma expressão regular é um jeito de descrever um texto por uma forma, como "três letras, um
traço e quatro números". As peças recebem expressões regulares nos dados do projeto, e uma
delas pode vir escrita errada. Esta peça prepara a expressão para o uso e, quando ela está
errada, dá um erro que diz onde ela está escrita.

Por exemplo: uma configuração traz, numa chave, uma expressão com um parêntese que abre e
não fecha. O erro traz o nome da chave e o que está errado na expressão.

## Como funciona

- Recebe o texto da expressão e o lugar em que ela está escrita.
- Prepara a expressão, que o Python passa a poder procurar num texto.
- Entrega a expressão pronta ou dá o erro, com o lugar.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que ela dá

#### compila

`compila` é o nome do pedido para preparar uma expressão regular.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `texto`: o texto da expressão regular, escrita do jeito do Python.
2. `onde`: o lugar em que ela está escrita, como o nome da chave. É o que aparece na
   mensagem do erro.

A resposta é a expressão pronta para o uso.

O pedido dá erro quando o texto não é uma expressão regular válida. O erro é um
`ErroDeDados` (ver [erro-de-dados](../erro-de-dados/README.md)).

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
