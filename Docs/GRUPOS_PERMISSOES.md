# Grupos de usuários e permissões

## Como funciona

O backend tem um grupo para cada persona: `cliente` e `tatuador`. Cada conta recebe exatamente um grupo. A autorização lê as permissões do grupo no PostgreSQL, enquanto o campo `tipo` continua na resposta da API para manter compatibilidade com o frontend.

As tabelas de autorização são:

- `grupos`: grupos `cliente` e `tatuador`.
- `usuario_grupos`: associação entre conta e grupo; `usuario_id` é chave primária, então a conta tem no máximo um grupo.
- `permissoes`: catálogo de operações autorizáveis.
- `grupo_permissoes`: permissões de cada grupo.

Na inicialização, o banco cria as tabelas e associa contas existentes com base no campo `tipo`. Um tipo antigo desconhecido é associado ao grupo `cliente`, de menor privilégio. O cadastro público também sempre atribui o grupo `cliente`; a requisição não escolhe o grupo.

## Permissões iniciais

| Operação | Cliente | Tatuador |
| --- | --- | --- |
| Consultar `/me` e horários disponíveis | Sim | Sim |
| Listar tatuagens | Apenas as próprias | Todas |
| Consultar detalhes e passos | Apenas das próprias | Todas |
| Criar pedido e editar pedido próprio | Sim | Não |
| Aprovar desenho ou solicitar ajustes | Sim | Não |
| Registrar desenho, sessão e demais passos | Não | Sim |
| Atualizar situação de sessão e agendar retoque | Não | Sim |
| Criar contas para outros tatuadores | Não | Sim |

As rotas públicas `POST /usuarios` e `POST /login` não exigem sessão; `POST /usuarios` sempre cria um cliente. A rota `POST /usuarios/tatuadores` exige uma sessão com a permissão `contas:cadastrar_tatuador`, atribuída ao grupo tatuador. As demais rotas protegidas verificam a permissão do grupo. A checagem de propriedade continua aplicada às tatuagens e aos seus passos.

## Onde ajustar

`backend/permissoes.py` contém o catálogo de códigos e a matriz inicial das permissões de cada grupo. Altere essa matriz para conceder ou remover operações; ao iniciar o backend, `backend/banco.py` sincroniza os vínculos no PostgreSQL. Os blocos relacionados no código estão marcados com o comentário `GRUPOS E PERMISSÕES`.

`backend/seguranca.py` contém as dependências e verificações reutilizáveis. `backend/rotas/tatuagens.py` declara a permissão necessária para cada operação; o cadastro aplica a associação em `backend/repositorios/usuario.py`.
