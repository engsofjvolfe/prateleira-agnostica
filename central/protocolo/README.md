# protocolo

A peça da central que lê a folha do protocolo, para os vigias entenderem o programa.

## Para que serve

Um vigia é uma peça que o programa onde a IA trabalha chama sozinho, em certos momentos,
para saber se a IA pode seguir. Quando a IA vai usar uma ferramenta, o programa entrega ao
vigia um formulário preenchido, que diz o que vai acontecer. Os campos desse formulário têm
nomes que o programa escolheu, e o que o vigia responde também tem um formato certo. Cada
programa faz isso do seu jeito: a mesma ferramenta, ou o mesmo campo, tem um nome num
programa e outro nome em outro.

Nada que muda de um uso para outro fica escrito no código. Por isso, os nomes do programa
ficam numa folha do projeto, a folha do protocolo, e esta peça a lê para os vigias. Assim,
os mesmos vigias servem a qualquer programa: basta trocar a folha.

## Como funciona

- O programa chama o vigia e entrega o formulário.
- Com a folha, o vigia entende o formulário: qual é o momento, qual é a sessão, qual
  ferramenta a IA vai usar e com que entrada, que é o que a IA manda para a ferramenta, como
  o caminho de um arquivo.
- O vigia que deixa passar fica calado. O que tem algo a dizer monta o que responde com um
  dos modelos da folha.

## Como ligar num projeto

O projeto guarda a folha do protocolo do seu programa nas pastas de dados dele. Cada vigia
recebe o caminho dela na opção `--protocolo`, e o README de cada vigia diz o que ele usa da
folha. Esta peça chega ao projeto junto com a [central](../README.md), pelo vigia que a usa.

## Detalhes

### O formulário e a resposta

O formulário chega ao vigia pela entrada padrão, em JSON. O que o vigia responde sai pela
saída padrão, em JSON.

### A folha do protocolo

O molde está em `esquemas/protocolo.schema.json`.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `eventos` | o nome que o programa dá a cada momento: `antes` de a IA usar uma ferramenta, `fim` de uma resposta e, se o programa tiver, `lote`, depois de um grupo de usos, com o que cada um devolveu |
| `chaves` | o nome de cada campo do formulário: o do momento (`evento`), a `sessao`, a `ferramenta`, a `entrada`, a `pasta` de onde a ferramenta roda e o `fim_repetido`, o sinal de que o fim da resposta já foi travado uma vez; para o lote, a lista dos usos (`chamadas`) e, em cada um, a `resposta`, o que a ferramenta devolveu. A ferramenta e a entrada de um uso do lote vêm nos mesmos campos que no formulário de antes |
| `respostas` | o modelo de cada coisa que o vigia pode responder, em JSON: `nega` (barra o uso, com o motivo), `contexto` (entrega um texto à IA antes do uso) e `trava` (não deixa a resposta terminar, com o motivo). Em qualquer texto de dentro do modelo, `{texto}` vira o texto do vigia; o resto fica como está |
| `terminal` | a ferramenta de terminal (`ferramenta`) e o campo da entrada que traz o comando (`campo_comando`) |
| `buscas` | cada ferramenta de busca: o `nome` e o campo da entrada que traz o que se procura (`campo_padrao`) |
| `escritas` | os campos que trazem o caminho do arquivo escrito (`campos_caminho`); as ferramentas que trocam um trecho (`trocas`), cada uma com o campo do trecho de `antes`, o do de `depois` e o que pede para trocar `todas` as vezes; e as que gravam o arquivo inteiro (`inteiros`), cada uma com o campo do texto |
| `leituras` | cada ferramenta de leitura: o `nome`; o campo do caminho (`campo_caminho`), o da linha em que a leitura começa (`campo_comeco`) e o de quantas linhas ela lê (`campo_quantas`); quantas linhas ela lê sem esse campo (`linhas_sem_limite`); o número que o programa dá à primeira linha do arquivo (`primeira_linha`); e, se o programa tiver, a forma de uma linha numerada do que a leitura devolve (`linha_numerada`, uma expressão regular com o grupo `linha`) e os campos da entrada que não mudam o pedaço lido (`campos_livres`) |
| `resumos` | as ferramentas que leem por outro modelo de IA e entregam um resumo |

O `lote`, as `chamadas`, a `resposta`, a `linha_numerada` e os `campos_livres` podem
faltar: só o vigia que trata o lote precisa deles.

### O que dá erro na folha

A folha que não segue o molde dá erro, que diz o arquivo e o lugar do valor errado (ver
[conferencia-de-molde](../conferencia-de-molde/README.md)). Ela também dá erro, com o que
está errado e onde, quando: um nome não está numa linha só ou só tem espaços; dois momentos
têm o mesmo nome; dois campos têm o mesmo nome, também o das `chamadas` e o da `resposta`;
não há nenhum campo de caminho de escrita; uma ferramenta se repete numa lista; um campo
livre se repete; a forma da linha numerada não é uma expressão regular válida ou não tem o
grupo `linha`; um modelo não tem `{texto}` ou tem outra coisa entre chaves; ou um número de
leitura fica abaixo do menor possível (1 linha sem limite, 0 para a primeira linha).

Quando a folha ou o formulário está fora da forma, o erro é um `ErroDeDados` (ver
[erro-de-dados](../erro-de-dados/README.md)), que diz o que e onde.

### O que ela dá

No código do vigia, esta peça se chama `protocolo`, e cada pedido se escreve com esse nome
antes, como `protocolo.ler`.

#### ler

`ler` é o nome do pedido para ler a folha do protocolo.

Quem pede diz uma coisa só, que no código se chama `caminho`: o caminho da folha.

A resposta é a folha, já conferida.

O pedido dá erro nos casos de [O que dá erro na folha](#o-que-dá-erro-na-folha).

#### le_evento

`le_evento` é o nome do pedido para entender o formulário que o programa entregou.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `protocolo`: a folha, que é a resposta do `ler`.
2. `texto`: o texto do formulário.

A resposta são as partes do formulário: o momento (`antes`, `fim` ou `lote`) e cada campo
que ele traz, pelo nome que o campo tem no molde.

O pedido dá erro quando o formulário não é um objeto JSON e quando o nome do momento falta
ou é de outro momento, também o do lote quando a folha não o tem.

#### chamadas

`chamadas` é o nome do pedido para pegar os usos de um lote.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `protocolo`: a folha, que é a resposta do `ler`.
2. `partes`: as partes do formulário, que são a resposta do `le_evento`.

A resposta é a lista dos usos do lote, na ordem. Cada uso vem com a `ferramenta`, a
`entrada` e a `resposta` que o formulário traz dele.

O pedido dá erro quando a folha não diz o campo dos usos ou o da resposta, quando o
formulário não traz os usos, quando eles não são uma lista e quando um deles não é um
objeto.

#### textos_de

`textos_de` é o nome do pedido para pegar cada texto de dentro de um valor JSON.

Quem pede diz uma coisa só, que no código se chama `valor`: o valor JSON.

A resposta traz cada texto de dentro do valor, nos objetos e nas listas, na ordem.

#### caminho

`caminho` é o nome do pedido para saber o caminho inteiro de um arquivo que um uso nomeia.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `valor`: o caminho do arquivo, como o uso o escreveu.
2. `pasta`: a pasta de onde o uso roda.

A resposta é o caminho absoluto e sem atalhos, com o `~` trocado pela pasta do usuário. O
caminho relativo parte da pasta de onde o uso roda.

#### resposta

`resposta` é o nome do pedido para montar o que o vigia responde ao programa.

Quem pede diz três coisas, nesta ordem. No código, cada uma tem um nome:

1. `protocolo`: a folha, que é a resposta do `ler`.
2. `qual`: o nome de um modelo da folha, que é `nega`, `contexto` ou `trava`.
3. `texto`: o texto do vigia.

A resposta é uma cópia do modelo, com o texto do vigia no lugar de `{texto}`.

#### anotacao

`anotacao` é o nome do pedido para saber em que arquivo um vigia anota o que guarda de uma
sessão.

Quem pede diz as coisas abaixo, nesta ordem. No código, cada uma tem um nome:

1. `pasta`: a pasta das anotações.
2. `sessao`: a identificação da sessão.
3. `chaves`: as chaves, cada uma um texto. Pode vir uma, mais de uma ou nenhuma.

As duas primeiras têm de vir sempre.

A resposta é o caminho do arquivo da sessão, dentro da pasta das anotações. Com chaves, é o
caminho do arquivo da última chave, dentro da pasta da sessão, uma pasta dentro da outra na
ordem das chaves. Cada nome é a impressão digital (SHA-256) da identificação da sessão ou
da chave, e por isso o caminho nunca sai da pasta das anotações.

O pedido dá erro quando a sessão não tem identificação e quando uma chave não é texto.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
