# modelo-de-texto

A peça da central que preenche um texto com lugares marcados.

## Para que serve

Um modelo é um texto com lugares marcados, cada um com um nome entre chaves. Em
`Olá, {nome}`, o lugar é o `{nome}`. Esta peça troca cada lugar pelo valor dele e diz quais
lugares um modelo tem. Assim, o texto fica nos dados do projeto, e a peça só põe nele o que
muda a cada vez.

Por exemplo: com o valor `Ana` para o lugar `nome`, o modelo `Olá, {nome}` vira `Olá, Ana`.

## Como funciona

- Acha no modelo cada lugar: uma chave que abre, o nome e a chave que fecha.
- Troca cada lugar pelo valor que tem o nome dele.
- O resto do texto fica como está.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que é um lugar

Tudo o que está entre uma chave que abre e a chave que fecha, sem outra chave no meio. O
nome do lugar é o que está entre as duas, como está escrito, também quando é vazio ou tem
espaços. A chave sem par fica como está.

### O que ela dá

#### campos

`campos` é o nome do pedido para saber quais lugares um modelo tem.

Quem pede diz uma coisa só, que no código se chama `modelo`: o texto do modelo.

A resposta é a lista dos nomes dos lugares, na ordem em que aparecem no modelo. O nome que
aparece duas vezes vem duas vezes.

#### preenche

`preenche` é o nome do pedido para preencher um modelo.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `modelo`: o texto do modelo.
2. `valores`: os valores, cada um com o nome do lugar dele.

A resposta é o texto com cada lugar trocado pelo valor dele. O valor posto não se lê de
novo como modelo: uma chave dentro dele fica como está.

O pedido dá erro quando o modelo tem um lugar sem valor. O erro é um `ErroDeDados` (ver
[erro-de-dados](../erro-de-dados/README.md)).

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
