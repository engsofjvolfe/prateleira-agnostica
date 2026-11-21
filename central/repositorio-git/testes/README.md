# testes

Os testes da peça [repositorio-git](../README.md).

## Para que serve

O teste confere se a peça faz o que o README dela diz: responde sim quando a pasta, ou uma pasta
acima dela, tem um `.git`, e não quando nenhuma tem.

Por exemplo: se a peça olhar só a própria pasta, o teste falha, porque uma pasta de dentro de um
repositório deixa de ser vista como parte dele.

## Como funciona

1. O teste sorteia árvores de pastas, com uma semente fixa, para sair sempre igual, com nomes de
   letras de fora do ASCII e com espaços.
2. Ele põe um `.git` num nível sorteado da árvore, como pasta numa árvore e como arquivo na outra, e
   confere a resposta para cada pasta: sim do nível do `.git` para baixo, não acima dele.
3. Ele confere o caminho que conta a partir da pasta do comando, o atalho que leva para dentro do
   repositório e o caminho com `..` que volta para cima do `.git`.
4. No fim, ele mostra cada caso que não confere e quantos foram.

## Como ligar num projeto

Para rodar, o teste precisa do Python 3, num sistema que aceita atalhos. O comando:

    python3 -I <central>/roda/roda.py <central>/repositorio-git/testes/teste_repositorio_git.py <pasta da peça> <pasta de gravação>

`<central>` é a pasta central da prateleira; `<pasta da peça>`, a pasta da peça testada; e
`<pasta de gravação>`, uma pasta vazia, fora de um repositório git, onde o teste grava as árvores
de pastas.

A prova deste teste se faz pela peça [copias-estragadas](../../copias-estragadas/README.md), da
central, com a lista `estragos.json` desta pasta e o comando acima.

## Detalhes

### Os arquivos

| Arquivo | O que é |
| --- | --- |
| `teste_repositorio_git.py` | o teste |
| `estragos.json` | a lista de estragos, no molde da [copias-estragadas](../../copias-estragadas/README.md#a-lista-de-estragos) |

### Como o teste roda a peça

O teste lê o arquivo de código da peça da pasta que recebe, e nunca o código que o Python já
preparou e guardou, e faz os pedidos a ela por dentro. Assim, um estrago que não muda o tamanho do
arquivo não passa despercebido.

### O que dá erro

O teste acha um erro na peça quando ela dá uma resposta errada ou quebra. A pasta de gravação
dentro de um repositório git faz o próprio teste quebrar.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../../LICENSE-CONTENT.txt).*
