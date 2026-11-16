# ganchos

Vigias que o programa onde a IA trabalha consulta antes de deixar a IA agir, e o ajuste que
impede a IA de alterar os arquivos deles.

Para fazer as coisas, a IA usa ferramentas: ler um arquivo, escrever um arquivo, rodar um
comando no terminal, procurar uma palavra. Em certos momentos (antes de a IA usar uma
ferramenta, depois de um grupo de usos e no fim de cada resposta dela), o programa chama
sozinho os vigias desta pasta e espera o que cada um diz: "pode"; "não pode", com o motivo;
ou "antes, leia isto". Esses vigias são os ganchos.

## As peças

- [regras-de-codigo](regras-de-codigo/README.md): o vigia das regras de código.
- [busca-por-palavra](busca-por-palavra/README.md): o vigia da busca.
- [leitura-completa](leitura-completa/README.md): o vigia da leitura.
- [destino-da-limpeza](destino-da-limpeza/README.md): o vigia do registro da limpeza.
- [chamadas-permitidas](chamadas-permitidas/README.md): a cancela e o registro.
- [ajuste-de-protecao](ajuste-de-protecao/README.md): o ajuste que protege os vigias.

## O que vale para todas

- Cada uma é escrita em Python e só usa o que já vem com o Python e as peças da
  [central](../central/README.md).
- O próprio programa se configura para chamar os vigias: ali se diz quais vigias rodam e em
  que momentos. Se o programa consegue barrar um uso também quando um vigia falha ou nem
  chega a rodar, vale ligar essa opção: ela fecha o último buraco.
- O comando que chama um vigia começa pelo `roda.py` da central (ver
  [roda](../central/roda/README.md)).
- O que é do projeto chega pelo comando que chama o vigia: a configuração dele, na opção
  `--config`; a folha do protocolo (ver [protocolo](../central/protocolo/README.md)), na
  opção `--protocolo`; e os textos que ele mostra.
- O vigia que lê uma linha do terminal usa a
  [leitura-do-terminal](../central/leitura-do-terminal/README.md), com a configuração dela
  na opção `--terminal`. Quando o projeto liga a cancela de
  [chamadas-permitidas](chamadas-permitidas/README.md), ela já barra todo comando que não
  está liberado, e essa leitura vira proteção dobrada: cada vigia funciona sozinho, também
  sem a cancela.
- Toda configuração tem a chave `versao_schema`, com a versão do molde, e o molde fica na
  pasta `esquemas` da peça. A configuração que não segue o molde dá erro, que diz o arquivo
  e o lugar do valor errado.
- O vigia que guarda o que acontece numa sessão anota numa pasta que a configuração dá, na
  chave `estado`, com o caminho a partir da pasta da configuração.
- O vigia que grava um arquivo que outro uso pode estar gravando ao mesmo tempo tranca o
  arquivo antes de gravar, e por isso precisa de um sistema que tranca arquivos.
- Na dúvida, o vigia barra: barrar a mais pode, barrar a menos não.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
