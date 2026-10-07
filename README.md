# Tinta Negra Tattoo Studio

Aplicação para acompanhar pedidos, desenhos, sessões e retoques em um estúdio de tatuagem. A cliente Bruna acompanha seus pedidos pelo celular; o tatuador Vitor organiza projetos e agenda pelo computador.

## Documentos e referências

- [Cartilha original](Docs/CARTILHA.md): referência inicial do projeto.
- [Briefing atualizado](Docs/BRIEFING.md): escopo implementado nesta versão.
- [Registro das alterações de cadastro e autenticação](Docs/ALTERACOES_AUTENTICACAO_CADASTRO.md): estrutura, migration, endpoints e testes.
- [Regras do projeto](REGRAS.md)
- [Testes automatizados](Docs/TESTES_AUTOMATIZADOS.md)
- [Protótipo visual no Figma](https://www.figma.com/make/wLYOJUSL3igbq7cDs07YNY/Sistema-para-est%C3%BAdio-de-tatuagem?t=KweCrSBwk0mXwx39-1)

## Rodar o backend

No PowerShell, a partir da raiz:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.exemplo .env }
```

Edite `backend/.env` para conter `ENDERECO_FRONTEND=http://localhost:5173` e uma chave JWT aleatória e exclusiva em `CHAVE_DO_TOKEN`. Gere uma com `python -c "import secrets; print(secrets.token_urlsafe(48))"` e configure o resultado no arquivo. `SECRET_KEY` ainda é aceita como nome alternativo. A API não inicia se a chave estiver ausente ou usar o segredo demonstrativo antigo. Não compartilhe nem versione esse valor.

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

## Funcionalidades implementadas

- **Autenticação:** cadastro de clientes por nome, e-mail e senha; login por e-mail ou usuário; senhas armazenadas em hash PBKDF2 com salt individual e token JWT para proteger as rotas da API. O cadastro nunca permite que a pessoa escolha o perfil de tatuador.
- **Cliente:** cria e edita pedidos enquanto estão na etapa inicial, anexa imagem de referência, acompanha etapa e histórico, consulta o desenho enviado e aprova ou pede ajustes.
- **Tatuador:** acompanha a visão geral, agenda e projetos; filtra tatuagens por etapa; envia o desenho; agenda sessões e registra o retoque.
- **Agenda:** o tatuador escolhe a duração inteira da sessão, a partir de uma hora. A disponibilidade considera a duração escolhida, evita sobreposições e mantém os horários entre 10h e 20h, fora do almoço; não há agendamentos às segundas-feiras.
- **Retoque:** quando a sessão é confirmada como realizada, o sistema cria uma reserva inicial de duas horas a partir de 15 dias depois. Na ficha do retoque, antes de confirmá-lo como realizado, o tatuador escolhe a duração a partir de uma hora e um horário compatível; a reserva é atualizada sem sobrepor outros agendamentos.
- **API:** lista e consulta tatuagens, filtra por etapa e cliente, cria e atualiza pedidos, consulta passos e horários disponíveis por data e duração, registra passos e atualiza a situação de sessões, e agora exige autenticação e autorização por perfil.

## Organização do backend

- `main.py`: inicializa a API, valida a chave do token, configura CORS e registra os routers.
- `seguranca.py`: centraliza hash/verificação de senha, emissão e validação JWT e regras reutilizáveis de acesso por perfil.
- `modelos/usuario.py`: representa o registro interno do usuário (`email` e `senha_hash`) e produz sua versão pública sem credenciais.
- `esquemas/usuario.py`: valida entrada do cadastro/login e define os dados de usuário que podem sair pela API.
- `repositorios/usuario.py`: consulta usuários por ID, username e e-mail e persiste novos registros no SQLite.
- `servicos/usuario.py`: implementa cadastro de cliente e autenticação sem permitir autoatribuição do perfil de tatuador.
- `rotas/autenticacao.py`: expõe `/login` e `/me`; `rotas/usuarios.py` expõe `POST /usuarios`.
- `rotas/tatuagens.py`: contém as rotas do domínio de tatuagens e passos, protegidas por bearer token e autorização por perfil. Não há entidade genérica de tarefas neste projeto.

## Dados e organização

Os dados de usuários, tatuagens e passos ficam no banco SQLite local `backend/database.sqlite3` e persistem após reiniciar a API. A inicialização migra automaticamente usuários legados, preenchendo e-mail de demonstração quando necessário e convertendo senhas para hashes. O arquivo do banco é local e ignorado pelo Git; planeje backups antes de usar os dados em produção. Imagens são mantidas como texto codificado junto ao pedido ou passo. As contas Bruna (`bruna` / `bruna123`) e Vitor (`vitor` / `vitor123`) são credenciais demonstrativas e devem ser alteradas ou removidas antes de qualquer implantação real. O backend separa modelos, esquemas, serviços, repositórios, rotas e segurança; `rotas/tatuagens.py` protege as rotas próprias do domínio deste sistema.

Para executar os testes automatizados, consulte [TESTES_AUTOMATIZADOS.md](Docs/TESTES_AUTOMATIZADOS.md). Para detalhes da reorganização de usuários e autenticação, consulte [ALTERACOES_AUTENTICACAO_CADASTRO.md](Docs/ALTERACOES_AUTENTICACAO_CADASTRO.md).
