# repositorio-git

A peça da central que diz se uma pasta fica num repositório git.

## Para que serve

Um repositório git é uma pasta cujo histórico o programa git guarda. Uma peça pode trabalhar de um
jeito quando a pasta do projeto fica num repositório e de outro quando não fica, como listar só os
arquivos que o git guarda. Esta peça diz se a pasta fica num repositório sem rodar o git. Assim, a
peça que a usa sabe se vai precisar do git antes de chamá-lo.

Por exemplo: a pasta de um projeto fica dentro de outra, que tem o `.git`. Esta peça diz que sim.

## Como funciona

- Acha o lugar real da pasta no disco, seguindo os atalhos, como o git faz.
- Olha essa pasta e cada pasta acima dela, até o começo do disco.
- Diz que sim quando uma delas tem um `.git`, que é onde o git guarda o histórico.

## Como ligar num projeto

Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa. O projeto não
guarda nenhum arquivo para ela.

## Detalhes

### O que ela dá

#### no_repositorio

`no_repositorio` é o nome do pedido para saber se uma pasta fica num repositório git.

Quem pede diz uma coisa só, que no código se chama `pasta`: o caminho da pasta. O caminho que não
começa no início do disco conta a partir da pasta de onde o comando roda.

A resposta é sim (`True`) quando a pasta, ou uma pasta acima dela, tem um `.git`, seja ele uma
pasta ou um arquivo, e não (`False`) quando nenhuma tem.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
