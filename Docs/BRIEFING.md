# Briefing — Tinta Negra Tattoo Studio

## O negócio e o problema

O estúdio é pequeno e conta com dois tatuadores. Cada tatuagem passa pela aprovação do desenho, por uma ou mais sessões e, depois da cicatrização, pelo retoque.

Hoje, o andamento dos trabalhos fica perdido em conversas de mensagem.

Com isso, clientes e tatuadores não conseguem saber com facilidade em que etapa está cada tatuagem nem qual é o próximo passo.

## Para quem é o sistema

### Bruna — cliente

- **Contexto:** tem 27 anos, é designer e vai fazer sua primeira tatuagem grande.
- **O que precisa resolver:** descrever sua ideia e acompanhar as etapas, sabendo o que vem depois.
- **Onde usa o sistema:** celular.
- **Jornada:**
  1. Pede uma tatuagem informando a ideia, o local do corpo e o tamanho.
  2. Vê suas tatuagens e a etapa de cada uma.
  3. Abre uma tatuagem e consulta o histórico do desenho, das sessões e do retoque.

### Vitor — tatuador

- **Contexto:** trabalha no estúdio e organiza a própria agenda.
- **O que precisa resolver:** registrar o que foi feito e ver quais tatuagens estão esperando o próximo passo.
- **Onde usa o sistema:** computador.
- **Jornada:**
  1. Consulta as tatuagens e filtra a lista pela etapa.
  2. Abre uma tatuagem e registra o desenho aprovado, uma sessão ou o retoque.
  3. Confere que a etapa da tatuagem foi atualizada.

## O que o sistema oferece

- Pedir uma tatuagem.
- Consultar tatuagens e filtrar por etapa ou cliente.
- Mostrar uma tatuagem e consultar seus passos.
- Registrar passos e atualizar a etapa correspondente.

## Regra principal

Uma tatuagem nova começa como **pedida**. Primeiro, o desenho é aprovado; depois, podem acontecer uma ou mais sessões; por fim, após a cicatrização, acontece o retoque. O sistema recusa uma sessão antes da aprovação do desenho e recusa o retoque antes de pelo menos uma sessão. Quando um passo é aceito, a etapa muda de acordo com ele.

## Como a pessoa acessa nesta versão

Enquanto o login não faz parte do projeto atual, o front permite escolher o perfil em uma lista, sem senha. A cliente informa na própria requisição quem ela é, para consultar apenas as tatuagens dela.

## O que fica fora desta versão

Orçamento, sinal, pagamento, portfólio com fotos e avisos por mensagem.
