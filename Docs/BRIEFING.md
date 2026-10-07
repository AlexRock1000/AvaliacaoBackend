# Briefing — Tinta Negra Tattoo Studio

## O negócio e o problema

O estúdio tem dois tatuadores. Cada projeto passa pela criação e aprovação do desenho, por uma ou mais sessões e, após a cicatrização, pelo retoque. Hoje as informações ficam espalhadas em conversas, dificultando o acompanhamento das etapas e dos horários.

## Para quem é o sistema

### Bruna — cliente

Bruna tem 27 anos, é designer e fará sua primeira tatuagem grande. Usa o sistema principalmente no celular para:

1. Criar um pedido com ideia, local do corpo, tamanho e imagem de referência opcional.
2. Consultar seus pedidos, etapas, próximos passos e histórico.
3. Editar o pedido enquanto ele ainda está na etapa inicial.
4. Ver o desenho enviado pelo tatuador e aprová-lo ou pedir ajustes com uma observação.
5. Acompanhar as sessões agendadas e o retoque.

### Vitor — tatuador

Vitor organiza os trabalhos do estúdio pelo computador. Usa o sistema para:

1. Consultar a visão geral, a agenda e os projetos, filtrando por etapa.
2. Abrir a ficha do pedido e consultar a referência enviada pela cliente.
3. Enviar o desenho como imagem e acompanhar a aprovação ou solicitação de ajustes.
4. Agendar uma ou mais sessões em horários disponíveis.
5. Cancelar uma sessão ou marcá-la como realizada.
6. Registrar a realização do retoque.

## Autenticação e autorização

A autenticação foi iniciada com login em memória para os perfis de cliente e tatuador. O backend emite um token JWT e exige o cabeçalho `Authorization: Bearer <token>` em todas as rotas protegidas. O cliente só acessa os seus próprios pedidos e o tatuador pode consultar ou administrar qualquer tatuagem do estúdio.

## Etapas e regras implementadas

O pedido começa como **pedida**. O tatuador envia o desenho, que leva à etapa **aguardando aprovação**. A cliente pode aprová-lo (**desenho aprovado**) ou pedir ajustes (**ajustes no desenho**). O tatuador pode reenviar o desenho após ajustes.

Depois da aprovação, o tatuador escolhe a duração de cada sessão em horas inteiras, com mínimo de uma hora, e agenda um horário que comporte essa duração. Horários ocupados não podem ser reservados novamente; sessões canceladas liberam o horário. Sessões e retoques não são agendados às segundas-feiras; a agenda mantém as reservas entre 10h e 20h, exclui o horário de almoço e não oferece horários passados no dia atual.

Ao marcar uma sessão como realizada, o sistema cria uma reserva inicial de retoque de duas horas para uma data disponível a partir de 15 dias depois e atualiza a etapa para **aguardando retoque**. Na ficha do retoque, antes de marcá-lo como realizado, o tatuador escolhe sua duração (mínimo de uma hora) e um horário que comporte esse tempo. A reserva atualizada não pode colidir com outros agendamentos. Ao confirmar o retoque, o projeto passa para **finalizada**. Uma sessão encerrada não pode ser alterada novamente.

## Telas do frontend

- **Pedir tatuagem:** formulário de criação e edição do pedido, com envio opcional de imagem de referência.
- **Minhas tatuagens:** pedidos da cliente, etapa, orientação do próximo passo e histórico; inclui resposta ao desenho.
- **Visão geral:** resumo do trabalho e acesso aos próximos itens da fila.
- **Agenda:** tatuagens e horários de sessão, com ações de cancelamento e confirmação.
- **Projetos:** lista de projetos para acompanhamento e acesso à ficha.
- **Ficha:** detalhes do pedido e registro do desenho, sessão ou retoque, conforme a etapa.

O layout se adapta a celular e computador. A lista de perfis é uma escolha de demonstração, sem autenticação.

## API implementada

- `GET /tatuagens` lista tatuagens; aceita os filtros `etapa` e `cliente_id` e mostra as mais recentes primeiro.
- `GET /tatuagens/{id}` consulta uma tatuagem.
- `POST /tatuagens` cria um pedido.
- `PUT /tatuagens/{id}` atualiza pedido ainda não iniciado, com validação de perfil.
- `GET /tatuagens/{id}/passos` consulta o histórico.
- `POST /tatuagens/{id}/passos` registra desenho, resposta da cliente, sessão ou retoque.
- `GET /tatuagens/horarios-disponiveis?data=AAAA-MM-DD&duracao_horas=N&ignorar_passo_id=ID` lista horários livres que comportam a duração pedida; `ignorar_passo_id` é opcional e permite recalcular a própria reserva do retoque. A duração mínima é uma hora.
- `PATCH /tatuagens/{id}/passos/{passo_id}/situacao` cancela ou confirma uma sessão.
- `PATCH /tatuagens/{id}/passos/{passo_id}/agendamento` ajusta a duração e o horário do retoque agendado.

## Limites desta versão

Os dados são guardados em memória e desaparecem ao reiniciar o backend. A autenticação é simulada com usuários fixos em memória e não substitui um sistema de usuários real e persistente. Imagens são enviadas como conteúdo codificado no JSON. Não fazem parte do escopo pagamentos, orçamento, notificações ou persistência em banco de dados.
