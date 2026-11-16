# destino-da-limpeza

O vigia que leva para o documento de registro o texto que sai da memória e guarda o registro
para que nada nele mude.

## Para que serve

Alguns projetos têm memórias que a IA vai guardando entre sessões. Quando algo nelas é
concluído, uma limpeza tira esse texto da memória, e ele vai para um documento de registro.
Assim a memória de trabalho fica em dia, a próxima sessão sabe como seguir, e o que foi feito
fica guardado.

O registro é como um diário: o que está escrito nele não pode mudar nem sumir, e o que entra
nele tem de ser o que saiu da memória, sem nada inventado. Por isso quem escreve no registro
é este vigia, e não a IA. A limpeza só tira o texto da memória; no fim da resposta, o vigia
acha o que saiu e o escreve no registro, igual.

Exemplo: a IA tira da memória a linha de uma tarefa que terminou. No fim da resposta, a mesma
linha aparece no fim do registro. Se a IA tentar escrever no registro, o vigia não deixa.

## Como funciona

O programa da IA consulta o vigia antes de cada escrita em arquivo e de cada comando no
terminal, e no fim de cada resposta. A cada consulta, o vigia deixa a IA seguir ou a barra,
isto é, não deixa.

Os arquivos da memória são as origens, e o documento de registro é o destino. O vigia guarda,
numa pasta só dele, a pasta das anotações, duas coisas:

- **uma cópia das origens**, como estavam da última vez que ele escreveu no destino;
- **a impressão digital do destino**: um código curto calculado do texto inteiro dele. Cada
  texto dá um código, e se uma letra muda, o código sai outro. Funciona como um lacre.

Na primeira vez, sem nada guardado, ele só faz a cópia e o lacre, do jeito que as origens e o
destino estão.

- **A cada consulta, antes de tudo:** ele confere que a IA não consegue mudar o destino nem a
  pasta das anotações (ver "A proteção que ele exige") e confere o lacre do destino. Se a IA
  consegue mudá-los, ou se o lacre não bate, ele barra toda escrita e todo comando e não
  escreve no destino. O lacre que não bate quer dizer que o destino mudou por um caminho que o
  vigia não viu.
- **Antes de escrever no destino ou na pasta das anotações:** a escrita da IA é barrada. Só o
  vigia escreve neles.
- **Antes de um comando no terminal:** o comando que traz o nome do destino ou da pasta das
  anotações é barrado.
- **No fim da resposta:** ele compara as origens com a cópia. O texto que saiu delas vai para
  o fim do destino, do jeito que estava, como um bloco novo (um trecho separado do resto por
  uma linha em branco). Depois, ele atualiza a cópia e o lacre.

O que conta como texto que saiu:

- **o texto apagado**;
- **a versão antiga do texto mudado**, porque nada some da memória sem deixar rastro;
- e não conta **o texto que só trocou de lugar** dentro das origens, porque continua nelas.

Como ele compara os arquivos, e não as ações da IA, conta o texto que sai por qualquer
caminho: pela ferramenta de editar, por um comando ou por um programa que a IA roda. Se a
resposta para antes
do fim, a cópia continua a antiga, e o texto vai para o destino no fim da resposta seguinte.

Quando o lacre não bate, o texto que sai da memória espera na comparação. Para destravar, uma
pessoa olha o destino: se a mudança foi errada, põe o destino de volta como estava, e o lacre
volta a bater; se foi de propósito, apaga o lacre guardado, e o vigia faz um novo, do destino
como está.

Ele não lê o sentido do texto: não sabe se o que saiu foi concluído ou só mudou, e leva os
dois.

## A proteção que ele exige

O vigia só vê o que o programa da IA lhe mostra a cada consulta: o caminho de uma escrita, o
texto de um comando. Um comando pode chegar a um arquivo sem trazer o nome dele, e um
programa que a IA roda faz o que o vigia não vê. Assim, sozinho, ele não impede que a IA mude o destino ou a pasta
das anotações: o lacre mostra a mudança no destino depois, e, sem a pasta, ele perde a cópia
e o lacre e começa de novo com o que encontrar.

Por isso o destino e a pasta das anotações têm de ficar protegidos pelo próprio computador,
de um jeito que só o vigia consiga mudá-los, e a IA não, por nenhum caminho. O vigia não
monta essa proteção: o projeto a monta, ao ligá-lo. Mas ele a confere a cada consulta, com a
peça [conferencia-de-protecao](../../central/conferencia-de-protecao/README.md) da central, e
barra tudo enquanto ela não estiver montada.

## Como ligar num projeto

O projeto monta a proteção (ver "A proteção que ele exige") e configura o programa para
chamar este vigia antes de cada uso das ferramentas que escrevem arquivo e da de terminal, e
no fim de cada resposta, com este comando:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/destino_da_limpeza.py \
        --config <configuração> --protocolo <protocolo> --destino <arquivo> \
        --origem <arquivo ou pasta> --aviso-escrita <texto> --aviso-terminal <texto> \
        --aviso-lacre <texto> --aviso-protecao <texto>

Cada chamada cuida de um destino. O projeto com mais de um registro chama o vigia uma vez
para cada um, cada qual com as suas origens e a sua configuração.

Nas pastas de dados dele ficam: a configuração, a folha do protocolo, os quatro textos de
aviso, o destino, as origens e a pasta das anotações.

## Detalhes

### As opções

- `--destino`: o documento de registro; vem uma vez só.
- `--origem`: um arquivo, ou uma pasta com tudo o que há dentro dela, de onde a limpeza tira
  texto; pode vir mais de uma vez. O destino não conta como origem, mesmo dentro de uma pasta
  de origem.
- `--aviso-escrita`: o texto do bloqueio quando a IA tenta escrever no destino ou na pasta das
  anotações.
- `--aviso-terminal`: o texto do bloqueio quando um comando traz o nome do destino ou da pasta
  das anotações.
- `--aviso-lacre`: o texto do bloqueio quando o lacre do destino não bate.
- `--aviso-protecao`: o texto do bloqueio quando a IA consegue mudar o destino ou a pasta das
  anotações.

### A configuração

O molde está em `esquemas/destino-da-limpeza.schema.json`.

| Chave | O que é |
| --- | --- |
| `estado` | a pasta das anotações: a cópia das origens e a impressão digital do destino |

### Como ele acha o texto que saiu

Para cada origem, ele compara a cópia com o arquivo de agora, linha a linha, e junta as
linhas seguidas que saíram num trecho. O trecho que aparece inteiro, na mesma ordem, em alguma
origem de agora só trocou de lugar e fica fora. Os outros vão para o destino, cada um como um
bloco, na ordem dos caminhos das origens e, dentro de cada uma, na ordem em que estavam. Uma
origem que some inteira conta como todo o texto dela saído.

### Mais de uma sessão ao mesmo tempo

A comparação, a escrita no destino e a atualização da cópia e do lacre se fazem com a pasta
das anotações trancada, para que duas sessões não escrevam o mesmo texto duas vezes.

### O que ele usa da folha do protocolo

O momento, o modelo `nega`, a ferramenta de terminal, com o campo do comando, e as
ferramentas que escrevem arquivo, com o campo do caminho.

### O que dá erro

Quando algo dá errado ao conferir (a configuração fora do molde, um texto de aviso que não se
lê, um formulário que não se lê, uma origem ou o destino que não se leem), o vigia barra a
escrita ou o comando, com o erro no motivo. No fim da resposta, o erro deixa a cópia e o lacre
como estavam, e o texto que saiu espera a próxima comparação. Com a folha do protocolo que não
se lê, não há como responder, e o vigia só sai com o erro.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
