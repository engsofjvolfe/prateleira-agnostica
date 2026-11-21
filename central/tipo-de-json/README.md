# tipo-de-json

A peça da central que diz se um valor é de um tipo do JSON.

## Para que serve

O que muda de um uso para outro chega às peças em arquivos de dados, e o JSON é o jeito de
escrever esses dados. No JSON, cada valor é de um tipo: um texto, um número, um número
inteiro, uma lista, um objeto, o sim ou o não, ou o nada. Antes de usar um valor, a peça
precisa saber se ele é do tipo que ela espera; senão, o erro só aparece no meio do trabalho,
ou passa calado.

Esta peça responde a essa pergunta, sempre do mesmo jeito, e evita uma armadilha: para o
Python, a língua em que a prateleira é escrita, o sim e o não contam como números. Sem esta
peça, o sim passaria por número inteiro.

Por exemplo: uma peça recebe, de um arquivo de dados, a linha em que uma leitura começa, e
pergunta se o valor é um número inteiro. Com um número, a resposta é sim; com o sim no lugar
do número, a resposta é não.

## Como funciona

- Recebe o valor e o nome do tipo.
- Olha, na sua lista, o que esse nome é na língua em que a prateleira é escrita.
- Responde sim ou não. O nome que não está na lista dá erro, porque quem perguntou se
  enganou.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa. Ela não
lê nenhum arquivo: trabalha só com o valor que recebe.

## Detalhes

### O que ela dá

#### TIPOS

`TIPOS` é o nome que guarda a lista dos tipos do JSON que esta peça conhece, cada um com o
nome que o JSON lhe dá: `object`, `array`, `string`, `integer`, `number`, `boolean` e
`null`. São esses os nomes que o pedido abaixo aceita, e são os mesmos que um molde usa (ver
[conferencia-de-molde](../conferencia-de-molde/README.md)).

Um número inteiro é dos dois tipos de número, o `integer` e o `number`. O sim e o não são só
do `boolean`.

#### do_tipo

`do_tipo` é o nome do pedido para saber se um valor é de um tipo.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `valor`: o valor.
2. `tipo`: o nome do tipo, um dos de `TIPOS`.

A resposta é sim (`True`) ou não (`False`).

O pedido dá erro quando o nome não é de nenhum tipo da lista. O erro é um `ErroDeDados` (ver
[erro-de-dados](../erro-de-dados/README.md)).

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
