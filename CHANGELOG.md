# Changelog

Todas as mudanças significativas da prateleira serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e a
prateleira segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não publicado]

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

[não publicado]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/engsofjvolfe/prateleira-agnostica/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/engsofjvolfe/prateleira-agnostica/releases/tag/v0.1.0
