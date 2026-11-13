# regras-de-codigo

O vigia que garante que o que a IA escreve segue as regras do projeto, sem depender da
palavra dela.

## Para que serve

Um texto de regras, a IA pode deixar de lado. Uma conferência pedida a ela, a IA pode fazer
pela metade e dizer que fez inteira. Este vigia confere por fora da IA e só a deixa terminar
a resposta quando três fatos estão provados: ela leu inteiro cada arquivo que escreveu; o
que ela escreveu passou nas conferências do projeto; e o que só uma pessoa confere tem o ok
dessa pessoa. Uma conferência é um programa do projeto que olha um arquivo e diz se ele
segue uma regra e, se não segue, onde está o erro.

Por exemplo: a IA escreve um arquivo de 80 linhas, diz que conferiu tudo e vai terminar. A
conferência de uma das regras do projeto aponta um erro na linha 12, e a IA só leu as 20
primeiras linhas. O vigia não deixa a resposta terminar e diz à IA o nome da regra, a linha
do erro e as linhas que faltam ler.

## Como funciona

Uma tarefa vai da primeira escrita num arquivo até o fim da resposta em que tudo passou. O
vigia não cria conferências: roda as que o projeto der.

1. **Quando a IA vai escrever num arquivo:** se é a primeira escrita nele na tarefa, ou se
   ela volta a ele depois de escrever em outro, o vigia entrega a ela os textos de regras
   que o projeto liga àquele arquivo. Depois, anota o arquivo como escrito.
2. **Depois que a IA lê um arquivo:** o vigia anota as linhas que ela leu.
3. **Antes de um comando no terminal** (a janela onde se digitam ordens para o computador):
   o vigia barra o comando que escreve num arquivo, o que roda um programa escrito ali mesmo
   e o que ele não consegue ler. Assim, a IA não escreve por um caminho que o vigia não
   acompanha.
4. **No fim da resposta:** se a tarefa escreveu arquivos, o vigia confere, em cada um:
   - **a leitura:** o arquivo foi lido do começo ao fim depois da última escrita nele; ler
     um pedaço não conta;
   - **as conferências:** cada conferência que o projeto liga ao arquivo roda nele e passa;
   - **o ok de uma pessoa:** se o arquivo é dos que só uma pessoa confere, o ok dela foi
     dado depois da última escrita.

   Se falta leitura ou se uma conferência não passou, o vigia não deixa a resposta terminar
   e diz à IA o que falta: o arquivo e as linhas não lidas, ou o nome da regra, o arquivo e
   o que a conferência apontou. Se falta só o ok de uma pessoa, a resposta termina com o
   aviso dos arquivos que esperam o ok. Quando tudo passa, a tarefa seguinte começa do zero.

## O ok de uma pessoa

Os arquivos que o projeto diz que só uma pessoa confere esperam o ok dela.

- **Como se dá o ok:** a pessoa lê o arquivo e, se concordar, manda na conversa a mensagem
  de ok com o caminho do arquivo (o nome dele, com as pastas onde ele está). A IA não manda
  mensagem no lugar da pessoa, então não consegue dar o ok.
- **Até quando vale:** o ok vale para o conteúdo que o arquivo tinha quando a mensagem foi
  mandada. Se o arquivo muda depois, o ok cai.
- **Enquanto falta o ok:** a IA só pode escrever nos arquivos que esperam o ok; qualquer
  outra escrita é barrada. Assim, nada mais anda até a pessoa conferir, e a IA ainda pode
  corrigir o arquivo se a pessoa pedir. Ao fim de cada resposta, o vigia lembra quais
  arquivos ainda esperam.

## Como ligar num projeto

O projeto configura o programa para chamar este vigia antes de cada uso das ferramentas que
escrevem arquivo e da de terminal, depois de cada uso da ferramenta de leitura, a cada
mensagem da pessoa e no fim de cada resposta, sempre com o mesmo comando, que passa pela
[roda](../../central/roda/README.md) da central:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/regras_de_codigo.py \
        --config <configuração> --terminal <configuração do terminal> \
        --protocolo <protocolo> --fim <texto> --bloqueio <texto>

Nas pastas de dados dele ficam: a configuração, a configuração do terminal, a folha do
protocolo, os textos das regras, as conferências, o texto do aviso do fim e o texto do aviso
do bloqueio.

## Detalhes

### As opções

- `--config`: a configuração do vigia.
- `--terminal`: a configuração do terminal.
- `--protocolo`: a folha do [protocolo](../../central/protocolo/README.md) do programa.
- `--fim`: o texto que abre o aviso do fim da resposta, antes da lista do que falta.
- `--bloqueio`: o texto que abre o aviso de bloqueio, antes da parte do comando ou da escrita
  que o causou.

### As conferências

Cada conferência é chamada com o caminho do arquivo como última parte do comando. O código
de saída diz o resultado:

| Código | O que quer dizer |
| --- | --- |
| `0` | o arquivo passou |
| `1` | o arquivo não passou; o que a conferência escreveu vai para a IA, junto com o nome da regra |
| outro | a conferência quebrou; o arquivo não passa, e o aviso diz que a conferência quebrou |

As conferências rodam na ordem da configuração, e os arquivos em ordem alfabética. Uma
conferência tem de dar sempre a mesma resposta para o mesmo arquivo.

### O que é barrado

- A escrita da IA na pasta das anotações do vigia.
- Enquanto falta o ok de uma pessoa, a escrita da IA em qualquer arquivo que não espera o ok.
- No terminal, o comando que escreve num arquivo: o que manda a saída para um arquivo com
  `>`, o que a configuração do terminal diz que sempre escreve e o que tem uma opção que, por
  ela, o faz escrever.
- No terminal, o comando que roda código escrito ali mesmo: o que traz um texto embutido com
  `<<`, o que tem uma opção que, pela configuração do terminal, o faz rodar código e o
  programa que, por ela, lê código do terminal quando é chamado sem arquivo.
- No terminal, o comando que não se lê.

Como a linha do comando é lida está na
[leitura do terminal](../../central/leitura-do-terminal/README.md) da central.

### A configuração

O molde está em `esquemas/regras-de-codigo.schema.json`. Os padrões de nome usam `*` para
qualquer trecho do caminho, e maiúscula e minúscula contam igual.

| Chave | O que é |
| --- | --- |
| `estado` | a pasta das anotações do vigia: os arquivos escritos, as linhas lidas e os oks |
| `regras` | a lista dos textos de regras; cada um com `texto`, o caminho dele, e `arquivos`, os padrões de nome a que ele vale |
| `conferencias` | a lista das conferências; cada uma com `nome`, o nome da regra que aparece no aviso, `comando`, o programa e as opções dele, e `arquivos`, os padrões de nome a que ela vale |
| `ok_de_pessoa.arquivos` | os padrões de nome dos arquivos que só uma pessoa confere |
| `ok_de_pessoa.mensagem` | o texto que abre a mensagem de ok da pessoa, antes do caminho do arquivo |

E na configuração do terminal:

| Chave | O que é |
| --- | --- |
| `destinos_livres` | os destinos para onde escrever não conta como escrita |
| `sempre_escrevem` | os comandos que sempre escrevem num arquivo |
| `escrevem_com_opcao` | para cada comando, as opções que o fazem escrever ou rodar código escrito no comando |
| `leem_codigo_sem_arquivo` | os programas que, chamados sem arquivo, leem código do próprio terminal |

### O que ele usa da folha do protocolo

O momento; a mensagem da pessoa; os modelos `contexto` (com as regras), `nega` (com o
bloqueio), `trava` (no fim, quando falta leitura ou conferência) e `aviso` (no fim, quando
falta só o ok de uma pessoa); a ferramenta de terminal, com o campo do comando; os campos do
caminho do arquivo escrito; e, da ferramenta de leitura, o caminho, a primeira linha lida e
a quantidade de linhas.

### O que dá erro

Falta um dos textos ou uma das configurações; um arquivo não segue o seu molde; o momento
não é conhecido; a sessão não tem identificação; a ferramenta de escrita não traz um campo
de caminho que a folha conhece; a ferramenta de leitura não traz os campos que a folha
conhece; a conferência da configuração não existe.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
