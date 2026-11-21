# leitura-do-terminal-temporaria

A cópia temporária da [leitura-do-terminal](../leitura-do-terminal/README.md), com as listas
de quem escreve num arquivo ou roda código.

## Para que serve

A leitura do terminal desmonta uma linha do terminal nos comandos que ela vai rodar. Um vigia
que barra a escrita feita por um comando precisa saber também quais comandos escrevem num
arquivo e quais rodam código escrito na própria linha. Essas listas são do projeto e ficam na
configuração do terminal, que a leitura do terminal ainda não aceita com elas.

Mudar a leitura do terminal agora poderia quebrar as peças que já a usam. Por isso, esta
cópia traz a leitura do terminal com essas listas a mais na configuração, e a leitura do
terminal fica como está.

Por exemplo: o projeto lista, na configuração do terminal, os comandos que sempre escrevem num
arquivo. O vigia pede a configuração a esta cópia e recebe essa lista junto com o resto.

## Como funciona

Tudo o que a [leitura-do-terminal](../leitura-do-terminal/README.md#como-funciona) faz, esta
cópia faz igual. A mais, a configuração lida traz as quatro listas de
[A configuração](#a-configuração).

## A cópia temporária

Esta cópia é o jeito de mudar a leitura do terminal sem quebrar ninguém, em três fases: o novo
nasce ao lado do antigo, sem mexer nele; quem usa o antigo passa para o novo; e o antigo sai.
Quando os testes existirem, as peças que usam a leitura do terminal passam a usar esta cópia,
ela toma o lugar e o nome dela, e esta pasta sai.

## Como ligar num projeto

Enquanto esta cópia existe, o projeto guarda, nas pastas de dados dele, uma configuração do
terminal na forma dela para a peça que a usa, que a recebe na opção `--terminal`. Essa
configuração não serve às peças que usam a leitura do terminal, que recusa as chaves que não
conhece. Esta peça chega ao projeto junto com a [central](../README.md), pela peça que a usa.

## Detalhes

### A configuração

O molde está em `esquemas/leitura-do-terminal-temporaria.schema.json`. É o da
[configuração da leitura do terminal](../leitura-do-terminal/README.md#a-configuração), com
estas chaves a mais, que podem faltar:

| Chave | O que é |
| --- | --- |
| `destinos_livres` | os destinos para onde mandar a saída não conta como escrita |
| `sempre_escrevem` | os comandos que sempre escrevem num arquivo |
| `escrevem_com_opcao` | para cada comando, as opções que o fazem escrever ou rodar código escrito no comando |
| `leem_codigo_sem_arquivo` | os programas que, chamados sem arquivo, leem código do próprio terminal |

A chave que falta vale como lista vazia.

### O que ela dá

No código da peça que a usa, esta peça se chama `leitura_do_terminal_temporaria`. Ela dá os
mesmos nomes da [leitura-do-terminal](../leitura-do-terminal/README.md#o-que-ela-dá), com
esta diferença:

#### configuracao_do_terminal

A resposta traz também as quatro listas: `destinos_livres`, `sempre_escrevem`,
`escrevem_com_opcao` e `leem_codigo_sem_arquivo`.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
