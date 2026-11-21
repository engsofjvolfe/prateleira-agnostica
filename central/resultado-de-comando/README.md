# resultado-de-comando

A peça da central que roda um comando e diz como ele acabou.

## Para que serve

Uma peça pode precisar rodar um programa do projeto e saber o que ele achou, como uma
conferência, que olha um arquivo e diz se ele segue uma regra. Todo comando, quando acaba,
entrega um número, o código de saída. Esta peça roda o comando e diz, por esse número, se ele
passou, se não passou ou se quebrou, junto com o que ele escreveu.

Por exemplo: uma conferência olha um arquivo e acha um erro. Ela escreve onde está o erro e
acaba com o número 1. Esta peça diz que ela não passou e entrega o que ela escreveu.

## Como funciona

- Roda o comando a partir da pasta que quem pede diz, sem mandar nada para ele ler e solto do
  terminal: assim o comando que para para perguntar algo falha na hora, em vez de ficar
  esperando uma resposta que ninguém vê.
- Espera o comando acabar e guarda o que ele escreveu.
- Lê o código de saída: 0 é passou; 1 é não passou; qualquer outro é quebrou, isto é, o
  comando parou sem conseguir dar a resposta.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa. O
projeto não guarda nenhum arquivo para ela.

## Detalhes

### O código de saída

| Código de saída | Como o comando acabou |
| --- | --- |
| 0 | passou (`PASSOU`) |
| 1 | não passou (`NAO_PASSOU`) |
| outro | quebrou (`QUEBROU`) |

O que o comando escreveu se lê em UTF-8, como na
[leitura-de-texto](../leitura-de-texto/README.md); o que não se lê assim vira um sinal de
troca.

### O que ela dá

#### resultado

`resultado` é o nome do pedido para rodar um comando e saber como ele acabou.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `comando`: as palavras do comando; a primeira é o programa.
2. `pasta`: a pasta de onde o comando roda.

A resposta traz quatro coisas, nesta ordem: como o comando acabou (`PASSOU`, `NAO_PASSOU`
ou `QUEBROU`); o código de saída; o que ele escreveu na saída padrão; e o que ele escreveu na
saída de erro.

O pedido dá erro quando o comando não tem nenhuma palavra e quando ele não roda, como quando
o programa não existe. O erro é um `ErroDeDados` (ver
[erro-de-dados](../erro-de-dados/README.md)).

#### PASSOU, NAO_PASSOU e QUEBROU

Os nomes de como um comando acaba, na resposta do `resultado`, como na tabela de
[O código de saída](#o-código-de-saída).

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
