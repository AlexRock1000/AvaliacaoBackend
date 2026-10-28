# Instruções do projeto

## Pendência autorizada: migrar a base SQLite quando o Docker estiver disponível

O usuário pediu que a IA faça a migração dos dados assim que o Docker puder ser usado. Na próxima sessão neste projeto, retome esta tarefa proativamente quando o daemon do Docker estiver ativo; essa ação já foi autorizada pelo usuário.

1. Na raiz do repositório, confirme que `docker info` funciona e suba somente o PostgreSQL com `docker compose up -d db`.
2. Aguarde o serviço `db` ficar saudável (`docker compose ps`).
3. Execute `python -m migrar_sqlite_postgresql` no diretório `backend`, usando o ambiente virtual existente do projeto e instalando `backend/requirements.txt` se necessário.
4. O migrador copia usuários, tatuagens e passos, preserva IDs e hashes de senha e mantém `backend/database.sqlite3` intacto. Ele exige as tabelas de destino vazias. Se o PostgreSQL já tiver dados e a migração abortar, não apague volume, tabelas ou o arquivo SQLite; inspecione e informe o conflito.
5. Após uma migração bem-sucedida, inicie a aplicação com `docker compose up --build -d` e confirme que os serviços estão ativos.
6. Depois de confirmar a migração, remova esta seção para que a operação não seja repetida em sessões futuras.

O procedimento manual também está documentado na seção **Executar com Docker Compose** do `README.md`.
