# roda

A peça da central que roda uma peça com a central à mão.

## Para que serve

Uma peça da prateleira usa mecanismos da central, e a central pode estar em qualquer pasta.
Para a peça usar a central sem saber onde ela está, o comando chama primeiro o `roda.py`, e
é ele que roda a peça. Como o caminho do `roda.py` vem no comando, é o comando que diz onde
a central está.

Por exemplo: uma peça usa o leitor de arquivos de texto da central. No código dela, basta
pedir o leitor pelo nome; quem o acha é o `roda.py`.

## Como funciona

- O comando chama o `roda.py` e, logo depois, dá o arquivo de código da peça e as opções
  dela.
- O `roda.py` olha as pastas da central, que são as vizinhas da pasta dele, e guarda onde
  está o arquivo de código de cada uma.
- Ele roda o código da peça, com as opções dela.
- Quando o código da peça pede uma peça da central pelo nome, o `roda.py` entrega.

## Como ligar num projeto

O comando de toda peça que usa a central começa assim:

    python3 -I <pasta da central>/roda/roda.py <arquivo de código da peça> <opções da peça>

O README de cada peça traz o comando dela inteiro.

## Detalhes

### Como ele acha as peças da central

Em cada pasta da central, vale o arquivo de código que tem o nome da pasta, como diz a
[estrutura das peças](../../ESTRUTURA-DAS-PECAS.md#os-nomes). É por esse nome que o código
de uma peça pede uma peça da central: a da pasta `leitura-de-texto` se pede como
`leitura_de_texto`. A pasta que tem esse arquivo já faz parte da central.

### O que a peça recebe

O código da peça roda como se o comando o chamasse direto: recebe as opções dela, lê a
entrada padrão e escreve na saída padrão, e o código de saída do comando é o dela.

### O que dá erro

O `roda.py` escreve o erro na saída de erro e sai com o código 1, antes de rodar a peça,
quando: falta o arquivo de código da peça no comando; ele não é um arquivo; ou uma peça da
central tem o nome de algo que já vem com o Python.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
