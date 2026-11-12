# O formato dos README

Todo README da prateleira segue o mesmo formato. Assim, quem nunca programou, mas sabe usar
uma IDE, entende qualquer peça do mesmo jeito. O formato só muda quando uma peça precisa de
algo que ele não cobre, e aí muda aqui, para todas.

## O README da raiz

O README da raiz é geral: diz o que a prateleira é e não cita detalhes das peças, que ficam
no README de cada uma. Ele tem:

1. **O título:** o nome do repositório.
2. **Os badges** das licenças.
3. **O que a prateleira é**, em poucas frases simples.
4. **Como usar:** em poucas frases, com o link para a estrutura das peças, para este formato
   e para o changelog.
5. **A licença:** cada parte com a sua licença, e o crédito ao reusar o conteúdo.
6. **A linha da licença.**

## O README de uma peça

1. **O título:** o nome da pasta da peça.
2. **Uma frase** que diz o que a peça é.
3. **Para que serve:** o problema e o que a peça faz, em poucas frases, com um exemplo.
4. **Como funciona:** o que acontece, passo a passo, em palavras simples.
5. **Como ligar num projeto:** o comando que roda a peça e os arquivos que o projeto guarda
   para ela nas pastas de dados dele.
6. **Detalhes:** para quem for mexer na peça. As opções do comando, a configuração chave por
   chave, o que dá erro e o que mais for preciso, cada assunto com o seu subtítulo.
7. **Testes:** onde estão.
8. **A linha da licença.**

Uma peça só ganha uma parte a mais quando precisa dela de verdade. A parte a mais entra
depois de "Como funciona", com um título que diz o que ela é.

## O README de uma peça da central

A [central](central/README.md) guarda os mecanismos que mais de uma peça usa. O README de
uma peça dela segue o de uma peça, e ainda:

- Em "Como ligar num projeto", diz como a peça chega ao projeto e, quando o projeto guarda
  um arquivo para ela, qual é.
- Em "Detalhes", a parte "O que ela dá" explica cada nome que a peça dá às outras, um por
  subtítulo: o que recebe, o que entrega e quando dá erro. É para esses subtítulos que o
  dicionário da central aponta.

## O README de um grupo de peças

Uma pasta que junta peças tem um README com:

1. **O título:** o nome da pasta.
2. **O que o grupo é**, em poucas frases simples.
3. **As peças:** o link do README de cada uma, com poucas palavras ao lado.
4. **O que vale para todas:** o que é comum às peças do grupo, dito uma vez só.
5. **A linha da licença.**

## Como se escreve

- Em "Para que serve" e "Como funciona", nenhum termo técnico aparece sem ser explicado ali
  mesmo. Os termos técnicos ficam em "Detalhes" e em "O que vale para todas".
- Cada ideia se explica no README que é dono dela. Quando a peça usa algo que está
  centralizado em outra parte, e só se for preciso, o README dela aponta para o README da
  parte centralizada.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt).*
