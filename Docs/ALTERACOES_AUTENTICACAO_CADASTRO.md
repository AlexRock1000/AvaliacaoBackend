# Registro de alterações — usuários, cadastro e autenticação

## Objetivo

Esta alteração organiza o cadastro e a autenticação do backend em camadas explícitas, adiciona cadastro de clientes por e-mail e atualiza a tabela SQLite sem perder os usuários existentes. A aplicação continua usando o domínio de tatuagens; não foi criada uma entidade genérica de tarefas.

## Arquitetura e arquivos

- [../backend/main.py](../backend/main.py): valida a chave de assinatura no startup e registra os routers de autenticação, usuários e tatuagens.
- [../backend/seguranca.py](../backend/seguranca.py): reúne PBKDF2 com salt aleatório, verificação de senha, geração/validação de JWT, dependência bearer e verificações de perfil/dono do pedido. Substitui a lógica anteriormente separada entre `autenticacao.py` e `seguranca_senhas.py`.
- [../backend/modelos/usuario.py](../backend/modelos/usuario.py): modelo interno com `email` e `senha_hash`; `para_publico()` remove campos de autenticação antes de devolver um usuário.
- [../backend/esquemas/usuario.py](../backend/esquemas/usuario.py): valida nome, e-mail e senha de cadastro, credenciais de login, e define os campos públicos de resposta.
- [../backend/repositorios/usuario.py](../backend/repositorios/usuario.py): implementa busca por ID, username e e-mail, além de `salvar()` no SQLite.
- [../backend/servicos/usuario.py](../backend/servicos/usuario.py): concentra cadastro, autenticação e resolução do usuário atual; as contas cadastradas recebem sempre o perfil `cliente`.
- [../backend/rotas/autenticacao.py](../backend/rotas/autenticacao.py): fornece login e consulta da identidade autenticada.
- [../backend/rotas/usuarios.py](../backend/rotas/usuarios.py): fornece o endpoint de cadastro.
- [../backend/rotas/tatuagens.py](../backend/rotas/tatuagens.py): permanece como router do domínio do produto; as operações exigem token e validam perfil e propriedade da tatuagem.
- [../backend/configuracao.py](../backend/configuracao.py) e [../backend/.env.exemplo](../backend/.env.exemplo): leem `CHAVE_DO_TOKEN`; `SECRET_KEY` continua disponível como alias para compatibilidade.
- [../backend/banco.py](../backend/banco.py): cria o esquema atual e migra usuários legados.
- [../backend/requirements.txt](../backend/requirements.txt): declara `httpx2`, utilizado pelo `TestClient` no ambiente atual.
- [../.gitignore](../.gitignore): exclui `.env`, banco SQLite e arquivos auxiliares locais do versionamento.

## Banco e migração

A tabela `usuarios` passa a conter:

| Coluna | Uso |
| --- | --- |
| `id` | Identificador da conta. |
| `nome` | Nome público. |
| `tipo` | Perfil de autorização, como `cliente` ou `tatuador`. |
| `username` | Identificador compatível com as contas existentes. |
| `email` | E-mail único, comparado sem diferenciar maiúsculas/minúsculas. |
| `senha_hash` | Hash PBKDF2 com salt individual; nunca é devolvido pela API. |

Na inicialização, o banco detecta esquemas anteriores. Senhas em texto puro são convertidas em hash; hashes existentes são preservados. Contas antigas sem e-mail recebem um endereço interno no formato `<username>@tintanegra.local`. A migração mantém IDs, nomes, usernames e tipos já existentes. As contas demonstrativas Bruna e Vitor recebem e-mails demonstrativos nesse mesmo domínio local.

## Chave JWT

Configure `CHAVE_DO_TOKEN` em `backend/.env` com um valor aleatório exclusivo para cada ambiente. A configuração aceita `SECRET_KEY` como alias de compatibilidade. A API falha no startup se a chave estiver ausente ou usar o segredo padrão conhecido. O arquivo `.env` é local, ignorado pelo Git e não deve ser publicado. O valor configurado não deve ser registrado em logs nem enviado em documentação.

O `.env` local foi removido do índice do Git sem apagar a cópia de trabalho. O `.gitignore` também exclui o banco SQLite e seus arquivos auxiliares; esses arquivos permanecem locais e devem ser incluídos em uma política de backup, não em commits.

## API de usuários

### `POST /usuarios`

Cria uma conta de cliente. Exemplo do corpo esperado:

```json
{
  "nome": "Ana Cliente",
  "email": "ana@example.com",
  "senha": "uma-senha-com-pelo-menos-oito-caracteres"
}
```

Retorna HTTP `201` com `id`, `nome`, `tipo`, `username` e `email`. Não retorna a senha nem seu hash. O perfil é definido no serviço e campos extras da requisição não permitem criar uma conta de tatuador. E-mails duplicados retornam HTTP `409`; entradas inválidas são rejeitadas pela validação do esquema.

### `POST /login`

Mantém o formato de credenciais compatível com o frontend: `username` aceita o username existente ou um e-mail, e `password` recebe a senha. Em sucesso, retorna um token JWT e os dados públicos da conta. Credenciais inválidas retornam HTTP `401`.

### `GET /me`

Exige `Authorization: Bearer <token>` e retorna os dados públicos da conta associada ao token.

As rotas de tatuagens continuam protegidas pelo mesmo bearer token. Clientes só podem acessar os próprios pedidos; o perfil de tatuador pode administrar os pedidos do estúdio.

## Compatibilidade e limites

- O login pelas contas demonstrativas existentes via `bruna` e `vitor` permanece compatível.
- O endpoint de cadastro foi adicionado ao backend; esta alteração não cria uma tela de cadastro no frontend.
- Não existe recurso genérico de tarefas neste sistema; por isso, as rotas do produto permanecem em `rotas/tatuagens.py`.
- O cadastro não inclui confirmação de e-mail, recuperação/troca de senha nem criação pública de perfil de tatuador.
- As senhas demonstrativas são conhecidas e não devem ser usadas em produção.

## Testes

A suíte executada contém 21 testes e cobre cadastro, normalização e duplicidade de e-mail, login por e-mail e username, hash e migração de senha, proteção de perfil, ordenação e fluxo de sessões.

Os novos cenários de autenticação e cadastro ficam em [../backend/tests/test_autenticacao.py](../backend/tests/test_autenticacao.py); os testes de hash e migração ficam em [../backend/tests/test_seguranca_senhas.py](../backend/tests/test_seguranca_senhas.py). Os cadastros transitórios usam um domínio reservado de teste e são removidos ao final, sem deixar usuários artificiais na base local.

Para executar, estando na pasta `backend`:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

O resultado validado para esta alteração foi: **21 testes aprovados**.

## Documentação atualizada

- [../README.md](../README.md): instruções de configuração da chave, recursos de cadastro e responsabilidades das camadas.
- [BRIEFING.md](BRIEFING.md): contratos da API, autenticação, persistência e limites atualizados.
- [TESTES_AUTOMATIZADOS.md](TESTES_AUTOMATIZADOS.md): cenários e resultado da suíte.
- [../REGRAS.md](../REGRAS.md): organização arquitetural do backend.
