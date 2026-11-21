# texto-de-comando

A peça da central que roda um comando e entrega, como texto, o que ele escreveu.

## Para que serve

Uma peça pode precisar do que um comando escreve, como o conteúdo de um arquivo guardado no
git. Esse conteúdo tem de chegar do mesmo jeito que a leitura de um arquivo de texto o
entrega, e dar erro quando não se lê. Esta peça roda o comando e entrega o que ele escreveu
desse jeito.

Por exemplo: uma peça pede ao git a cópia de um arquivo que vai no próximo commit. Se a cópia
tem letras que não se leem, esta peça dá um erro, em vez de trocar essas letras por um sinal.

## Como funciona

- Roda o comando a partir da pasta que quem pede diz, sem mandar nada para ele ler e solto do
  terminal: assim o comando que para para perguntar algo falha na hora, em vez de ficar
  esperando uma resposta que ninguém vê.
- Espera o comando acabar.
- Quando ele acaba com o código de saída 0, entrega o que ele escreveu, lido como na
  [leitura-de-texto](../leitura-de-texto/README.md).
- Quando ele acaba com outro código, a resposta diz que ele não passou.
- Quando ele não roda, ou o que escreveu não se lê, dá erro.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa. O
projeto não guarda nenhum arquivo para ela.

## Detalhes

### O que ela dá

#### texto_do_comando

`texto_do_comando` é o nome do pedido para rodar um comando e receber, como texto, o que ele
escreveu na saída padrão.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `comando`: as palavras do comando; a primeira é o programa.
2. `pasta`: a pasta de onde o comando roda.

A resposta é o que o comando escreveu na saída padrão, lido em UTF-8, com cada quebra de
linha como `\n`, quando ele acaba com o código de saída 0. Quando ele acaba com outro código,
a resposta é `None`, o nome que o Python dá a "nenhum".

O pedido dá erro quando o comando não tem nenhuma palavra, quando ele não roda, como quando o
programa não existe, e quando o que ele escreveu na saída padrão não se lê em UTF-8. O erro é
um `ErroDeDados` (ver [erro-de-dados](../erro-de-dados/README.md)), e a mensagem diz o
comando.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
