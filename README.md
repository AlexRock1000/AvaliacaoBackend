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

No PowerShell, a partir da raiz:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.exemplo .env }
cd ..
if (-not (Test-Path .env)) { Copy-Item .env.exemplo .env }
docker compose up -d db
cd backend
```

O `requirements.txt` já inclui `PyJWT`; também é possível instalá-lo diretamente. Para gerar uma chave hexadecimal aleatória de 64 caracteres, rode na pasta `backend`:

```powershell
.venv\Scripts\python.exe -m pip install PyJWT
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para `CHAVE_DO_TOKEN=` em `backend/.env`, junto com `ENDERECO_FRONTEND=http://localhost:5173`. `DATABASE_URL` aponta para o PostgreSQL local iniciado pelo Compose; se alterar os dados de conexão em `.env`, atualize também essa URL. Em `backend/.env.exemplo`, mantenha a chave do token vazia. `configuracao.py` lê essas variáveis; `SECRET_KEY` continua aceita como alias. Os arquivos `.env` locais são ignorados pelo Git. Nunca copie a chave para o exemplo, logs ou documentação. Ao trocar a chave, reinicie a API e faça login novamente: os tokens emitidos com a chave anterior deixam de valer.

```powershell
.venv\Scripts\python.exe -m uvicorn main:aplicativo --reload
```

A API fica em `http://localhost:8000`; a documentação interativa fica em `http://localhost:8000/docs`.

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
