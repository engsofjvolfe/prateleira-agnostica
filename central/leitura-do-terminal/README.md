# leitura-do-terminal

A peça da central que desmonta uma linha do terminal nos comandos que ela vai rodar.

## Para que serve

Uma linha digitada no terminal pode ter mais de um comando. Nos exemplos abaixo, os nomes
dos comandos são inventados:

- `lista; procura segredo notas.txt` tem dois comandos: `lista` e `procura`, que procura a
  palavra "segredo" no arquivo `notas.txt`;
- `mostra "não use procura"` tem um comando só, `mostra`. Ali, "procura" é só uma palavra
  dentro das aspas.

Uma peça que barra a busca tem de barrar a primeira linha e deixar passar a segunda. Para
isso, não basta procurar a palavra "procura": é preciso ler a linha como o terminal lê. Esta
peça faz essa leitura para as peças que precisam saber o que uma linha roda.

## Como funciona

A peça lê a linha do jeito que o terminal lê:

- separa os comandos que a linha junta, como os dois do primeiro exemplo;
- acha os comandos escondidos dentro de outro comando;
- respeita as aspas, para não confundir um texto com um comando, como no segundo exemplo;
- diz quais palavras são comandos de verdade.

A linha que não dá para ler, como uma com aspas abertas e nunca fechadas, dá um erro
próprio.

## Como ligar num projeto

O projeto guarda a configuração desta peça nas pastas de dados dele e dá o caminho dela à
peça que a usa, na opção `--terminal`. Esta peça chega ao projeto junto com a
[central](../README.md), pela peça que a usa.

## Detalhes

### O que ela reconhece

- Os sinais que juntam comandos ou mandam a saída para um arquivo (como `|`, `;` ou `>`),
  também colados um no outro, as aspas, a barra que protege um caractere e os comentários.
- Os comandos de dentro de `$( )` e de crases, também entre aspas.
- O texto que vai para outro comando rodar: depois de um comando que, pela configuração,
  roda o texto que recebe, cada palavra se lê também como uma linha.
- O arquivo para onde um comando manda a saída, ou de onde ele lê, que fica fora das
  palavras do comando, junto com o número colado antes do sinal (como o `2` de `2>`).
- As palavras que rodam como comando: a primeira, menos uma atribuição (como `NOME=valor`);
  a que vem depois de uma palavra com `$` ou crase, que o terminal troca por outra coisa e
  que pode sumir da linha; e toda palavra que vem depois de um prefixo da configuração ou
  de um comando que roda o texto que recebe.
- O comando de mais de uma palavra, também com outras palavras no meio: com nomes
  inventados, `programa parte`, também em `programa -x pasta parte`.
- A opção dentro de uma palavra: a curta também junto de outras curtas (`-a` em `-ba`), e a
  longa também com um valor (`--nome` em `--nome=1`).

A linha com aspa, crase ou `$(` sem fechar não se lê. O mesmo vale para a linha que manda
rodar um texto assim.

### O que ela não vê

- O texto que vai para um comando que a configuração não cita entre os que rodam o texto
  que recebem.
- O nome de comando que o terminal monta na hora de rodar, com `$`, crase ou chaves.

### A configuração

O molde está em `esquemas/leitura-do-terminal.schema.json`.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `prefixos` | as palavras depois das quais as outras também rodam como comando |
| `rodam_texto` | os comandos que rodam o texto que recebem: depois de cada um, cada palavra se lê também como uma linha, e as palavras também rodam como comando |

### Os sinais

Cada sinal do terminal tem um nome, no começo do arquivo `leitura_do_terminal.py`, e a peça
que precisa de um sinal o pede pelo nome.

| Nome | Sinal | O que faz na linha |
| --- | --- | --- |
| `ESCRITA` | `>` | manda a saída para um arquivo |
| `LEITURA` | `<` | lê de um arquivo |
| `TEXTO_EMBUTIDO` | `<<` | traz, nas linhas seguintes, um texto para o comando ler |
| `ABRE` | `(` | abre um grupo de comandos |
| `FECHA` | `)` | fecha um grupo de comandos |
| `DUPLICACAO` | `&` | depois de `>` ou de `<`, aponta para outra saída ou entrada, pelo número dela |
| `FECHA_DESCRITOR` | `-` | depois de `>&` ou de `<&`, fecha a saída ou a entrada |
| `TROCA` | `$` | começa o que o terminal troca por outra coisa |
| `SUBSTITUICAO` | `$(` | abre um comando de dentro, que o terminal troca pelo que ele escreve |
| `CRASE` | `` ` `` | abre e fecha um comando de dentro |
| `ASPA_SIMPLES` | `'` | abre e fecha um texto que fica como está |
| `ASPA_DUPLA` | `"` | abre e fecha um texto em que o terminal ainda troca o que começa por `$` ou crase |
| `ESCAPE` | `\` | protege o caractere seguinte |
| `COMENTARIO` | `#` | no começo de uma palavra, abre um comentário, que vai até o fim da linha |
| `QUEBRA` | a quebra de linha | separa dois comandos |
| `ATRIBUICAO` | `=` | separa um nome do valor dele |
| `OPCAO` | `-` | começa uma opção curta |
| `OPCAO_LONGA` | `--` | começa uma opção longa |

### O que ela dá

#### lidos

`lidos` é o nome do pedido para ler uma linha do terminal.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `comando`: a linha.
2. `rodam_texto`: os comandos que rodam o texto que recebem, como na
   [configuração](#a-configuração).

A primeira tem de vir sempre. A segunda pode faltar: sem ela, nenhum texto se lê como uma
linha.

A resposta traz um item para a linha, um para cada comando de dentro dela e um para cada
texto que ela manda rodar, nessa ordem. Cada item traz duas coisas, nesta ordem:

1. As partes: cada palavra ou sinal, com a marca de qual dos dois é.
2. As palavras de cada comando.

O comando de dentro fica, na palavra dele, como está escrito.

O pedido dá o erro `ComandoIlegivel` quando um comando não se lê.

#### configuracao_do_terminal

`configuracao_do_terminal` é o nome do pedido para ler a [configuração](#a-configuração).

Quem pede diz uma coisa só, que no código se chama `arquivo`: o caminho da configuração.

A resposta é a configuração lida, com os `prefixos` e os `rodam_texto`.

O pedido dá erro quando a configuração não segue o molde. O erro diz o arquivo e o lugar do
valor errado (ver [conferencia-de-molde](../conferencia-de-molde/README.md)).

#### posicoes_de_comando

`posicoes_de_comando` é o nome do pedido para saber quais palavras de um comando rodam como
comando, pelo que está em [O que ela reconhece](#o-que-ela-reconhece).

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `palavras`: as palavras de um comando.
2. `prefixos`: os prefixos, como na [configuração](#a-configuração).

A resposta é a lista das posições dessas palavras. A primeira palavra tem a posição 0.

#### depois_do_comando

`depois_do_comando` é o nome do pedido para saber se um comando da linha é um comando
procurado e, quando é, o que vem depois dele.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `comando`: o comando procurado, de uma ou mais palavras.
2. `palavras`: as palavras de um comando da linha.

Quando as palavras começam pelo comando procurado, a resposta são as palavras que vêm
depois dele. Começar por ele é ter a primeira palavra dele pelo nome, sem o caminho, e as
outras na ordem, também com outras palavras no meio. Quando não começam, a resposta é nada
(`None`).

#### comandos_achados

`comandos_achados` é o nome do pedido para achar cada vez que uma linha roda um dos
comandos procurados.

Quem pede diz três coisas, nesta ordem. No código, cada uma tem um nome:

1. `comando`: a linha.
2. `procurados`: a lista dos comandos procurados, cada um de uma ou mais palavras.
3. `terminal`: a configuração lida, que é a resposta do `configuracao_do_terminal`.

A resposta traz um item para cada vez que a linha, um comando de dentro dela ou um texto
que ela manda rodar roda um dos procurados, na ordem. Cada item diz três coisas, nesta
ordem:

1. Qual dos procurados foi achado, pela posição dele na lista. O primeiro tem a posição 0.
2. As palavras que vêm depois dele.
3. O trecho do comando, da palavra dele em diante.

O pedido dá o erro `ComandoIlegivel` quando um comando não se lê.

#### opcao_bate

`opcao_bate` é o nome do pedido para saber se uma opção aparece numa palavra, pelo que está
em [O que ela reconhece](#o-que-ela-reconhece).

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `opcao`: a opção.
2. `palavra`: a palavra.

A resposta é sim ou não.

#### eh_redirecionamento

`eh_redirecionamento` é o nome do pedido para saber se um sinal manda a saída para um
arquivo ou lê de um arquivo.

Quem pede diz uma coisa só, que no código se chama `sinal`: o sinal.

A resposta é sim ou não.

#### ComandoIlegivel

`ComandoIlegivel` é o nome do erro que esta peça dá quando a linha não se lê. A mensagem
dele é o sinal que ficou sem fechar.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
