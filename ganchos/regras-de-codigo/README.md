# regras-de-codigo

O vigia que cobra da IA as regras de código do projeto.

## Para que serve

O projeto tem regras para o código, escritas em textos dele. Este vigia entrega essas regras
à IA antes de ela escrever código e, no fim, não a deixa terminar sem conferir o que
escreveu contra elas.

## Como funciona

Uma tarefa vai da primeira escrita de código ou de dados até a conferência no fim da
resposta.

- **Antes de escrever um arquivo de código ou de dados:** na primeira escrita da tarefa, o
  vigia entrega à IA os textos das regras. Depois, anota cada arquivo escrito.
- **Antes de um comando no terminal:** barra o comando que escreve num arquivo, o que roda
  código escrito ali mesmo e o que não dá para ler.
- **No fim da resposta:** se a tarefa escreveu código ou dados, o vigia não deixa a resposta
  terminar e pede à IA que confira cada arquivo contra as regras. Quando ela volta da
  conferência, ele deixa terminar, e a tarefa seguinte começa do zero.

Os formatos que o projeto deixa de fora não recebem as regras nem a conferência. O arquivo
sem extensão (o fim do nome, depois do ponto), ou de uma extensão que o projeto não cita,
recebe.

## Como ligar num projeto

O projeto configura o programa para chamar este vigia antes de cada uso das ferramentas que
escrevem arquivo e da de terminal, e no fim de cada resposta, sempre com o mesmo comando:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/regras_de_codigo.py \
        --config <configuração> --terminal <configuração do terminal> \
        --protocolo <protocolo> --regras <texto> --fim <texto> --bloqueio <texto>

Nas pastas de dados dele ficam: a configuração, a configuração do terminal, a folha do
protocolo, os textos das regras, o pedido de conferência e o aviso do bloqueio.

## Detalhes

### As opções

- `--regras`: um texto de regras. Pode vir mais de uma vez; os textos são entregues na
  ordem dada.
- `--fim`: o pedido de conferência, que vem depois das regras e antes da lista dos
  arquivos.
- `--bloqueio`: o aviso do bloqueio no terminal, que vem antes da parte do comando que o
  causou.

### O que é barrado no terminal

- O comando que escreve num arquivo: o que manda a saída para um arquivo com `>`, o que a
  configuração diz que sempre escreve e o que tem uma opção que, pela configuração, o faz
  escrever.
- O comando que roda código escrito ali mesmo: o que traz um texto embutido com `<<`, o que
  tem uma opção que, pela configuração, o faz rodar código e o programa que, pela
  configuração, lê código do terminal quando é chamado sem arquivo.
- O comando que não se lê, como um com aspa sem fechar.

Entre aspas, `>` e `<<` são texto e passam. O que está dentro de `$( )` e de crases também é
lido.

### A configuração

O molde está em `esquemas/regras-de-codigo.schema.json`.

| Chave | O que é |
| --- | --- |
| `estado` | a pasta das anotações, que guardam os arquivos escritos na tarefa e se apagam ao fim dela |
| `sem_conferencia` | os formatos, pela extensão, que ficam de fora das regras e da conferência; maiúscula e minúscula contam igual |
| `terminal.destinos_livres` | os destinos para onde escrever não conta como escrita |
| `terminal.sempre_escrevem` | os comandos que sempre escrevem num arquivo |
| `terminal.escrevem_com_opcao` | para cada comando, as opções que o fazem escrever ou rodar código escrito no comando |
| `terminal.leem_codigo_sem_arquivo` | os programas que, chamados sem arquivo, leem código do próprio terminal |

### O que ele usa da folha do protocolo

O momento; os modelos `contexto` (com as regras), `nega` (com o bloqueio) e `trava` (no
fim); a ferramenta de terminal, com o campo do comando; e os campos do caminho do arquivo
escrito.

### O que dá erro

Falta um dos textos ou a configuração do terminal; um arquivo não segue o seu molde; o
momento não é conhecido; a sessão não tem identificação; a ferramenta de escrita não traz um
campo de caminho que a folha conhece.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
