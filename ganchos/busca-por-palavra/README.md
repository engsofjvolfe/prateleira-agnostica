# busca-por-palavra

O vigia que barra a busca por palavra.

## Para que serve

A IA pode procurar uma palavra nos arquivos e ler só o pedaço em volta do que achou,
decidindo sem ter lido o resto. Este vigia barra essa busca. O caminho certo é listar os
títulos de um texto e ler inteiro o que trata do assunto.

Ele deixa passar só duas buscas:

- a dos padrões que o projeto libera na configuração;
- se o projeto quiser, a busca de um código exato num arquivo feito para isso. Com o código,
  a busca acha sempre as mesmas entradas, sem ler o arquivo inteiro.

Serve à fase em que tudo se lê inteiro. Quando já se sabe o endereço de cada coisa, a busca
só acha o lugar, e o que ela acha se lê inteiro; aí o projeto desliga este vigia.

## Como funciona

- **Antes de tudo:** pergunta à
  [conferencia-de-protecao](../../central/conferencia-de-protecao/README.md) se a IA continua
  sem conseguir alterar os arquivos que o projeto fechou para ela, como a configuração deste
  vigia. Enquanto ela consegue, barra todo uso.
- **No terminal:** barra o comando de busca, ou um comando de busca de dentro de outro,
  quando o que se procura (o padrão) não é um dos liberados. Quais comandos são de busca, o
  projeto diz na configuração. Barra também a busca que tira de um arquivo o que procurar, a
  busca em que não dá para saber o que se procura e o comando que não dá para ler.
- **Numa ferramenta de busca do programa:** barra a busca cujo padrão não é um dos
  liberados.

## Como ligar num projeto

O projeto configura o programa para chamar este vigia antes de cada uso da ferramenta de
terminal e das de busca, com este comando:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/busca_por_palavra.py \
        --config <configuração> --terminal <configuração do terminal> \
        --protocolo <protocolo> --lista <lista> --motivo <texto>

Nas pastas de dados dele ficam: a configuração, a configuração do terminal, a folha do
protocolo, a lista e o texto do motivo do bloqueio.

## Detalhes

### As opções

- `--lista`: a lista dos arquivos e das pastas que o projeto fechou para a IA, na forma que a
  [conferencia-de-protecao](../../central/conferencia-de-protecao/README.md#a-lista) pede.
- `--motivo`: o texto do bloqueio, que vem antes da parte do comando que o causou ou do que a
  conferencia-de-protecao achou.
- `--exatas <arquivo> <forma>`: liga a busca exata para um arquivo. A forma é a expressão
  regular que cada padrão tem de seguir inteiro. A opção vem uma vez para cada arquivo, cada
  um com a sua forma. O caminho do arquivo parte da pasta de onde o comando roda. No comando
  que o programa roda, a forma vai entre aspas simples, para o terminal não mexer nela. O
  padrão com um sinal que a busca lê como padrão (`\ . * + ? [ ] ( ) { } ^ $ |`) fica de
  fora da busca exata, também quando segue a forma: com ele, a busca acharia mais que o
  código.

### Como ele lê uma busca do terminal

- As opções de um comando de busca são as que a configuração cita para ele: as de padrão,
  as que tiram os padrões de um arquivo, as outras que levam um valor e as que não levam
  nenhum. A busca com uma opção que a configuração não cita é barrada: sem conhecer a
  opção, não dá para saber se a palavra seguinte é o valor dela.
- O valor de uma opção vem na palavra seguinte, colado na opção ou depois de um `=`. As
  opções de uma letra podem vir juntas numa palavra só, e a que leva valor fica por último.
  A opção que não leva valor, escrita com um valor depois de um `=`, barra a busca.
- As opções vêm antes das palavras soltas. A busca com uma opção depois de uma palavra solta
  é barrada: há comando que a lê como opção e comando que a lê como arquivo.
- Os padrões são o valor de cada opção de padrão. Quando não há nenhuma, o padrão é a
  primeira palavra solta.
- Os arquivos são as outras palavras soltas. Solta é a palavra que não é opção nem valor de
  opção, e toda palavra depois de `--`.

### O que ele não vê

A busca feita por um comando que a configuração não lista como comando de busca, e o que a
[leitura-do-terminal](../../central/leitura-do-terminal/README.md) não vê numa linha.

### A configuração

O molde está em `esquemas/busca-por-palavra.schema.json`.

| Chave | O que é |
| --- | --- |
| `padroes_livres` | os padrões que uma busca pode ter |
| `buscas` | cada comando de busca do terminal: o `comando`, de uma ou mais palavras; as `opcoes_do_padrao`, que trazem um padrão; as `opcoes_de_arquivo`, que tiram os padrões de um arquivo; as `opcoes_com_valor`, as outras que levam um valor; e as `opcoes_sem_valor`, as que não levam nenhum |

### O que ele usa da folha do protocolo

O momento, o modelo `nega` e as ferramentas de terminal e de busca, com o campo do comando e
o do padrão. Para a busca exata, também a pasta de onde o uso roda.

### O que dá erro

Falta o texto do motivo, a configuração do terminal ou a lista; um arquivo não segue o seu
molde; uma opção aparece mais de uma vez nas listas de um comando de busca; o momento não é o
de antes de um uso; a ferramenta não é de terminal nem de busca; e, com `--exatas`, o arquivo não
existe ou a forma não é uma expressão regular. Nesses casos, o vigia escreve o erro na saída
de erro e sai com erro, sem responder nada.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
