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
```

O `requirements.txt` já inclui `PyJWT`; também é possível instalá-lo diretamente. Para gerar uma chave hexadecimal aleatória de 64 caracteres, rode na pasta `backend`:

```powershell
.venv\Scripts\python.exe -m pip install PyJWT
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para `CHAVE_DO_TOKEN=` em `backend/.env`, junto com `ENDERECO_FRONTEND=http://localhost:5173`. Em `backend/.env.exemplo`, mantenha a linha `CHAVE_DO_TOKEN=` sem valor. `configuracao.py` lê essa variável; `SECRET_KEY` continua aceita como alias. O `.env` local é ignorado pelo Git, então `git status` não deve listá-lo. Nunca copie a chave para o exemplo, logs ou documentação. Ao trocar a chave, reinicie a API e faça login novamente: os tokens emitidos com a chave anterior deixam de valer.

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

## Build e teste integrado com Caddy

O frontend centraliza a URL da API em `frontend/src/api.js`. No desenvolvimento, a URL relativa passa pelo proxy do Vite até a API local. O build de produção usa `/api`, para que o navegador envie as chamadas à mesma origem que serviu a tela. Veja [decisoes.md](decisoes.md) para o motivo e [o plano de infraestrutura](.Docs/infra.md) para o diagrama completo.

Para testar o build integrado localmente, mantenha a API rodando em outro terminal. Como o Caddy será executado em um contêiner, inicie a API aceitando conexões da rede local do Docker:

```powershell
cd backend
.venv\Scripts\python.exe -m uvicorn main:aplicativo --host 0.0.0.0 --reload
```

Confira `http://127.0.0.1:8000/health`; a resposta esperada é `{"status":"ok"}`. O `frontend/Dockerfile` executa `npm ci` e `npm run build` em uma etapa temporária com Node 22. A imagem final contém o Caddy, os arquivos de `dist/` e o `Caddyfile`; não precisa montar a pasta `dist` do computador. Com a API ainda rodando, na raiz do repositório construa e execute a imagem:

```powershell
docker build -f frontend/Dockerfile -t tinta-negra .
docker run --rm -d --name tinta-negra-web -p 8080:80 tinta-negra
```

Abra `http://localhost:8080`. A tela e os pedidos `/api/...` usam a mesma origem; o Caddy remove `/api` ao encaminhar o pedido para a API na porta 8000 do computador host. A configuração atual é um teste local em HTTP, não uma publicação de produção com HTTPS. Para parar a instância em segundo plano, execute `docker stop tinta-negra-web`; se ela já estiver rodando, pare-a antes de repetir o comando.

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
- `repositorios/usuario.py`: consulta usuários por ID, username e e-mail e persiste novos registros no SQLite.
- `repositorios/grupo.py`: consulta as permissões efetivas do grupo associado a uma conta.
- `servicos/usuario.py`: implementa cadastro de cliente e autenticação sem permitir autoatribuição do perfil de tatuador.
- `rotas/autenticacao.py`: expõe `/login` e `/me`; `rotas/usuarios.py` expõe `POST /usuarios`.
- `rotas/tatuagens.py`: contém as rotas do domínio de tatuagens e passos, protegidas por bearer token e autorização por grupo. Não há entidade genérica de tarefas neste projeto.

## Dados e organização

Os dados de usuários, grupos, permissões, tatuagens e passos ficam no banco SQLite local `backend/database.sqlite3` e persistem após reiniciar a API. A inicialização migra usuários legados, associa cada conta ao grupo correspondente e preenche e-mail de demonstração ou converte senhas para hashes quando necessário. O arquivo do banco é local e ignorado pelo Git; planeje backups antes de usar os dados em produção. Imagens são enviadas como data URL codificada em base64 e limitadas a 5 MB por arquivo. As contas Bruna (`bruna` / `bruna123`) e Vitor (`vitor` / `vitor123`) são credenciais demonstrativas e devem ser alteradas ou removidas antes de qualquer implantação real. Para consultar a matriz aplicada e como alterá-la, veja [Grupos e permissões](Docs/GRUPOS_PERMISSOES.md).

Para executar os testes automatizados, consulte [TESTES_AUTOMATIZADOS.md](Docs/TESTES_AUTOMATIZADOS.md). Para detalhes da reorganização de usuários e autenticação, consulte [ALTERACOES_AUTENTICACAO_CADASTRO.md](Docs/ALTERACOES_AUTENTICACAO_CADASTRO.md).
