# caminhos-cobertos

A peça da central que dá os caminhos que um caminho cobre.

## Para que serve

Caminho é o endereço de um arquivo ou de uma pasta no disco. Uma peça que fecha, testa ou trata
um caminho precisa tratar também tudo o que esse caminho alcança. Um caminho pode alcançar mais de
um lugar do disco: uma pasta guarda outros arquivos; um atalho leva a outro arquivo; e um arquivo
que ainda não existe vai aparecer numa pasta. Esta peça diz, numa regra só, quais caminhos um
caminho cobre. Assim, duas peças que tratam o mesmo caminho tratam os mesmos lugares.

Por exemplo: uma peça recebe o caminho de uma pasta. Esta peça dá a pasta e cada arquivo e cada
pasta de dentro dela.

## Como funciona

Atalho é um arquivo pequeno que leva a outro arquivo, guardado em outro lugar, como os atalhos da
área de trabalho.

| O caminho | O que ele cobre |
| --- | --- |
| um arquivo | o arquivo |
| uma pasta | a pasta e tudo o que está dentro dela, também nas pastas de dentro; um atalho de dentro conta, mas não se segue |
| um atalho | o atalho e o que cobre o caminho para onde ele leva |
| um caminho que ainda não existe | a pasta em que ele vai aparecer, sem o que está dentro dela |

- Quando a pasta em que o caminho vai aparecer é um atalho, ela cobre também o caminho para onde
  ele leva, também sem o que está dentro.
- Quando essa pasta também não existe, ela vem do mesmo jeito, com um tipo próprio.
- Os caminhos vêm em ordem: cada pasta antes do que está dentro dela, e o que está numa pasta em
  ordem de nome.
- Quem pede passa também os caminhos que já vieram. Um caminho que já veio não vem de novo, nem o
  que está dentro dele. Assim, o lugar que dois caminhos cobrem vem uma vez só, e o atalho que leva
  a si mesmo para.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que ela dá

#### cobertos

`cobertos` é o nome do pedido para ter os caminhos que um caminho cobre.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `caminho`: o caminho, escrito desde o início do disco.
2. `vistos`: os caminhos que já vieram. Cada caminho que vem entra nela.

A resposta é a lista dos caminhos cobertos, na ordem de [Como funciona](#como-funciona). Cada um
traz três coisas, nesta ordem: o caminho, escrito desde o início do disco; o tipo dele; e se ele
está dentro de uma pasta coberta (`de_dentro`).

| Tipo | O que é |
| --- | --- |
| `ARQUIVO` | um arquivo |
| `PASTA` | uma pasta, coberta com tudo o que está dentro dela |
| `ATALHO` | um atalho |
| `ONDE_VAI_APARECER` | a pasta em que um caminho que ainda não existe vai aparecer, coberta sem o que está dentro dela |
| `FALTA` | a pasta em que um caminho que ainda não existe vai aparecer, quando ela também não existe |

O pedido dá erro quando o caminho não começa no início do disco, quando uma pasta coberta não se
deixa ler e quando um atalho coberto não se lê, como quando ele some no meio. O erro é um
`ErroDeDados` (ver [erro-de-dados](../erro-de-dados/README.md)).

#### destino_do_atalho

`destino_do_atalho` é o nome do pedido para saber para onde um atalho leva.

Quem pede diz uma coisa só, que no código se chama `atalho`: o caminho do atalho, escrito desde
o início do disco.

A resposta é o caminho para onde o atalho leva, escrito desde o início do disco. O atalho pode
guardar esse caminho a partir da pasta em que ele está, e `..` quer dizer a pasta de cima. Quando
a pasta do atalho é alcançada por outro atalho, o computador sobe a partir do lugar real dela, e
não do caminho escrito; a resposta conta do mesmo jeito. Quando o caminho para onde o atalho leva
é outro atalho, a resposta é ele, e não o último da fila.

O pedido dá erro quando o atalho não se lê. O erro é um `ErroDeDados`.

#### lugar_real

`lugar_real` é o nome do pedido para saber o lugar do disco em que um caminho fica.

Quem pede diz uma coisa só, que no código se chama `caminho`: o caminho, escrito desde o início
do disco.

A resposta é o caminho com a pasta dele no lugar real, e o último nome como está. Quando a pasta é
alcançada por um atalho, a resposta traz o lugar a que o atalho leva. Quando o próprio caminho é
um atalho, ele não se segue: a resposta é o lugar em que o atalho fica. Assim, dois caminhos
escritos de jeitos diferentes, que levam ao mesmo lugar, dão a mesma resposta.

#### ARQUIVO, PASTA, ATALHO, ONDE_VAI_APARECER e FALTA

Os nomes dos tipos de caminho, na resposta do `cobertos`, como na tabela de [cobertos](#cobertos).

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
