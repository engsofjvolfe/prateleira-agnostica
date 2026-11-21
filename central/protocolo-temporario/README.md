# protocolo-temporario

A cópia temporária do [protocolo](../protocolo/README.md), com o que a folha dele ainda não diz.

## Para que serve

O protocolo lê a folha que diz os nomes que o programa onde a IA trabalha usa. Um vigia
pode precisar de três coisas que essa folha ainda não traz: o momento em que a pessoa manda
uma mensagem na conversa, com o texto dela; o momento de depois de um uso de uma ferramenta;
e o modelo do aviso, a resposta que deixa a resposta da IA terminar e mostra um texto.

Mudar o protocolo agora poderia quebrar as peças que já o usam. Por isso, esta cópia traz o
protocolo com essas três coisas a mais, e o protocolo fica como está.

Por exemplo: um vigia precisa saber quando a pessoa dá um ok na conversa. Com esta cópia, a
folha diz o nome que o programa dá a esse momento e ao campo do texto, e o vigia recebe o
texto da pessoa.

## Como funciona

Tudo o que o [protocolo](../protocolo/README.md#como-funciona) faz, esta cópia faz igual. A
mais, o formulário, que é o que o programa entrega ao vigia a cada momento:

- pode ser do momento da mensagem da pessoa, e aí traz o texto dela;
- pode ser do momento de depois de um uso, e aí traz a ferramenta e o que a IA mandou para
  ela, como o do momento de antes do uso.

E o vigia pode responder com um aviso.

## A cópia temporária

Esta cópia é o jeito de mudar o protocolo sem quebrar ninguém, em três fases: o novo nasce ao
lado do antigo, sem mexer nele; quem usa o antigo passa para o novo; e o antigo sai. Quando os
testes existirem, as peças que usam o protocolo passam a usar esta cópia, ela toma o lugar e o
nome dele, e esta pasta sai.

## Como ligar num projeto

Enquanto esta cópia existe, o projeto guarda, nas pastas de dados dele, uma folha na forma
dela para o vigia que a usa, que a recebe na opção `--protocolo`. Essa folha não serve às
peças que usam o protocolo, que recusa as chaves que não conhece. Esta peça chega ao projeto
junto com a [central](../README.md), pelo vigia que a usa.

## Detalhes

### A folha

O molde está em `esquemas/protocolo-temporario.schema.json`. É o da
[folha do protocolo](../protocolo/README.md#a-folha-do-protocolo), com estas chaves a mais,
que podem faltar:

| Chave | O que é a mais |
| --- | --- |
| `eventos` | `depois`, o nome do momento de depois de um uso só, e `mensagem`, o do momento em que a pessoa manda uma mensagem |
| `chaves` | `mensagem`, o campo do formulário que traz o texto da pessoa |
| `respostas` | `aviso`, o modelo do que deixa a resposta terminar e mostra o texto do vigia |

O que dá erro na folha é o que dá erro na
[folha do protocolo](../protocolo/README.md#o-que-dá-erro-na-folha).

### O que ela dá

No código do vigia, esta peça se chama `protocolo_temporario`. Ela dá os mesmos pedidos do
[protocolo](../protocolo/README.md#o-que-ela-dá), com estas diferenças:

#### le_evento

O momento da resposta pode ser também `depois` ou `mensagem`. No momento `mensagem`, as
partes trazem também a `mensagem`, o texto da pessoa.

#### resposta

O `qual` pode ser também `aviso`. O pedido dá erro quando a folha não tem o modelo pedido.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
