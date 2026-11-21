# testes

Os testes da peça [texto-de-comando](../README.md).

## Para que serve

O teste confere se a peça faz o que o README dela diz: entrega o que o comando escreveu, lido
em UTF-8 e com as quebras de linha iguais; diz quando o comando não passou; e dá erro quando o
comando não roda ou escreve o que não se lê. A lista de estragos confere o próprio teste: são
cópias da peça quebradas de propósito, uma regra por vez, e o teste tem de falhar em cada uma.

Por exemplo: numa cópia da peça, as quebras de linha passam a vir como estão. O teste tem de
falhar nessa cópia, porque um texto escrito com quebras de mais de um jeito deixa de chegar com
todas iguais.

## Como funciona

1. O teste sorteia textos com letras de fora do ASCII e quebras de linha de cada jeito, com uma
   semente fixa, para sair sempre igual.
2. Ele roda comandos que escrevem esses textos e acabam com o código 0 ou com outro, e confere
   o que a peça entrega.
3. Ele confere os erros: o comando sem nenhuma palavra, o programa que não existe e o que se
   escreve e não se lê em UTF-8.
4. Ele confere que o comando roda a partir da pasta pedida, sem nada pela entrada padrão e solto
   do terminal.
5. Ele termina com o código de saída: 0 quando tudo confere, 1 quando acha um erro na peça e 2
   quando o próprio teste quebra.

## Como ligar num projeto

Para rodar, o teste precisa do Python 3, num sistema em que um programa pode começar uma sessão
própria, solto do terminal. O comando:

    python3 -I <central>/roda/roda.py <central>/texto-de-comando/testes/teste_texto_de_comando.py <pasta da peça> <pasta de gravação>

`<central>` é a pasta central da prateleira; `<pasta da peça>`, a pasta da peça testada; e
`<pasta de gravação>`, uma pasta vazia, onde o teste cria a pasta de onde um comando roda.

A prova das cópias estragadas se faz pelo pedido `prova` da central (ver
[copias-estragadas](../../copias-estragadas/README.md)), com a lista `estragos.json` desta
pasta e o comando acima, sem as duas pastas do fim, que a prova põe.

## Detalhes

### Os arquivos

| Arquivo | O que é |
| --- | --- |
| `teste_texto_de_comando.py` | o teste |
| `estragos.json` | a lista de estragos, no molde da [copias-estragadas](../../copias-estragadas/README.md#a-lista-de-estragos) |

### Como o teste roda a peça

O teste carrega o arquivo de código da peça da pasta que recebe e faz os pedidos a ela por
dentro. Os comandos que ele pede são do próprio Python que roda o teste. Para conferir que o
comando não recebe nada pela entrada padrão, o teste troca a entrada padrão dele mesmo por uma
que tem dados, só durante esse pedido.

### O que dá erro

O teste termina com 1 quando a peça não faz o que o README dela diz: uma resposta errada, um
erro que falta ou a peça que quebra com outro erro. Ele mostra cada caso que não confere e
quantos foram. Quando o próprio teste quebra, ele termina com 2.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../../LICENSE-CONTENT.txt).*
