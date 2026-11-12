# leitura-completa

O vigia que só deixa a IA ler um documento inteiro, do começo ao fim.

## Para que serve

A IA pode ler só um pedaço de um arquivo, por exemplo das linhas 50 às 80, e decidir algo
sem ter visto o resto. Este vigia não deixa. Todo documento se lê inteiro: a partir do
começo, cada pedaço continuando de onde o outro parou, até o fim. Qualquer outro jeito de
ler um arquivo, como um comando no terminal ou uma ferramenta de busca ou de resumo, é
barrado.

## Como funciona

- **Antes de uma leitura:** só passa a que começa na primeira linha do arquivo ou na linha
  seguinte à última lida. Recomeçar da primeira linha vale.
- **Antes de outro uso que leia um arquivo:** barra.
- **Depois de um grupo de usos:** o vigia anota até que linha cada arquivo foi lido de
  verdade, pelo que a leitura devolveu, e não pelo que foi pedido.
- **Antes de uma escrita:** só passa quando nenhum arquivo está lido só em parte.
- **No fim da resposta:** não deixa terminar enquanto houver arquivo lido só em parte.

Se um arquivo cresce depois de lido, ele volta a ficar lido só em parte, e a leitura
continua na linha nova.

Quando barra ou trava, o vigia mostra o texto do projeto e, depois dele, cada arquivo e até
onde ele foi lido.

## Como ligar num projeto

O projeto configura o programa para chamar este vigia antes de cada uso de ferramenta,
depois de cada grupo de usos e no fim de cada resposta, sempre com o mesmo comando:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/leitura_completa.py \
        --config <configuração> --protocolo <protocolo> --motivo <texto> --fim <texto>

Nas pastas de dados dele ficam: a configuração, a folha do protocolo, o texto do uso barrado
e o texto da resposta travada.

## Detalhes

### As opções

- `--motivo`: o texto do uso barrado, que vem antes das partes que o barraram.
- `--fim`: o texto da resposta travada, que vem antes dos arquivos lidos só em parte.

Cada um desses textos termina na linha que apresenta as partes que vêm depois dele.

### O que conta numa leitura

- A leitura só passa quando traz só os campos que a folha conhece para ela: o caminho, o
  começo, quantas linhas e os campos livres.
- A leitura de um arquivo que não existe passa, porque não há o que ler.
- Do que a leitura devolveu, vale o trecho seguido de linhas numeradas que começa na
  primeira linha do arquivo ou na seguinte à última lida; o resto não conta. A linha vazia
  que o programa pode mostrar depois da última quebra de linha não conta.
- A última linha de um arquivo se conta no próprio arquivo, a cada conferência.
- O arquivo vale pelo caminho absoluto e sem atalhos: o mesmo arquivo, escrito de outro
  jeito, é o mesmo.

### O que ele mostra quando barra ou trava

Depois do texto do projeto, uma por linha e em ordem, as partes que causaram o bloqueio: o
arquivo e até onde ele foi lido, como `<arquivo>: <lida>/<última>`, ou o arquivo e o campo
que a folha não conhece, como `<arquivo>: <campo>`.

### A configuração

O molde está em `esquemas/leitura-completa.schema.json`.

| Chave | O que é |
| --- | --- |
| `estado` | a pasta das anotações, numa linha só; a anotação guarda, de cada arquivo lido, o número da primeira linha e o da última lida |

A anotação se grava inteira de uma vez e se lê pelo molde `esquemas/anotacao.schema.json`,
com o caminho de cada arquivo numa linha só. Só o vigia a muda. Dois grupos de usos ao mesmo
tempo esperam um pelo outro para gravá-la.

### O que ele usa da folha do protocolo

Os três momentos (`antes`, `lote` e `fim`); os modelos `nega` e `trava`; as ferramentas de
leitura, com os campos, a primeira linha, a forma da linha numerada e os campos livres; e as
ferramentas de escrita, as que trocam um trecho e as que gravam o arquivo inteiro.

### O que dá erro

A configuração, a folha, um texto, o formulário ou a anotação fora da forma; o formulário
sem a sessão; o lote sem a forma da linha numerada na folha. Nesses casos, ele escreve o
erro na saída de erro e sai com o código 2, sem responder nada.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
