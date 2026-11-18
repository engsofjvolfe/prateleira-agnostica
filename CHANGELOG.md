# Changelog

Todas as mudanças significativas da prateleira serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e a
prateleira segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não publicado]

## [0.10.0] - 2026-11-18

### Modificado

- O README e o código da peça ajuste-de-protecao, de ganchos, com o molde da configuração: cria o
  usuário da IA e o usuário do programa; os itens em que as peças escrevem ficam com o usuário do
  programa, e os outros com o administrador; abre as pastas de trabalho também para o usuário do
  programa; cria a permissão de o usuário do programa rodar comandos com o usuário da IA, com a
  regra que a configuração traz, conferida antes de valer e provada depois; e confere o ajuste com
  o usuário do programa.
- Os vigias leitura-completa, regras-de-codigo e busca-por-palavra, de ganchos, no README e no
  código: cada um recebe a lista e pede a conferência a cada consulta; o leitura-completa barra a
  escrita na pasta das anotações dele.
- O README de ganchos, com o que precisa estar feito no computador e a lista entre o que chega a
  cada vigia pelo comando.

## [0.9.0] - 2026-11-17

### Adicionado

- O código da peça ajuste-de-protecao, de ganchos, com o molde da configuração e a parte do
  Linux: antes de mudar qualquer coisa, ela confere se o computador está pronto; cria o usuário
  da IA e o dono dos itens; fecha os itens, a lista, a configuração, a pasta dela e a da central;
  abre o caminho até eles e as pastas de trabalho; monta o comando que abre a IA; e confere o
  ajuste com o usuário da IA. Com a prévia, só mostra o que faria.

### Modificado

- O README da peça ajuste-de-protecao: a pessoa roda a peça com a IA fechada; o usuário da IA lê
  o que se fecha; as pastas acima de um item contam também pelo lugar real; as pastas de trabalho
  se abrem com o usuário da pessoa, com o limite dos arquivos que já nascem fechados; o passo 8
  testa também a lista, a configuração, a peça e a central; a pasta que falta nasce fechada; duas
  conferências novas de antes do ajuste; os textos, os sistemas, os arquivos de código, o que dá
  erro e o código de saída.

## [0.8.0] - 2026-11-16

### Adicionado

- O README da peça ajuste-de-protecao, de ganchos, com a pesquisa: ela faz no computador o
  ajuste que impede a IA de alterar os arquivos das peças que ficam de olho nela, com um
  usuário só para a IA, e confere o ajuste no fim com a peça conferencia-de-protecao.

### Modificado

- O README de ganchos, com a peça nova.

## [0.6.0] - 2026-11-16

### Modificado

- O README da peça destino-da-limpeza, de ganchos, com o nome da peça da central que confere
  a proteção.

## [0.5.0] - 2026-11-15

### Modificado

- O README da peça destino-da-limpeza, de ganchos: o vigia escreve no registro o texto que
  sai da memória, e a IA não escreve nele; guarda a impressão digital do registro e barra
  tudo quando ela não bate; e confere, com a peça protecao-de-arquivos da central, que a IA
  não consegue mudar o registro nem a pasta das anotações.

## [0.4.0] - 2026-11-15

### Adicionado

- O código da peça leitura-completa, de ganchos, com o molde da configuração dela e o da
  anotação: o vigia só deixa passar a leitura que começa na primeira linha do arquivo ou na
  seguinte à última lida; barra as ferramentas que leem um arquivo de outro jeito, que são a
  de terminal, as de busca e as que entregam um resumo; não deixa escrever nem terminar a
  resposta com arquivo lido só em parte; e guarda a impressão digital do trecho lido, que faz
  o anotado de um arquivo deixar de valer quando esse trecho muda.

### Modificado

- O README da peça leitura-completa, com os outros jeitos de ler que o vigia barra, a
  impressão digital do trecho lido e a conta das linhas do arquivo.

## [0.3.0] - 2026-11-13

### Adicionado

- O código da peça regras-de-codigo, de ganchos, com o molde da configuração dela.

## [0.2.0] - 2026-11-12

### Modificado

- O README da peça regras-de-codigo, de ganchos: o vigia confere por fora da IA a leitura
  inteira de cada arquivo escrito, as conferências do projeto e o ok de uma pessoa.

## [0.1.0] - 2026-11-12

### Adicionado

- O README geral da prateleira.
- O formato dos README da prateleira, em `FORMATO-DOS-README.md`.
- A estrutura das peças da prateleira, em `ESTRUTURA-DAS-PECAS.md`.
- Os README de ganchos, nesse formato: o do grupo e os das peças regras-de-codigo,
  busca-por-palavra, leitura-completa, destino-da-limpeza e chamadas-permitidas.
- A peça busca-por-palavra, de ganchos.

[não publicado]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.6.0...v0.8.0
[0.6.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/engsofjvolfe/prateleira-agnostica/releases/tag/v0.1.0
