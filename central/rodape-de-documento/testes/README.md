# testes

Os testes da peça [rodape-de-documento](../README.md).

## Para que serve

O teste confere se a peça faz o que o README dela diz: monta cada rodapé com os links refeitos e
os campos trocados, põe cada um no lugar dele, acha e tira os que o documento tem, diz quais estão
fora do dia e dá erro em cada caso que o README lista.

Por exemplo: se a peça deixar de pôr a `/` do fim num link refeito para uma pasta, o teste falha,
porque o rodapé do documento deixa de ter o link escrito como o modelo o escreve.

## Como funciona

1. O teste sorteia projetos, com uma semente fixa, para sair sempre igual: os nomes das pastas e
   dos arquivos, os textos dos documentos e dos modelos, os textos que abrem e fecham um campo, o
   separador, a marca e o formato da data, tudo com letras de fora do ASCII.
2. Para cada documento, ele monta pela regra do README o texto que a peça deve entregar e confere
   cada pedido: o rodapé montado, o lugar dele, o que falta, o que sobra, o que está diferente e o
   que se separa.
3. Ele confere cada erro que o README lista, ao ler o arquivo dos rodapés e num documento.
4. Num repositório git de prova, com commits de datas sorteadas, ele confere a data da última
   mudança.
5. No fim, ele mostra cada caso que não confere e quantos foram.

## Como ligar num projeto

Para rodar, o teste precisa do Python 3 e do programa git. O comando:

    python3 -I <central>/roda/roda.py <central>/rodape-de-documento/testes/teste_rodape_de_documento.py <pasta da peça> <pasta de gravação>

`<central>` é a pasta central da prateleira; `<pasta da peça>`, a pasta da peça testada; e
`<pasta de gravação>`, uma pasta vazia, onde o teste grava os projetos sorteados. A pasta de
gravação fica fora de um repositório git, porque o teste confere o erro de quem pede a data da
última mudança fora de um repositório.

A prova deste teste se faz pela peça [copias-estragadas](../../copias-estragadas/README.md), da
central, com a lista `estragos.json` desta pasta e o comando acima.

## Detalhes

### Os arquivos

| Arquivo | O que é |
| --- | --- |
| `teste_rodape_de_documento.py` | o teste |
| `estragos.json` | a lista de estragos, no molde da [copias-estragadas](../../copias-estragadas/README.md#a-lista-de-estragos) |

### Como o teste roda a peça

O teste lê o arquivo de código da peça da pasta que recebe, e nunca o código que o Python já
preparou e guardou, e faz os pedidos a ela por dentro. Assim, um estrago que não muda o tamanho do
arquivo não passa despercebido. Cada caso grava numa pasta própria, dentro da pasta de gravação. A
pasta do caso que passa se apaga; fica só a do caso que falha, para quem quiser ver o que
aconteceu. O git de prova roda sem as configurações do computador, para os commits saírem sempre
do mesmo jeito.

### O que dá erro

O teste acha um erro na peça quando ela dá uma resposta errada, deixa de dar um erro que o README
pede ou quebra com outro erro. A pasta de gravação dentro de um repositório git faz o próprio teste
quebrar.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../../LICENSE-CONTENT.txt).*
