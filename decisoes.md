# Decisões

## Por que `.env.production` contém apenas `/api`

`VITE_URL_DA_API=/api` é um caminho relativo à origem da página, não um endereço de servidor completo. Assim, se a tela estiver em `http://localhost:8080`, o navegador chama `http://localhost:8080/api/login` e mantém o protocolo, o host e a porta da própria tela. Em produção, o mesmo caminho relativo usa automaticamente o domínio HTTPS publicado.

O navegador vê tela e API na mesma origem, então não precisa de CORS entre elas. O servidor web encaminha `/api/*` para a API interna e remove o prefixo `/api`; por isso a rota `/api/login` chega à API como `/login`. No teste desta aula, o Caddy faz esse encaminhamento para a API na porta 8000, enquanto publica a tela e os pedidos pelo host na porta 8080.

No desenvolvimento, `.env.development` deixa `VITE_URL_DA_API` vazio: a tela usa caminhos relativos e o proxy do Vite encaminha as rotas ao FastAPI local. O destino `127.0.0.1:8000` em `vite.config.js` é usado pelo processo do Vite, não pelo navegador.

A aplicação lê essa configuração por `frontend/src/api.js`, que centraliza a base usada pelas chamadas da interface. O build foi conferido depois da troca: o JavaScript gerado usa `/api` e não inclui `localhost` ou `127.0.0.1` como destino das chamadas da interface. O destino loopback continua apenas no proxy de desenvolvimento do Vite.

## Deploy independente na Vercel

O deploy separado mantém `VITE_URL_DA_API` como URL HTTPS absoluta do backend Vercel, definida nas variáveis de build do projeto frontend. Essa variável de ambiente prevalece sobre `frontend/.env.production`, que continua como `/api` para o deploy local via Docker/Caddy. O backend expõe o mesmo FastAPI por `backend/app.py` para o runtime Python Vercel; no projeto backend, `ENDERECO_FRONTEND` deve ser a origem HTTPS exata do frontend para CORS. Segredos e `DATABASE_URL` são variáveis exclusivas do backend.
