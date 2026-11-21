# erro-de-dados

A peça da central com o erro que diz o que está errado e onde.

## Para que serve

Quando uma peça não tem como seguir, por um arquivo que falta ou por um valor fora da forma,
ela para e avisa. Para todas as peças avisarem do mesmo jeito, o aviso é um só: o
`ErroDeDados`. A mensagem dele diz o que está errado e onde.

Por exemplo: uma configuração traz um número onde devia haver um texto. A peça que a lê dá
um `ErroDeDados`, e a mensagem traz o arquivo, a chave e o motivo.

## Como funciona

- A parte da peça que acha o problema dá o erro, com a mensagem.
- O erro sobe até o código que roda a peça.
- Esse código faz com ele o que o README da peça diz: mostra a mensagem e para, ou responde
  de outro jeito.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que ela dá

#### ErroDeDados

`ErroDeDados` é o nome do erro que uma peça dá quando algo a impede de trabalhar.

- A parte do código que acha o problema dá o erro com uma mensagem. A mensagem diz o que
  está errado e onde: o arquivo, o lugar dentro dele e o motivo.
- O código que roda a peça apanha o erro por esse nome e faz com ele o que o README da peça
  diz.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
