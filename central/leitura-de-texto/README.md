# leitura-de-texto

A peça da central que lê um arquivo de texto.

## Para que serve

As peças leem arquivos de texto: um aviso que o projeto escreveu, um documento, um arquivo
de dados. Esta peça lê o arquivo e entrega o texto, sempre do mesmo jeito. Quando o arquivo
não existe ou não se lê, ela dá um erro que diz qual é o arquivo.

Por exemplo: uma peça recebe, no comando, o caminho do texto que ela mostra. Ela pede o
texto a esta peça; se o caminho está errado, o erro traz o caminho.

## Como funciona

- Abre o arquivo e lê tudo.
- Lê em UTF-8, o jeito de gravar texto que guarda as letras de qualquer língua.
- Entrega o texto com todas as quebras de linha iguais. Quem precisa delas como estão no
  arquivo pede assim.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### O que ela dá

#### le_texto

`le_texto` é o nome do pedido para ler um arquivo de texto.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `caminho`: o caminho do arquivo.
2. `exato`: sim (`True`) ou não (`False`). Com sim, as quebras de linha vêm como estão no
   arquivo. Serve a quem vai gravar o texto de volta, igual.

A primeira tem de vir sempre. A segunda pode faltar: sem ela, vale o não, e cada quebra de
linha, que no arquivo pode estar escrita como `\n`, `\r\n` ou `\r`, vem como `\n`.

A resposta é o texto do arquivo, lido em UTF-8.

O pedido dá erro quando o arquivo não existe ou não se lê em UTF-8. O erro é um
`ErroDeDados` (ver [erro-de-dados](../erro-de-dados/README.md)), e a mensagem diz qual é o
arquivo.

#### CODIFICACAO

`CODIFICACAO` é o nome que guarda o jeito de gravar texto em que esta peça lê, o UTF-8.
Serve à peça que grava um texto, ou que confere se ele pode ser gravado, para fazer do
mesmo jeito que esta lê.

#### QUEBRAS_COMO_ESTAO

`QUEBRAS_COMO_ESTAO` é o nome que guarda o que se diz ao Python, ao abrir um arquivo, para
ele não mexer nas quebras de linha. Serve à peça que grava de volta um texto lido com o
`exato`: com ele, cada quebra fica no arquivo como está no texto.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
