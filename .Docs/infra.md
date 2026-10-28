# Infraestrutura

Este desenho separa o que o código já faz localmente do que ainda é uma proposta de produção. Não há provedor, domínio ou servidor de produção configurados neste repositório.

## Plano

```mermaid
flowchart LR
  subgraph DEV["Desenvolvimento — computador de desenvolvimento"]
    navegadorDev["Navegador — cliente; o React roda aqui"]
    vite["Vite — entrega a tela na porta 5173"]
    apiDev["FastAPI + Uvicorn — porta 8000, local"]
    bancoDev[("SQLite — backend/database.sqlite3")]
    navegadorDev -->|abre a tela HTTP :5173| vite
    vite -->|entrega os arquivos React| navegadorDev
    navegadorDev -->|/login, /me, /usuarios, /tatuagens| vite
    vite -->|proxy para 127.0.0.1:8000| apiDev
    apiDev -->|lê e grava| bancoDev
  end

  subgraph PROD["Produção — proposta; hospedagem ainda a escolher"]
    navegadorProd["Navegador — máquina da pessoa, cliente"]
    dns["Domínio e DNS — a configurar"]
    subgraph SERVIDOR["Uma máquina de aplicação — proposta inicial"]
      web["Servidor web — HTTPS público :443; serve a tela e encaminha as rotas da API"]
      apiProd["FastAPI + Uvicorn — porta 8000, acesso interno"]
      bancoProd[("SQLite — disco persistente no servidor da API; cópias de segurança necessárias")]
      web -->|/login, /me, /usuarios, /tatuagens pela rede interna| apiProd
      apiProd -->|lê e grava| bancoProd
    end
    navegadorProd -.->|consulta o nome| dns
    dns -.->|resolve para o servidor| web
    navegadorProd -->|acessa o domínio por HTTPS :443| web
    web -->|entrega os arquivos da tela| navegadorProd
  end
```

Na proposta, só o HTTPS na porta 443 fica público. A API na porta 8000 e o arquivo SQLite ficam na máquina de aplicação. O SQLite não tem porta de rede. O uso de uma única API evita presumir que o arquivo SQLite será compartilhado por várias máquinas.

## Conferência das caixas

Não encontrei um desenho anterior de infraestrutura da IA no repositório. Conferi as caixas deste plano com o código e com as regras da aula:

| Caixa | Conferência |
| --- | --- |
| Navegador / React | Confirmado: o React executa no navegador da pessoa. |
| Vite | Confirmado apenas no desenvolvimento; o README informa a tela em `localhost:5173`. Não é apresentado como servidor de produção. |
| FastAPI + Uvicorn | Confirmado: API local na porta 8000. O proxy do Vite aponta para o loopback. |
| SQLite | Confirmado: o código cria `backend/database.sqlite3`; não há MySQL nem porta 3306 neste checkout. |
| Domínio / DNS e servidor web HTTPS | Peças propostas para produção; ainda não configuradas. |
| Disco persistente e cópias de segurança | Necessários para preservar o arquivo SQLite na proposta; a rotina de cópias ainda precisa ser definida. |
| CDN, balanceador, réplica de banco e monitoramento | Não aparecem configurados no projeto. Ficaram fora do plano inicial por não haver necessidade ou serviço escolhido que os sustente. |

## Desenvolvimento e produção

| Item | Desenvolvimento | Produção planejada |
| --- | --- | --- |
| Endereço da API | A tela usa rotas relativas; `VITE_URL_DA_API` fica vazio e o Vite encaminha `/login`, `/me`, `/usuarios` e `/tatuagens` para `127.0.0.1:8000`. | O navegador chama `/api/...` na mesma origem HTTPS. O servidor web remove `/api` e encaminha a rota ao FastAPI interno na porta 8000. `frontend/.env.production` define `VITE_URL_DA_API=/api`. No teste local do Caddy, a tela fica em `http://localhost:8080` e os pedidos da API usam essa mesma origem; o contêiner escuta na 80 e publica a 8080 no computador. Esse teste HTTP não é a configuração pública HTTPS. |
| Tela | Vite entrega a aplicação; React roda no navegador do computador de desenvolvimento. | Servidor web entrega os arquivos da aplicação ao navegador da pessoa. Ainda não há hospedagem configurada. |
| Banco | SQLite local no arquivo `backend/database.sqlite3`, na máquina que roda a API. | Proposta inicial: manter SQLite em disco persistente na máquina da API e definir cópias de segurança. Sem réplica nem várias instâncias da API. |
| Configuração e segredo | `backend/.env` local fornece `ENDERECO_FRONTEND` e `CHAVE_DO_TOKEN`; o `.env` não deve ir ao Git. | Configurações e chave próprias do ambiente, fornecidas ao servidor sem publicar o segredo. Hospedagem e mecanismo de configuração ainda não escolhidos. |
| CORS | A API libera a origem exata definida por `ENDERECO_FRONTEND`, se a variável estiver preenchida. | Se tela e API usarem a mesma origem HTTPS, o navegador não precisa de CORS. Se forem origens diferentes, configurar a origem pública exata em `ENDERECO_FRONTEND`; domínio ainda indefinido. |

## Caminho do login e máquina de cada etapa

1. **Bruna ou Vitor preenche usuário e senha** no navegador do próprio aparelho. O React roda nesse navegador; em desenvolvimento, a pessoa está no computador que também roda os servidores locais.
2. **O navegador envia `POST /login`** como formulário `application/x-www-form-urlencoded`. Em desenvolvimento, a chamada chega ao Vite na porta 5173, que a encaminha ao FastAPI em `127.0.0.1:8000`. Vite e FastAPI rodam no computador de desenvolvimento. Em produção, a tela chama `/api/login` na mesma origem, e o servidor web remove o prefixo `/api` antes de encaminhar `/login` ao FastAPI.
3. **O FastAPI autentica** na máquina da API. A rota `/login` chama o serviço, que procura e-mail ou username no SQLite local e confere o hash da senha. Credenciais inválidas recebem `401`.
4. **O FastAPI assina e devolve um JWT** para o navegador. O token contém o identificador e expira em 60 minutos. O navegador guarda o token em `localStorage` e consulta `GET /me` com `Authorization: Bearer ...`.
5. **O FastAPI valida o token e busca a conta atual** no SQLite. A tela abre a área de cliente ou tatuador conforme o perfil retornado. As chamadas protegidas seguintes também enviam o bearer token; uma resposta `401` apaga os dados locais da sessão.

Na produção proposta, o navegador continuaria no aparelho da pessoa; DNS e servidor web receberiam o acesso HTTPS, e o proxy encaminharia `/api/...` ao FastAPI interno após remover o prefixo. O Caddyfile copiado da aula atende HTTP na porta 80 dentro do contêiner e publica a porta 8080 localmente em `http://localhost:8080`, sem domínio nem HTTPS; é um teste local, separado da proposta pública HTTPS.

Referências do fluxo: [formulário e login no React](../frontend/src/Aplicativo.jsx#L1091), [proxy de desenvolvimento](../frontend/vite.config.js#L3), [rota `/login` e `/me`](../backend/rotas/autenticacao.py#L12), [autenticação](../backend/servicos/usuario.py#L25), [consulta SQLite](../backend/repositorios/usuario.py#L36), [JWT e validação](../backend/seguranca.py#L71), [banco local](../backend/banco.py#L8).

## Endereços fixos no código/configuração

- `127.0.0.1`: [frontend/vite.config.js](../frontend/vite.config.js#L5), linhas 5, 9, 13 e 17 — destino do proxy local do Vite para login, identidade, usuários e tatuagens.
- `127.0.0.1`: [.vscode/tasks.json](../.vscode/tasks.json#L7), linha 7 — endereço de escuta da tarefa local que inicia o Uvicorn; é configuração do VS Code.
- `host.docker.internal`: [Caddyfile](../Caddyfile#L5), linha 5 — o Caddy no contêiner usa esse nome para alcançar a API na máquina host; não é um endereço usado pelo navegador.

`frontend/src/api.js` lê `VITE_URL_DA_API`; em desenvolvimento, a base vazia mantém as chamadas relativas, e no build de produção a base é `/api`. A API também expõe `GET /health`, que retorna `{"status":"ok"}`.

Na validação integrada local, o build foi servido pelo Caddy em `http://localhost:8080`; o JavaScript gerado usa `/api`, sem endereço loopback como base das chamadas, e os logins e consultas dos dois perfis demonstrativos foram conferidos. Esse resultado valida o caminho navegador → Caddy → API no ambiente local, sem significar que a proposta HTTPS esteja publicada. Os passos para repetir o teste estão no [README](../README.md#build-e-teste-integrado-com-caddy).

O [Dockerfile do frontend](../frontend/Dockerfile) registra a construção em duas etapas: Node 22 gera o build e a imagem final do Caddy recebe `dist/` e o `Caddyfile` da aula. O contexto de build é a raiz do repositório; `.dockerignore` exclui ambientes virtuais, dependências já instaladas e arquivos de ambiente, mantendo `.env.production` para configurar `/api`. A imagem foi construída e iniciada localmente: `GET /` respondeu HTTP 200 e `GET /api/health` retornou `{"status":"ok"}`. Essa imagem segue a configuração HTTP do exercício e ainda não é uma publicação de produção.
