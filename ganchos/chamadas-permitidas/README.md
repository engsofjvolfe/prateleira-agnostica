# chamadas-permitidas

Dois vigias: a cancela, que só deixa a IA fazer o que a documentação do projeto permite, e o
registro, que anota tudo o que ela faz.

## Para que serve

A cancela trava tudo por padrão. A IA só pode usar uma ferramenta do jeito que uma regra do
projeto permite, e cada regra aponta o trecho da documentação do projeto que a autoriza. Se
o trecho some da documentação, a regra para de valer. A cancela também protege os arquivos
que a IA nunca pode mudar.

O registro anota num arquivo cada uso de ferramenta, antes de ele acontecer. Se não consegue
anotar, não deixa o uso acontecer.

## Como funciona

### A cancela

1. Primeiro, a proteção: o uso de qualquer ferramenta que escreve, também o de uma livre, é
   barrado quando cai num arquivo ou numa pasta protegida.
2. Depois, as ferramentas livres, que o projeto libera, passam sem regra.
3. Por fim, o resto só passa quando roda da pasta principal do projeto e é exatamente do
   jeito que uma regra que vale permite. A ferramenta que o projeto não cita, também a que
   ainda não existe, é barrada.

Por isso, um comando novo entra primeiro na documentação e depois na lista de regras.

### O registro

Cada uso, barrado ou não, vira uma linha no fim do registro, menos os das ferramentas que o
projeto deixa de fora. Dois usos ao mesmo tempo não misturam as linhas.

## O que a cancela não cobre

As ferramentas livres passam sem regra. Por isso, ler com elas um arquivo que a documentação
proíbe depende de a documentação ser seguida.

## Como ligar num projeto

O projeto configura o programa para chamar os dois antes de cada uso de ferramenta, seja
qual for, com estes comandos:

    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/cancela.py \
        --protocolo <protocolo> --config <configuração> --regras <lista> \
        --raiz <pasta principal> --barra-com <código>
    python3 -I <pasta da central>/roda/roda.py <pasta da peça>/registra.py \
        --protocolo <protocolo> --config <configuração> --registro <arquivo> \
        --barra-com <código>

Nas pastas de dados dele ficam: a configuração, a lista de regras, a folha do protocolo e o
registro.

## Detalhes

### Os arquivos da peça

| Arquivo | O que faz |
| --- | --- |
| `cancela.py` | a cancela |
| `registra.py` | o registro |
| `evento.py` | a configuração e o formulário, os mesmos para os dois vigias, e o jeito de barrar |
| `registro.py` | a forma do registro e a gravação de uma linha nele |
| `esquemas/` | os moldes da configuração, da lista de regras e das partes do formulário que os vigias usam |

### As opções

- `--regras`: a lista de regras do projeto.
- `--raiz`: a pasta principal do projeto.
- `--registro`: o arquivo do registro.
- `--barra-com`: o código de saída com que o programa não deixa o uso acontecer e mostra o
  motivo. Ele vem no comando, e não num arquivo, para valer também quando um arquivo está
  quebrado.

### Como eles barram

Os dois não respondem pelos modelos da folha do protocolo. O que deixa o uso acontecer fica
calado. O que o barra, ou que não consegue fazer o trabalho dele (a folha, a configuração, a
lista ou o formulário fora da forma, o registro que não se grava), escreve o motivo na saída
de erro e sai com o código de `--barra-com`.

### A configuração

O molde está em `esquemas/chamadas-permitidas.schema.json`.

| Chave | O que é |
| --- | --- |
| `fora_do_registro` | as ferramentas cujos usos não se gravam |
| `livres` | as ferramentas que a cancela deixa passar sem regra |
| `campos` | para cada outra ferramenta, o campo da entrada, um texto, que a forma de uma regra tem de bater inteira |
| `protegidos` | se houver: os caminhos, de arquivos ou de pastas, em que nenhum uso escreve, nem o de uma ferramenta livre; o caminho relativo parte da pasta principal |

Cada nome de ferramenta, campo ou caminho vem numa linha só, com algum caractere que não é
espaço.

A proteção não vale para as ferramentas de leitura. Os dois caminhos se comparam absolutos e
sem atalhos: o escrito a partir da pasta do uso, o protegido a partir da pasta principal. A
ferramenta livre passa antes de a lista ser lida: uma lista quebrada nunca barra a livre.

### A lista de regras

O molde está em `esquemas/regras.schema.json`, com as chaves `partes` e `regras`.

As `partes` são pedaços de forma com nome, para que um pedaço repetido fique num lugar só.
Cada nome, de letras minúsculas e `_`, dá uma expressão regular. A forma de uma regra usa a
parte como `<<nome>>`, e o nome que não é de uma parte dá erro.

Cada regra tem:

| Chave | O que é |
| --- | --- |
| `nome` | o nome dela, um só na lista |
| `ferramenta` | a ferramenta a que ela vale |
| `forma` | a expressão regular que o campo da entrada tem de bater inteiro, do começo ao fim |
| `fonte` | o `arquivo` da documentação que dá o uso e o `trecho` dele que o dá, letra por letra |
| `documentada` | se houver: o `arquivo` e o `texto` que tem de estar nele para o uso passar, montado com as partes que a forma nomeia, como `(?P<script>...)`, cada uma escrita como `{script}` |

A regra vale quando o trecho da fonte está no arquivo dela; a que perdeu o trecho não deixa
passar nada, e o motivo do bloqueio diz o nome dela. A `documentada` serve ao uso que a
documentação dá por um modelo: o uso passa só quando o texto montado está no arquivo dela.
Os caminhos relativos partem da pasta principal.

Como a forma bate com o comando inteiro, o comando que junta outro a ele só passa se a forma
deixar. Ela deixa de fora os sinais com que o terminal junta comandos (`;`, `|`, `&`), roda
um comando dentro de outro (`$`, a crase) ou manda a saída para um arquivo (`>`), e nunca
tem um trecho que aceite qualquer coisa, como `.*`.

### O registro

Um arquivo de texto com uma linha por uso gravado, na ordem dos usos. Cada linha é um objeto
JSON com exatamente as chaves `sessao` (a identificação da sessão), `ferramenta` (o nome
dela) e `entrada` (a entrada inteira, um objeto). A linha nunca se parte, porque o JSON
escreve a quebra de linha de um texto como escape, e cada linha termina com a quebra. O
registro que não existe nasce; a pasta dele tem de existir. Cada gravação tranca o arquivo.

### O que eles usam da folha do protocolo

O nome do momento de antes de um uso; os campos da sessão, da ferramenta, da entrada e da
pasta; os campos do caminho de um arquivo escrito; e as ferramentas de leitura.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
