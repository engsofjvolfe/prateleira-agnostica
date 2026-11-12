# A estrutura das peças

Toda peça da prateleira é uma pasta com a mesma estrutura. Assim, quem abre uma peça já sabe
onde está cada coisa. A estrutura só muda quando uma peça precisa de algo que ela não cobre,
e aí muda aqui, para todas.

## O que a pasta de uma peça tem

| O quê | O que é |
| --- | --- |
| `README.md` | o documento da peça, no [formato dos README](FORMATO-DOS-README.md) |
| o arquivo de código | o código da peça, em Python |
| `esquemas/` | os moldes: os arquivos que dizem a forma dos dados que a peça lê |
| `testes/` | os testes da peça, com o README deles |

A pasta `esquemas` existe na peça que lê arquivos de dados.

O que é de um projeto, como a configuração e os textos que a peça mostra, fica nas pastas de
dados dele e chega à peça pelo comando.

## Os nomes

- **A pasta:** o nome da peça, em letras minúsculas e sem acento, com as palavras separadas
  por `-`.
- **O arquivo de código:** o nome da pasta, com `_` no lugar de `-` e `.py` no fim. O traço
  muda porque o Python lê o `-` como o sinal de menos e não o aceita no nome de um arquivo
  de código que outro código usa. Assim, a pasta `uma-peca` guarda o `uma_peca.py`.
- **O molde:** o nome termina em `.schema.json`. O molde da configuração da peça tem o nome
  da pasta: na pasta `uma-peca`, é o `esquemas/uma-peca.schema.json`.

## A peça com mais de um arquivo de código

Quando o código de uma peça se divide em mais de um arquivo, o README dela traz, em
"Detalhes", o nome de cada arquivo e o que ele faz.

## As pastas que juntam peças

Uma pasta pode juntar peças que trabalham no mesmo assunto. Ela tem o README do grupo, e
cada peça é uma pasta dentro dela, com a estrutura acima.

A [central](central/README.md) é a pasta que junta os mecanismos que mais de uma peça usa.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt).*
