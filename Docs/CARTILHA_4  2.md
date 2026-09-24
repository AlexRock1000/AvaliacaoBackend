# Cartilha 4 · Traço Fino, estúdio de tatuagem

**Esta cartilha foi sorteada para dois alunos.** Vocês receberam o mesmo problema e vão entregar
soluções diferentes. Não combinem marca, paleta, telas nem nomes de rota. Na apresentação, cada
um explica as escolhas que fez e por que não fez as do colega.

## O negócio

Um estúdio de tatuagem pequeno, com dois tatuadores. Toda tatuagem passa por etapas: o desenho
precisa ser aprovado, depois vêm uma ou mais sessões e, quando a pele cicatriza, o retoque. Hoje
tudo isso se perde em conversas de mensagem, e ninguém sabe em que etapa está cada cliente.

## Perfil A · Bruna, a cliente. Usa no celular.

Bruna tem 27 anos, é designer e vai fazer a primeira tatuagem grande. Quer descrever a ideia pelo
celular e acompanhar cada etapa, sabendo sempre o que vem depois.

O que ela faz:

1. Pede uma tatuagem, com a ideia, o local do corpo e o tamanho.
2. Vê as tatuagens dela e a etapa de cada uma.
3. Abre uma tatuagem e lê o histórico: desenho, sessões e retoque.

## Perfil B · Vitor, o tatuador. Usa no computador.

Vitor tatua e organiza a própria agenda. Entre uma sessão e outra, precisa registrar o que foi
feito e ver de relance quais tatuagens estão esperando o próximo passo.

O que ele faz:

1. Vê as tatuagens, filtradas por etapa.
2. Abre uma tatuagem e registra um passo: o desenho aprovado, uma sessão ou o retoque.
3. Confere que a etapa da tatuagem mudou.

## As três entidades

- **O usuário.** Quem entra no sistema. Tem um tipo: cliente ou tatuador.
- **A tatuagem.** Pertence a um cliente. Guarda a ideia, o local do corpo, o tamanho e a etapa.
- **O passo.** Pertence a uma tatuagem. Guarda o tipo, a data e uma observação.

## As quatro telas

Da pessoa, pensadas para o celular:

1. **Pedir tatuagem.** O formulário em que a Bruna descreve a ideia.
2. **Minhas tatuagens.** As tatuagens dela, com a etapa, e o histórico de cada uma.

Da gestão, pensadas para o computador:

3. **A agenda.** Todas as tatuagens, com o filtro por etapa.
4. **A ficha.** O formulário que registra um passo numa tatuagem.

Todas as telas funcionam nos dois tamanhos. O aparelho de cada perfil diz onde a tela precisa
estar impecável.

## O que o back precisa oferecer

1. Listar as tatuagens, com filtro por etapa e por cliente.
2. Mostrar uma tatuagem.
3. Pedir uma tatuagem nova.
4. Listar os passos de uma tatuagem.
5. Registrar um passo numa tatuagem, aplicando a regra abaixo.

Os caminhos, os métodos, os nomes e os status são decisão sua. A régua é o REST da aula 2, e na
apresentação você defende cada escolha.

## A regra que o serviço cuida

A tatuagem nova começa como **pedida**. Os passos seguem uma ordem: primeiro o desenho aprovado,
depois uma ou mais sessões, e por fim o retoque, que só acontece depois da cicatrização. O serviço
recusa sessão antes do desenho aprovado, e retoque antes de pelo menos uma sessão. Cada passo aceito
muda a etapa: desenho aprovado leva a **desenho aprovado**, sessão leva a **em sessões** e retoque
leva a **finalizada**.

## Antes do login

Enquanto o login não chega, o front deixa escolher o perfil numa lista, sem senha. A tela da
pessoa pede ao back só o que é dela, informando quem ela é na própria requisição.

## O que não faz parte

Orçamento, sinal, pagamento, portfólio com fotos e aviso por mensagem.

## O que vem depois

No ciclo 2 esses dados saem da memória e vão para o MySQL. No ciclo 4 o usuário ganha senha, e
Bruna passa a ver só as tatuagens dela, porque o back confere quem está pedindo. No ciclo 5
entra um trecho de IA. A cartilha foi desenhada para aguentar as três coisas: não troque de ideia
no meio do caminho.
