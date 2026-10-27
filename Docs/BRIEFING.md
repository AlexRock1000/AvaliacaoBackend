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

A autenticação permite cadastro de clientes por nome, e-mail e senha, além de login por e-mail ou username. As senhas são armazenadas como hashes PBKDF2 com salt individual; o backend emite um token JWT assinado com `CHAVE_DO_TOKEN` configurada no ambiente (`SECRET_KEY` é aceita como alias), válido por 60 minutos, e exige o cabeçalho `Authorization: Bearer <token>` em todas as rotas protegidas. O app valida a sessão ao iniciar e volta ao login se o token expirar. Cada conta pertence a um grupo por persona (`cliente` ou `tatuador`), e as rotas verificam as permissões cadastradas para o grupo. O cadastro sempre atribui o grupo `cliente`; o cliente só acessa os próprios pedidos e o tatuador pode consultar ou administrar qualquer tatuagem do estúdio. As credenciais Bruna (`bruna` / `bruna123`) e Vitor (`vitor` / `vitor123`) são apenas demonstrações. Consulte [Grupos e permissões](GRUPOS_PERMISSOES.md) para a matriz de acesso.

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

O layout se adapta a celular e computador. O fluxo de login utiliza as contas de demonstração criadas pelo backend.

## API implementada

- `POST /usuarios` cadastra uma conta de cliente usando nome, e-mail e senha; o perfil não pode ser escolhido na requisição.
- `POST /login` aceita formulário OAuth2 (`username` recebe username ou e-mail; `password` recebe senha) e devolve `access_token` e `token_type: bearer`. Consulte `GET /me` para obter os dados públicos do usuário.
- `GET /me` exige bearer token e a permissão de consultar a própria conta; devolve também o grupo atual.
- `GET /tatuagens` lista tatuagens; aceita os filtros `etapa` e `cliente_id`, respeita o escopo do grupo e mostra as mais recentes primeiro.
- `GET /tatuagens/{id}` consulta uma tatuagem autorizada pelo grupo e pela propriedade da conta.
- `POST /tatuagens` cria um pedido com a permissão do grupo cliente.
- `PUT /tatuagens/{id}` atualiza pedido próprio ainda não iniciado, conforme a permissão do grupo.
- `GET /tatuagens/{id}/passos` consulta histórico autorizado pelo grupo e pela propriedade.
- `POST /tatuagens/{id}/passos` exige permissão para registrar passos ou para responder ao desenho, conforme o tipo informado.
- `GET /tatuagens/horarios-disponiveis?data=AAAA-MM-DD&duracao_horas=N&ignorar_passo_id=ID` lista horários livres que comportam a duração pedida; `ignorar_passo_id` é opcional e permite recalcular a própria reserva do retoque. A duração mínima é uma hora.
- `PATCH /tatuagens/{id}/passos/{passo_id}/situacao` cancela ou confirma uma sessão.
- `PATCH /tatuagens/{id}/passos/{passo_id}/agendamento` ajusta a duração e o horário do retoque agendado.

## Ambientes e publicação

No desenvolvimento, o Vite entrega a tela em `localhost:5173` e encaminha as chamadas relativas à API local na porta 8000. O frontend centraliza a URL da API em `frontend/src/api.js`; no build, a base `/api` mantém tela e API na mesma origem. O build foi servido localmente pelo Caddy em `http://localhost:8080`, com login e consultas dos dois perfis demonstrativos conferidos. Esse Caddy atende HTTP para o teste de integração; não há publicação de produção configurada.

A arquitetura de produção continua sendo uma proposta: um servidor web receberia HTTPS e encaminharia `/api` à API interna. O banco implementado neste checkout é SQLite em arquivo, não MySQL. O diagrama, as diferenças entre ambientes e os limites dessa proposta estão em [Infraestrutura](../.Docs/infra.md); a razão para usar `/api` no build está em [Decisões](../decisoes.md).

## Dados e limites desta versão

Usuários, grupos, permissões, tatuagens e passos são persistidos em `backend/database.sqlite3`, um arquivo SQLite local que não deve ser enviado ao Git e precisa de rotina de backup. A inicialização migra contas existentes para os grupos correspondentes e o esquema migra automaticamente senhas da estrutura legada para hashes. As contas de demonstração usam senhas conhecidas e não devem ser utilizadas como contas reais; ainda não há fluxo de cadastro, troca ou recuperação de senha na interface. Imagens são enviadas como data URL codificada em base64, com limite de 5 MB validado no navegador e na API. Não fazem parte do escopo pagamentos, orçamento ou notificações.

Para o inventário de arquivos, responsabilidades de cada camada, migration de usuários e contratos de cadastro/login, consulte [ALTERACOES_AUTENTICACAO_CADASTRO.md](ALTERACOES_AUTENTICACAO_CADASTRO.md).
