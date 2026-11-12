# destino-da-limpeza

O vigia que protege o documento de registro da limpeza.

## Para que serve

Alguns projetos têm memórias que a IA vai guardando entre sessões. Quando algo nelas é
concluído, uma limpeza tira esse texto da memória e o leva para um documento de registro.
Assim a memória de trabalho fica em dia, e a próxima sessão sabe como seguir.

Este vigia cuida do documento de registro: nada do que já está nele pode mudar ou sumir, e
só entra coisa nova quando, na mesma resposta, algo saiu da memória. Ele não chama a
limpeza; só vigia o registro.

## Como funciona

Os arquivos da memória são as origens, e o documento de registro é o destino.

- **Antes de escrever numa origem:** a escrita que tira ou muda texto fica anotada para a
  sessão. A origem nunca é barrada.
- **Antes de escrever no destino:** só passa a escrita que acrescenta texto novo entre os
  blocos (separado deles por uma linha em branco), e só depois de sair texto de uma origem
  na mesma resposta. A escrita que não muda nada também passa.
- **Antes de um comando no terminal:** o comando que traz o nome do destino é barrado.
- **No fim da resposta:** a anotação some, e a resposta seguinte começa sem nada saído.

Ele não lê o sentido do texto: garante quando o destino recebe texto e que o que ele já tem
fica como está, não que o texto novo seja o que saiu da memória.

## Como ligar num projeto

O projeto configura o programa para chamar este vigia antes de cada uso das ferramentas que
escrevem arquivo e da de terminal, e no fim de cada resposta, com este comando:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/destino_da_limpeza.py \
        --config <configuração> --protocolo <protocolo> --destino <arquivo> \
        --origem <arquivo ou pasta> --aviso-muda <texto> --aviso-sem-origem <texto> \
        --aviso-terminal <texto>

Nas pastas de dados dele ficam: a configuração, a folha do protocolo, os três textos de
aviso, o destino e as origens.

## Detalhes

### As opções

- `--destino`: o documento de registro protegido; pode vir mais de uma vez.
- `--origem`: um arquivo, ou uma pasta com tudo o que há dentro dela, de onde a limpeza tira
  texto; pode vir mais de uma vez.
- `--aviso-muda`: o texto do bloqueio quando o destino não cresceu só entre os blocos.
- `--aviso-sem-origem`: o texto do bloqueio quando nada saiu de uma origem na mesma
  resposta.
- `--aviso-terminal`: o texto do bloqueio quando o terminal nomeou o destino.

### O que é barrado no destino

A escrita que muda ou tira uma linha, a que gruda texto num bloco ou o põe no meio dele, a
que chega sem nada saído de uma origem e a da ferramenta que o vigia não sabe ler. Ele só lê
o destino e as origens; quem escreve é a ferramenta.

### A configuração

O molde está em `esquemas/destino-da-limpeza.schema.json`.

| Chave | O que é |
| --- | --- |
| `estado` | a pasta das anotações, que guardam, para cada sessão, se já saiu texto de uma origem na resposta |

### O que ele usa da folha do protocolo

O momento, o modelo `nega`, a ferramenta de terminal, com o campo do comando, e as escritas:
os campos do caminho, as ferramentas que trocam um trecho e as que gravam o arquivo inteiro.

### O que dá erro

Quando algo dá errado ao conferir (a configuração fora do molde, um texto de aviso que não
se lê, um formulário que não se lê), a escrita ou o comando que nomeia o destino é barrado,
com o erro no motivo, e o resto sai com o erro. Com a folha do protocolo que não se lê, não
há como responder, e o vigia só sai com o erro.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
