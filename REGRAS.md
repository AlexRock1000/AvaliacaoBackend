# Regras do projeto para a IA

## Objetivo e documentos

O projeto é o Tinta Negra Tattoo Studio. `Docs/CARTILHA.md` registra a proposta original; `Docs/BRIEFING.md` e o `README.md` descrevem o escopo implementado atualmente. Ao alterar o código, atualize a documentação correspondente para manter os três alinhados.

## Estrutura e arquitetura

- O frontend fica em `frontend/` e usa React, CSS responsivo e `fetch`.
- O backend fica em `backend/`, com configuração em `configuracao.py`, inicialização/CORS/registro de routers em `main.py`, modelos de domínio em `modelos/`, validação em `esquemas/`, regras em `servicos/`, acesso ao SQLite em `repositorios/`, endpoints em `rotas/` e hashes/tokens/autorização em `seguranca.py`.
- A direção das chamadas é rota → serviço → repositório. Não importe uma rota em outra.
- A configuração do CORS lê `ENDERECO_FRONTEND` do `.env`; libere somente o endereço exato configurado.
- Os dados são persistidos no SQLite local `backend/database.sqlite3`. Não introduza novos bancos, autenticação ou bibliotecas de busca no frontend sem solicitação explícita.

## Funcionalidades atuais

Considere o fluxo descrito em `Docs/BRIEFING.md`, incluindo pedidos com imagem de referência, edição antes do início, envio e resposta ao desenho, agendamento e atualização de sessões, agendamento automático do retoque e telas de visão geral, agenda, projetos e ficha. A ordenação das tatuagens mais recentes primeiro também faz parte do comportamento atual.

## Convenções de código

- Escreva identificadores, mensagens e comentários em português do Brasil.
- Use funções normais no backend e mantenha as decisões de negócio nos serviços.
- Comente funções, rotas e blocos relevantes explicando sua intenção. Ao apresentar um recurso novo, explique seu papel em comentário curto.
- Preserve os estados de carregamento, erro e sucesso nas telas que consultam a API.
- Valide entradas nos esquemas e mantenha as respostas e os códigos HTTP coerentes com o caso.

## Como responder e documentar

Trabalhe uma solicitação por vez. Antes de editar código, informe brevemente a camada afetada e a razão. Ao concluir mudanças, resuma os arquivos alterados e explique como executar ou conferir o resultado. Quando uma funcionalidade mudar, atualize README, briefing ou documentação de testes conforme necessário; preserve a cartilha original como referência, salvo pedido explícito para modificá-la.
