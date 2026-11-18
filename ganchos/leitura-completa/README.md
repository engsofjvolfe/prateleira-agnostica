# leitura-completa

O vigia que só deixa a IA ler um documento inteiro, do começo ao fim.

## Para que serve

A IA pode ler só um pedaço de um arquivo, por exemplo das linhas 50 às 80, e decidir algo
sem ter visto o resto. Este vigia não deixa. Todo documento se lê inteiro: a partir do
começo, cada pedaço continuando de onde o outro parou, até o fim. Qualquer outro jeito de
ler um arquivo, como um comando no terminal ou uma ferramenta de busca ou de resumo, é
barrado.

## Como funciona

- **A cada consulta, antes de tudo:** o vigia pergunta à
  [conferencia-de-protecao](../../central/conferencia-de-protecao/README.md) se a IA continua
  sem conseguir alterar os arquivos que o projeto fechou para ela, como as anotações deste
  vigia. Enquanto ela consegue, ele barra todo uso e não deixa a resposta terminar.
- **Antes de uma leitura:** só passa a que começa na primeira linha do arquivo ou na linha
  seguinte à última lida. Recomeçar da primeira linha vale.
- **Antes de outro uso que leia um arquivo:** barra.
- **Depois de um grupo de usos:** o vigia anota até que linha cada arquivo foi lido de
  verdade, pelo que a leitura devolveu, e não pelo que foi pedido.
- **Antes de uma escrita:** barra a que cai na pasta das anotações do vigia. As outras só
  passam quando nenhum arquivo está lido só em parte.
- **No fim da resposta:** não deixa terminar enquanto houver arquivo lido só em parte.

De cada arquivo, o vigia guarda uma impressão digital do trecho já lido: uma conta feita
sobre o texto desse trecho, que dá outro resultado quando o texto muda. Se o trecho já lido
muda, o que estava anotado deixa de valer, e o arquivo volta a ter de ser lido do começo. Se
o arquivo só cresce depois do trecho lido, a leitura continua na linha nova.

Quando barra ou trava, o vigia mostra o texto do projeto e, depois dele, cada arquivo e até
onde ele foi lido, ou o que a conferencia-de-protecao achou.

## Como ligar num projeto

O projeto configura o programa para chamar este vigia antes de cada uso de ferramenta,
depois de cada grupo de usos e no fim de cada resposta, sempre com o mesmo comando:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/leitura_completa.py \
        --config <configuração> --protocolo <protocolo> --lista <lista> \
        --motivo <texto> --fim <texto>

Nas pastas de dados dele ficam: a configuração, a folha do protocolo, a lista, o texto do uso
barrado e o texto da resposta travada.

## Detalhes

### As opções

- `--lista`: a lista dos arquivos e das pastas que o projeto fechou para a IA, na forma que a
  [conferencia-de-protecao](../../central/conferencia-de-protecao/README.md#a-lista) pede.
- `--motivo`: o texto do uso barrado, que vem antes das partes que o barraram.
- `--fim`: o texto da resposta travada, que vem antes dos arquivos lidos só em parte.

Cada um desses textos termina na linha que apresenta as partes que vêm depois dele.

### O que conta numa leitura

- A leitura só passa quando traz só os campos que a folha conhece para ela: o caminho, o
  começo, quantas linhas e os campos livres.
- A leitura de um arquivo que não existe, ou que não se lê como texto, passa, porque não há o
  que ler.
- Do que a leitura devolveu, vale o trecho seguido de linhas numeradas que começa na
  primeira linha do arquivo ou na seguinte à última lida; o resto não conta. A linha vazia
  que o programa pode mostrar depois da última quebra de linha não conta.
- A última linha de um arquivo se conta no próprio arquivo, a cada conferência. A quebra de
  linha, que é o sinal invisível que separa uma linha da outra, conta nas três formas em que
  ela pode estar escrita num arquivo, as mesmas que o leitor de texto da prateleira entende.
- O arquivo vale pelo caminho absoluto e sem atalhos: o mesmo arquivo, escrito de outro
  jeito, é o mesmo.

### O que ele mostra quando barra ou trava

Depois do texto do projeto, uma por linha e em ordem, as partes que causaram o bloqueio: o
arquivo e até onde ele foi lido, como `<arquivo>: <lida>/<última>`; o arquivo e o campo que a
folha não conhece, como `<arquivo>: <campo>`; o arquivo que a escrita alteraria na pasta das
anotações, pelo caminho dele; a ferramenta que lê de outro jeito, pelo nome que ela tem na
folha; ou cada linha que a conferencia-de-protecao entregou, como
`<caminho>: <tipo>`, com o caminho vazio na linha que não é de nenhum arquivo.

### A configuração

O molde está em `esquemas/leitura-completa.schema.json`.

| Chave | O que é |
| --- | --- |
| `estado` | a pasta das anotações, numa linha só; a anotação guarda, de cada arquivo lido, o número da primeira linha, o da última lida e a impressão digital do trecho lido |

A anotação se grava inteira de uma vez e se lê pelo molde `esquemas/anotacao.schema.json`,
com o caminho de cada arquivo numa linha só. Só o vigia a muda. Dois grupos de usos ao mesmo
tempo esperam um pelo outro para gravá-la.

### O que ele usa da folha do protocolo

Os três momentos (`antes`, `lote` e `fim`); os modelos `nega` e `trava`; as ferramentas de
leitura, com os campos, a primeira linha, a forma da linha numerada e os campos livres; as
ferramentas de escrita, as que trocam um trecho e as que gravam o arquivo inteiro, com os
campos do caminho do arquivo escrito; e os outros jeitos de ler um arquivo, que são a
ferramenta de terminal, as de busca e as que leem por outro modelo de IA e entregam um resumo.

### O que dá erro

A configuração, a folha, a lista, um texto, o formulário ou a anotação fora da forma; o
formulário sem a sessão; o lote sem a forma da linha numerada na folha; a escrita sem o caminho
num campo que a folha conhece, porque aí não se sabe onde ela cai. Nesses casos, ele escreve o
erro na saída de erro e sai com o código 2, sem responder nada.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
