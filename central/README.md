# central

A pasta dos mecanismos que mais de uma peça da prateleira usa.

Quando duas peças precisam de um mesmo mecanismo, como o que lê um arquivo de dados, esse
mecanismo fica aqui. As peças da central existem para as outras peças, que as usam por
dentro.

## As peças

- [roda](roda/README.md): o que roda uma peça com a central à mão.
- [erro-de-dados](erro-de-dados/README.md): o erro que diz o que está errado e onde.
- [leitura-de-texto](leitura-de-texto/README.md): o leitor dos arquivos de texto.
- [leitura-de-json](leitura-de-json/README.md): o leitor dos dados em JSON.
- [conferencia-de-molde](conferencia-de-molde/README.md): o conferidor dos dados contra o
  molde deles.
- [expressao-regular](expressao-regular/README.md): o preparador das expressões regulares.
- [repetidos](repetidos/README.md): o que acha os valores repetidos de uma lista.
- [modelo-de-texto](modelo-de-texto/README.md): o que preenche um texto com lugares
  marcados.
- [protocolo](protocolo/README.md): o leitor da folha do protocolo.
- [protocolo-temporario](protocolo-temporario/README.md): a cópia temporária do protocolo,
  com o que a folha dele ainda não diz.
- [leitura-do-terminal](leitura-do-terminal/README.md): o leitor das linhas do terminal.
- [leitura-do-terminal-temporaria](leitura-do-terminal-temporaria/README.md): a cópia
  temporária da leitura do terminal, com as listas de quem escreve num arquivo ou roda código.
- [copias-estragadas](copias-estragadas/README.md): o que prova que o teste de uma peça pega
  os defeitos dela.
- [resultado-de-comando](resultado-de-comando/README.md): o que roda um comando e diz como
  ele acabou.
- [tipo-de-json](tipo-de-json/README.md): o que diz se um valor é de um tipo do JSON.
- [conferencia-de-protecao](conferencia-de-protecao/README.md): o que confere se o computador
  está impedindo a IA de alterar os arquivos das peças que ficam de olho nela.
- [caminho-escrito](caminho-escrito/README.md): o que dá, inteiro, o caminho que um arquivo de
  dados escreve.
- [caminhos-cobertos](caminhos-cobertos/README.md): o que dá os caminhos que um caminho cobre.
- [texto-de-comando](texto-de-comando/README.md): o que roda um comando e entrega, como texto, o
  que ele escreveu.
- [repositorio-git](repositorio-git/README.md): o que diz se uma pasta fica num repositório git.
- [rodape-de-documento](rodape-de-documento/README.md): o que monta, põe, acha e tira o rodapé de
  um documento.

O [dicionário](DICIONARIO.md) é o índice de tudo o que a central dá: cada nome, em poucas
palavras, com o link para o README que o explica. Antes de escrever algo numa peça,
consulta-se o dicionário: o que já existe se usa daqui.

## O que vale para todas

- Cada uma faz um serviço só e fica separada das outras: quem a usa puxa só o que precisa.
- Cada uma serve a qualquer peça e a qualquer projeto.
- Cada uma é escrita em Python e só usa o que já vem com o Python e as outras peças da
  central.
- Tudo o que uma peça da central dá se explica no README dela e tem a sua linha no
  dicionário.
- A parte "O que ela dá", no README de cada peça, é para quem escreve o código de outra
  peça, que faz pedidos a ela: diz, de cada pedido, o que ele tem de dizer e o que vem na
  resposta.
- O caminho da central chega pelo comando da peça que a usa, que começa pelo `roda.py` (ver
  [roda](roda/README.md)).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
