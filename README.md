# Tinta Negra Tattoo Studio

Aplicação para acompanhar pedidos, desenhos, sessões e retoques em um estúdio de tatuagem. A cliente Bruna acompanha seus pedidos pelo celular; o tatuador Vitor organiza projetos e agenda pelo computador.

## Documentos e referências

- [Cartilha original](Docs/CARTILHA.md): referência inicial do projeto.
- [Briefing atualizado](Docs/BRIEFING.md): escopo implementado nesta versão.
- [Registro das alterações de cadastro e autenticação](Docs/ALTERACOES_AUTENTICACAO_CADASTRO.md): estrutura, migration, endpoints e testes.
- [Grupos e permissões](Docs/GRUPOS_PERMISSOES.md): grupos por persona e permissões aplicadas às rotas.
- [Regras do projeto](REGRAS.md)
- [Testes automatizados](Docs/TESTES_AUTOMATIZADOS.md)
- [Plano de infraestrutura e ambientes](.Docs/infra.md)
- [Decisão sobre a URL da API no build](decisoes.md)
- [Protótipo visual no Figma](https://www.figma.com/make/wLYOJUSL3igbq7cDs07YNY/Sistema-para-est%C3%BAdio-de-tatuagem?t=KweCrSBwk0mXwx39-1)

## Rodar o backend

### Usando Supabase

```powershell
cd backend
if (-not (Test-Path .env)) { Copy-Item .env.exemplo .env }
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No painel do Supabase, abra **Connect** e copie a URI PostgreSQL do projeto. Prefira a URI do pooler recomendada pelo painel quando a conexão direta não estiver disponível na sua rede. Preencha `DATABASE_URL` em `backend/.env` com essa URI; não inclua a senha em arquivos versionados, mensagens ou logs. Preencha também `ENDERECO_FRONTEND=http://localhost:5173` e defina `CHAVE_DO_TOKEN` com uma chave aleatória. Para gerar a chave, rode na pasta `backend`:

```powershell
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Com o ambiente virtual ativado e o terminal dentro de `backend/`, crie as tabelas e registre o baseline Alembic:

```powershell
.\.venv\Scripts\Activate.ps1
python criar_tabelas.py
alembic stamp 0001_esquema_inicial
alembic upgrade head
fastapi dev main.py
```

O comando `criar_tabelas.py` cria o esquema sem contas de demonstração. Execute os comandos do Alembic somente se a criação terminar sem erro: `stamp 0001_esquema_inicial` registra o esquema existente, e `upgrade head` aplica as migrations seguintes, incluindo a ativação do RLS nas tabelas do projeto e em `alembic_version`. Sem políticas, a Data API do Supabase não terá acesso às linhas com papéis comuns. A conexão da aplicação com o usuário `postgres` passa por fora do RLS; as permissões e regras de negócio continuam aplicadas pela API. Novas mudanças no esquema devem ser migrations em `backend/migracoes/versions/`. A API roda localmente em `http://localhost:8000`; use `/docs` para cadastrar os perfis e testar cada login. O backend conecta ao PostgreSQL do Supabase; o navegador e a API continuam em execução local.

A camada de banco usa SQLAlchemy com o driver `psycopg2-binary`. O `NullPool` evita manter um pool local de conexões, deixando esse gerenciamento para o pooler do PostgreSQL, como o Supabase.

`backend/.env` é local e ignorado pelo Git; mantenha a senha apenas nesse arquivo. `backend/.env.exemplo` deixa a URL e a chave vazias. `configuracao.py` lê essas variáveis; `SECRET_KEY` continua aceita como alias de `CHAVE_DO_TOKEN`. Ao trocar a chave, reinicie a API e faça login novamente: tokens emitidos com a chave anterior deixam de valer.

### Usando PostgreSQL local com Docker Compose

Se preferir o banco local, copie também o `.env.exemplo` da raiz para `.env` e inicie o serviço `db` com `docker compose up -d db`. Configure `DATABASE_URL` em `backend/.env` com os dados do PostgreSQL local, em vez da URI do Supabase. A inicialização da API cria o esquema local automaticamente.

## Rodar o frontend

Em outro terminal, a partir da raiz:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Abra `http://localhost:5173`. O seletor no cabeçalho alterna entre os perfis Bruna e Vitor.

## Executar com Docker Compose

O Compose reúne três serviços: `web` (Caddy com a tela), `api` (FastAPI) e `db` (PostgreSQL). O banco persiste no volume `postgres_data`; a porta 5432 fica disponível apenas no loopback do computador para permitir executar a API diretamente durante o desenvolvimento. O frontend centraliza a URL da API em `frontend/src/api.js`: no build, `/api` mantém tela e API na mesma origem, e o Caddy encaminha essa rota para `api:8000` na rede interna do Compose. Veja [decisoes.md](decisoes.md) e [o plano de infraestrutura](.Docs/infra.md).

O `.env` da raiz contém as credenciais locais do PostgreSQL; copie `.env.exemplo` para criá-lo e troque a senha de desenvolvimento antes de qualquer uso fora do computador local. A chave JWT e as configurações da API ficam em `backend/.env`, criado a partir de `backend/.env.exemplo`. O Compose passa esse arquivo à API e monta `DATABASE_URL` com o endereço interno do banco.

Para preservar os dados atuais do arquivo SQLite, inicie somente o banco e execute a migração antes de iniciar a API:

```powershell
docker compose up -d db
cd backend
.venv\Scripts\python.exe -m migrar_sqlite_postgresql
cd ..
```

O comando copia usuários, tatuagens e passos para um PostgreSQL vazio, mantém as senhas e os IDs existentes e não altera o arquivo SQLite original. Depois, suba a aplicação normalmente. Se preferir começar sem os dados antigos, pule a migração.

```powershell
docker compose up --build -d
```

Abra `http://localhost:8080`. Para conferir a API, acesse `http://localhost:8080/api/health`; a resposta esperada é `{"status":"ok"}`. O Caddyfile é montado no contêiner e encaminha `/api` ao serviço `api` pela rede interna. A imagem do frontend usa Node 22 somente na etapa de build e Caddy na imagem final.

Para parar os serviços sem apagar os dados do PostgreSQL, execute `docker compose down`. O volume do banco só é removido com `docker compose down -v`. Se um contêiner Caddy antigo já ocupar a porta 8080, pare-o antes de subir o Compose. Esta configuração atende HTTP local; não representa uma publicação HTTPS de produção.

## Funcionalidades implementadas

- **Autenticação:** cadastro de clientes por nome, e-mail e senha; login por e-mail ou usuário; senhas armazenadas em hash PBKDF2 com salt individual e token JWT válido por 60 minutos para proteger as rotas da API. O app valida a sessão ao abrir e retorna ao login quando o token expira. O cadastro nunca permite que a pessoa escolha o perfil de tatuador.
- **Grupos e permissões:** cada conta pertence ao grupo `cliente` ou `tatuador`. O backend confere as permissões do grupo em cada rota protegida, limita clientes aos próprios pedidos e permite ajustar a matriz em `backend/permissoes.py`.
- **Cliente:** cria e edita pedidos enquanto estão na etapa inicial, anexa imagem de referência de até 5 MB, acompanha etapa e histórico, consulta o desenho enviado e aprova ou pede ajustes.
- **Tatuador:** acompanha a visão geral, agenda e projetos; filtra tatuagens por etapa; envia o desenho de até 5 MB; agenda sessões e registra o retoque.
- **Agenda:** o tatuador escolhe a duração inteira da sessão, a partir de uma hora. A disponibilidade considera a duração escolhida, evita sobreposições e mantém os horários entre 10h e 20h, fora do almoço; não há agendamentos às segundas-feiras.
- **Retoque:** quando a sessão é confirmada como realizada, o sistema cria uma reserva inicial de duas horas a partir de 15 dias depois. Na ficha do retoque, antes de confirmá-lo como realizado, o tatuador escolhe a duração a partir de uma hora e um horário compatível; a reserva é atualizada sem sobrepor outros agendamentos.
- **API:** lista e consulta tatuagens, filtra por etapa e cliente, cria e atualiza pedidos, consulta passos e horários disponíveis por data e duração, registra passos e atualiza a situação de sessões, com permissões de rota definidas para os grupos.

## Organização do backend

- `main.py`: inicializa a API, valida a chave do token, configura CORS e registra os routers.
- `seguranca.py`: centraliza hash/verificação de senha, emissão e validação JWT e regras reutilizáveis de acesso por grupo.
- `permissoes.py`: declara os códigos de permissão e a matriz inicial dos grupos `cliente` e `tatuador`.
- `modelos/usuario.py`: representa o registro interno do usuário (`email` e `senha_hash`) e produz sua versão pública sem credenciais.
- `esquemas/usuario.py`: valida entrada do cadastro/login e define os dados de usuário que podem sair pela API.
- `repositorios/usuario.py`: consulta usuários por ID, username e e-mail e persiste novos registros no PostgreSQL.
- `repositorios/grupo.py`: consulta as permissões efetivas do grupo associado a uma conta.
- `servicos/usuario.py`: implementa cadastro de cliente e autenticação sem permitir autoatribuição do perfil de tatuador.
- `rotas/autenticacao.py`: expõe `/login` e `/me`; `rotas/usuarios.py` expõe `POST /usuarios`.
- `rotas/tatuagens.py`: contém as rotas do domínio de tatuagens e passos, protegidas por bearer token e autorização por grupo. Não há entidade genérica de tarefas neste projeto.

## Dados e organização

Usuários, grupos, permissões, tatuagens e passos são armazenados no PostgreSQL e persistem no volume `postgres_data`. A inicialização cria o esquema e as contas demonstrativas quando necessário. Para importar a base SQLite existente, use o comando de migração acima; o arquivo original permanece local como cópia de segurança. Imagens são enviadas como data URL codificada em base64 e limitadas a 5 MB por arquivo. As contas Bruna (`bruna` / `bruna123`) e Vitor (`vitor` / `vitor123`) são credenciais demonstrativas e devem ser alteradas ou removidas antes de qualquer implantação real. Para consultar a matriz aplicada e como alterá-la, veja [Grupos e permissões](Docs/GRUPOS_PERMISSOES.md).

Para executar os testes automatizados, consulte [TESTES_AUTOMATIZADOS.md](Docs/TESTES_AUTOMATIZADOS.md). Para detalhes da reorganização de usuários e autenticação, consulte [ALTERACOES_AUTENTICACAO_CADASTRO.md](Docs/ALTERACOES_AUTENTICACAO_CADASTRO.md).
