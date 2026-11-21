# rodape-de-documento

A peça da central que monta, põe, acha e tira o rodapé de um documento.

## Para que serve

O rodapé é um texto que fica no fim de um documento. Mais de uma peça lida com o rodapé de um
documento. Se cada uma fizesse isso do seu jeito, o mesmo documento ficaria com rodapés diferentes
conforme a peça. Por isso, o rodapé se monta, se põe, se acha e se tira só aqui, a partir de um
arquivo de dados que o projeto escreve uma vez.

Por exemplo: o rodapé tem um link, que é um texto que leva a outro arquivo quando se clica nele.
O link vale a partir de uma pasta. Num documento de outra pasta, o mesmo link levaria a lugar
nenhum. Esta peça monta o rodapé desse documento com o link refeito para a pasta dele.

## Como funciona

1. O projeto escreve, num arquivo de dados, os tipos de documento e os rodapés dele. Um tipo de
   documento é um jeito de escrever documentos, com as regras dele, como a forma de um link. Cada
   rodapé tem um modelo, que é o texto do rodapé escrito uma vez para cada tipo, e diz quais
   documentos o levam.
2. Para um documento, a peça acha o tipo dele e os rodapés que ele leva. Quem diz é a lista do
   projeto ou, quando o projeto quer, uma linha do próprio documento.
3. A peça monta cada rodapé a partir do modelo. Primeiro, refaz cada link para que ele funcione a
   partir da pasta do documento. Depois, troca cada campo
   pelo valor dele. Um campo é um nome escrito no modelo no lugar de algo que muda de um documento
   para outro, como o caminho do documento, que é o endereço dele dentro da pasta do projeto.
4. A peça põe cada rodapé no lugar dele: no fim do documento ou no fim de cada seção. Uma seção é
   uma parte do documento que começa numa linha própria, como um título.
5. Para trocar ou tirar um rodapé, a peça acha o rodapé que o documento já tem. Quando o tipo tem
   uma marca, que é uma linha que diz "aqui começa o rodapé", ela o acha pela marca. Sem marca,
   ela o acha pelo texto dos modelos.

## Como ligar num projeto

Esta peça chega ao projeto junto com a central, pela peça que a usa.

O projeto guarda para ela, nas pastas de dados dele, o arquivo dos rodapés, em JSON, e os
arquivos dos modelos. A peça que usa esta diz, no README dela, como o comando recebe o caminho do
arquivo dos rodapés e o da pasta raiz, que é a pasta de onde contam os caminhos dos documentos.

## Detalhes

### O arquivo dos rodapés

O molde está em `esquemas/rodape-de-documento.schema.json`. Os caminhos que o arquivo escreve
contam a partir da pasta dele. As expressões regulares se escrevem do jeito do Python.

| Chave | O que é |
| --- | --- |
| `versao_schema` | `1` |
| `tipos` | os tipos de documento: o nome de cada um e o que ele é (ver [Um tipo](#um-tipo)) |
| `rodapes` | os rodapés: o nome de cada um e o que ele é (ver [Um rodapé](#um-rodapé)) |
| `campos` | opcional: como um campo se escreve e os valores que o projeto dá (ver [Os campos](#os-campos)) |
| `formato_da_data` | opcional: como uma data se escreve, com os códigos de data do Python, como `%Y` para o ano, `%m` para o mês e `%d` para o dia; é obrigatório quando um modelo tem um campo de data |
| `sem_rodape` | opcional: o nome que, numa linha de escolha, diz que o documento fica sem rodapé |

#### Um tipo

| Chave | O que é |
| --- | --- |
| `arquivos` | os padrões dos arquivos do tipo, um ou mais (ver [Os padrões](#os-padrões)) |
| `separador` | o texto entre o texto do documento e o rodapé, e entre o rodapé e o que vem depois dele: só espaços e quebras de linha, terminando numa quebra de linha, para o rodapé começar numa linha própria; no JSON, `\n` é uma quebra de linha |
| `links` | opcional: as expressões regulares que acham um link, cada uma com o grupo `alvo`, escrito `(?P<alvo>...)`, que pega o lugar para onde o link leva |
| `partes_sem_link` | opcional: as expressões regulares das partes do modelo em que um link fica como está, como um trecho de código |
| `marca` | opcional: a linha que marca o começo de um rodapé |
| `linha_de_escolha` | opcional: a expressão regular da linha em que um documento diz o rodapé que leva, com o grupo `nome`, escrito `(?P<nome>...)` |
| `linha_de_secao` | opcional: a expressão regular da linha que começa uma seção |
| `linha_de_fim` | opcional: a expressão regular da linha antes da qual fica o rodapé do fim, quando ele não fica no fim do arquivo |

As expressões de `links` e de `partes_sem_link` se procuram no texto inteiro do modelo. As de
`linha_de_escolha`, `linha_de_secao` e `linha_de_fim` se procuram em cada linha, sem a quebra de
linha. Uma linha é igual à `marca` quando tem o mesmo texto, sem contar os espaços das pontas.

#### Um rodapé

| Chave | O que é |
| --- | --- |
| `modelos` | o modelo de cada tipo: o nome do tipo e o caminho do arquivo do modelo |
| `documentos` | os padrões dos documentos que o rodapé cobre, um ou mais |
| `fora` | opcional: os padrões dos documentos que ele não cobre, mesmo quando seguem um de `documentos` |
| `lugar` | `fim`, para o fim do documento, ou `secao`, para o fim de cada seção |

O rodapé cobre só os documentos dos tipos que têm modelo nele. O modelo é um arquivo de texto em
UTF-8. Ele vale sem as linhas em branco do começo e sem os espaços e as quebras de linha do fim.

#### Os campos

| Chave | O que é |
| --- | --- |
| `abre` | o texto que abre um campo |
| `fecha` | o texto que fecha um campo |
| `valores` | opcional: os valores que o projeto dá, cada um com o nome do campo |

Um campo se escreve com o texto de `abre`, o nome do campo e o texto de `fecha`. O texto de
`abre` sem o de `fecha` depois dele fica como está. Sem `campos`, os modelos não têm campos. O
valor posto no lugar de um campo não se lê de novo: um link ou um campo dentro dele fica como
está.

Além dos de `valores`, a peça dá estes campos:

| Campo | O valor |
| --- | --- |
| `caminho` | o caminho do documento a partir da pasta raiz, com `/` entre as partes |
| `nome` | o nome do arquivo do documento |
| `mudanca` | a data da última mudança do texto do documento, sem os rodapés: a do último commit em que ele mudou, seguindo o documento quando ele muda de nome ou de pasta; com uma mudança que ainda não entrou num commit, a data do dia |
| `hoje` | a data do dia, no relógio do computador |

- A data de um commit é a que ele guarda, no fuso em que foi feito.
- O campo `mudanca` só existe quando a pasta raiz fica num repositório git, pelo que a peça
  repositorio-git, da central, responde.
- Sem marca, a troca do texto de um modelo também conta como mudança do texto, porque o rodapé
  velho não se acha (ver [Como se acha o rodapé](#como-se-acha-o-rodapé-que-um-documento-tem)).

### Os padrões

Um padrão diz quais arquivos ele pega pelo caminho inteiro deles a partir da pasta raiz. As
partes de um caminho são os nomes entre as `/`.

| No padrão | O que pega |
| --- | --- |
| `*` | qualquer pedaço de uma parte, também vazio |
| `?` | um caractere qualquer de uma parte |
| `**`, quando é uma parte inteira | nenhuma, uma ou mais partes, com as `/` entre elas |
| qualquer outro caractere | ele mesmo |

Cada padrão tem uma linha só, com algo além de espaços, e não se repete na mesma lista.

### Os links

- Um link do modelo é cada pedaço que uma expressão de `links` acha, fora das `partes_sem_link`.
- O `alvo` que começa com um esquema, com `#` ou com `/` fica como está. O esquema é um nome
  seguido de `:`, como `https:` ou `mailto:`.
- Qualquer outro alvo é o caminho de um arquivo ou de uma pasta, contado a partir da pasta do
  modelo. Depois de um `#`, ele pode ter um lugar dentro desse arquivo. O caminho se lê como está
  escrito, sem trocar códigos como `%20`, e tem de levar a um arquivo ou a uma pasta que existe.
- No rodapé de um documento, esse caminho vira o caminho do mesmo arquivo a partir da pasta do
  documento, com `/` entre as partes e com a `/` do fim quando ele tinha uma. O que vinha depois
  do `#` continua depois dele. O resto do link fica como está.
- O link refeito tem de ser achado inteiro pela mesma expressão, com o caminho novo no `alvo`.
  Por isso, o modelo escreve o link de um jeito que aceite qualquer caminho do projeto, também um
  caminho com espaços.

### Onde o rodapé fica

O documento se divide em partes. Sem `linha_de_secao`, ele é uma parte só. Com ela, a primeira
parte é o começo, até a primeira linha de seção, e cada seção é uma parte, de uma linha de seção
até a próxima. A última parte termina antes da última linha que a `linha_de_fim` acha ou, sem
ela, no fim do arquivo.

- O rodapé de lugar `secao` fica no fim de cada seção. O começo não é uma seção.
- O rodapé de lugar `fim` fica no fim da última parte, depois do rodapé da última seção.
- No fim de uma parte ficam: o texto dela, sem os espaços e as quebras de linha do fim; o
  `separador`; e o rodapé. Quando algo vem depois do rodapé, o `separador` fica entre os dois. O
  arquivo termina com uma quebra de linha.
- O documento vazio fica só com o rodapé.
- Com `marca`, cada rodapé começa com a linha da marca.
- O rodapé e o separador entram com a quebra de linha que o documento usa: a primeira que aparece
  nele ou, sem nenhuma, `\n`.

### Qual rodapé um documento leva

- Um documento é um arquivo de um dos tipos. O arquivo dos rodapés e os modelos não são
  documentos.
- Quando o tipo tem `linha_de_escolha` e o documento tem essa linha, ele leva os rodapés que as
  linhas dele nomeiam. O nome de `sem_rodape` diz que ele não leva nenhum e só vale sozinho.
- Quando não, ele leva cada rodapé que o cobre: o rodapé com um padrão de `documentos` que ele
  segue e nenhum de `fora`.
- Um documento leva no máximo um rodapé de cada lugar.

### Como se acha o rodapé que um documento tem

- **Com marca:** em cada parte, o rodapé começa na primeira linha igual à marca e vai até o fim
  da parte. Por isso, a marca só aparece nos rodapés: o texto que vem depois dela, até o fim da
  parte, conta como rodapé. Numa parte cabem: no começo, um rodapé quando não há seções e nenhum
  quando há; em cada seção, um; na última seção, dois.
- **Sem marca:** a peça procura o rodapé só nos lugares em que o documento leva um. No fim de
  cada parte desses lugares, o rodapé é o texto de um dos modelos do tipo para aquele lugar. Ele
  começa no começo de uma linha e pode ter qualquer caminho nos links, qualquer valor nos campos
  e qualquer espaço ou quebra de linha onde o modelo tem um. Depois dele, só há espaços e quebras
  de linha. Na última parte, acha-se primeiro o rodapé do fim e, antes dele, o da seção.
- Sem marca, quando o texto de um modelo muda, o rodapé velho não se acha mais: ele fica no
  documento, e o novo entra depois dele.
- Por isso, só com marca se acha, para tirá-lo, o rodapé de um lugar em que o documento não leva
  nenhum.

### Quando um documento está em dia

Um documento está em dia quando o texto dele é igual ao que esta peça poria nele. No campo
`hoje`, vale qualquer data escrita no `formato_da_data`.

### O que dá erro

Ao ler o arquivo dos rodapés:

- o arquivo que não se lê como JSON ou que sai do molde;
- um padrão repetido na mesma lista;
- uma expressão regular que não vale ou que não tem o grupo que pede;
- um nome de tipo, em `modelos`, que não está em `tipos`;
- o lugar `secao` num rodapé com modelo para um tipo sem `linha_de_secao`;
- o nome de `sem_rodape` igual ao de um rodapé;
- um valor de `valores` com o nome de um campo da peça;
- um modelo que falta, que não se lê em UTF-8 ou que fica vazio;
- um modelo com uma linha igual à marca, ou com uma linha que a `linha_de_escolha`, a
  `linha_de_secao` ou a `linha_de_fim` acham;
- um link do modelo cujo caminho não leva a um arquivo ou a uma pasta que existe;
- dois links do modelo que se cruzam, ou um campo dentro do `alvo` de um link;
- um campo do modelo sem valor, um campo de data sem `formato_da_data` e o campo `mudanca` fora
  de um repositório git.

Num documento:

- um arquivo que segue os padrões de dois tipos;
- uma linha de escolha com um nome que não é de um rodapé, com o de `sem_rodape` junto de outro,
  ou com um rodapé sem modelo para o tipo do documento;
- dois rodapés do mesmo lugar;
- mais linhas iguais à marca numa parte do que rodapés que cabem nela;
- um link refeito que a expressão dele não acha mais inteiro.

Todo erro é um `ErroDeDados`, o erro da central que diz o que está errado e onde. A mensagem diz
o arquivo e o lugar dentro dele.

### O que ela dá

#### le_rodapes

`le_rodapes` é o nome do pedido para ler o arquivo dos rodapés.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `caminho`: o caminho do arquivo dos rodapés.
2. `raiz`: o caminho da pasta raiz dos documentos.

A resposta são os rodapés, já conferidos. É o que os outros pedidos recebem em `rodapes`.

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro) ao ler o arquivo dos rodapés.

#### eh_documento

`eh_documento` é o nome do pedido para saber se um arquivo é um documento.

Quem pede diz duas coisas, nesta ordem. No código, cada uma tem um nome:

1. `rodapes`: a resposta do `le_rodapes`.
2. `caminho`: o caminho do arquivo a partir da pasta raiz, com `/` entre as partes.

A resposta é sim (`True`) ou não (`False`).

O pedido dá erro quando o arquivo segue os padrões de dois tipos.

#### com_rodapes

`com_rodapes` é o nome do pedido para ter o texto que um documento deve ter.

Quem pede diz três coisas, nesta ordem. No código, cada uma tem um nome:

1. `rodapes`: a resposta do `le_rodapes`.
2. `caminho`: o caminho do documento a partir da pasta raiz, com `/` entre as partes.
3. `texto`: o texto do documento, com as quebras de linha como estão no arquivo.

A resposta é o texto do documento com cada rodapé que ele leva no lugar e sem os que ele não leva
mais, com a data do dia no campo `hoje`.

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro) num documento.

#### problemas

`problemas` é o nome do pedido para saber quais rodapés de um documento estão fora do dia.

Quem pede diz as mesmas três coisas do `com_rodapes`, na mesma ordem.

A resposta é a lista dos rodapés fora do dia, em ordem de linha. A lista vazia diz que o
documento está em dia. Cada item traz o lugar (`fim` ou `secao`), a linha, contada a partir de 1,
e o motivo:

| Motivo | Quando | A linha |
| --- | --- | --- |
| `falta` | a parte não tem o rodapé que leva | a última linha com texto da parte, ou a 1 no documento vazio |
| `diferente` | a parte tem um rodapé, mas não o certo, ou não no jeito certo | a primeira linha do rodapé |
| `sobra` | a parte tem um rodapé que não leva | a primeira linha do rodapé |

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro) num documento.

#### rodapes_montados

`rodapes_montados` é o nome do pedido para ter os rodapés de um documento, montados.

Quem pede diz as mesmas três coisas do `com_rodapes`, na mesma ordem.

A resposta traz cada rodapé que o documento leva: o lugar e o texto, montado para ele, sem a
linha da marca e com a data do dia no campo `hoje`.

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro) num documento.

#### separa

`separa` é o nome do pedido para separar o texto de um documento dos rodapés que ele tem.

Quem pede diz as mesmas três coisas do `com_rodapes`, na mesma ordem.

A resposta traz duas coisas: o texto sem os rodapés que o documento tem; e, de cada rodapé, o
lugar e as linhas em que ele está. Serve a quem confere a forma de um documento e deixa os
rodapés de lado.

O pedido dá erro nos casos de [O que dá erro](#o-que-dá-erro) num documento.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
