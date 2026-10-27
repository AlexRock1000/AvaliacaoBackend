# Testes e validação

## Backend

Os testes usam `unittest` e exercitam serviços e rotas com o banco SQLite local. Cada teste limpa as tabelas de tatuagens e passos antes e depois da execução; os usuários de demonstração permanecem no banco e contas criadas pelos testes são removidas.

Os cenários cobertos são:

- ordenação decrescente por identificador nas listas geral e filtradas por cliente ou etapa;
- fluxo de envio e aprovação do desenho para preparar uma sessão;
- reserva de horário, cancelamento e liberação do horário;
- confirmação de sessão realizada e criação automática do agendamento de retoque;
- escolha de horário de retoque a partir de 15 dias, sem segunda-feira e sem colisão com outra reserva;
- recusa de alteração de sessão já encerrada;
- validação de situação permitida pelo esquema de entrada;
- login válido/inválido, armazenamento e verificação de hash, e não exposição de credenciais;
- cadastro de cliente, normalização de e-mail, rejeição de duplicidade, recusa de autoatribuição de perfil e login subsequente por e-mail;
- migração da tabela de usuários para e-mail e hash de senha, com preenchimento para contas legadas.

Os testes de agendamento existentes usam a duração padrão de duas horas; ainda não verificam durações personalizadas nem a atualização da reserva na ficha do retoque.

No PowerShell, a partir da pasta `backend`, instale as dependências uma vez e rode a suíte:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Com o ambiente virtual do [README](../README.md):

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

A suíte de backend possui 21 testes; todos passaram na última validação após a reorganização de usuários e autenticação. O inventário completo dessa alteração está em [ALTERACOES_AUTENTICACAO_CADASTRO.md](ALTERACOES_AUTENTICACAO_CADASTRO.md).

## Frontend

Não há testes automatizados de interface. Para verificar se o React e o CSS compilam para produção, na pasta `frontend` execute:

```powershell
npm.cmd run build
```

## Verificação manual da API

Inicie o backend e acesse `http://localhost:8000/docs`. A documentação interativa permite conferir as rotas de tatuagens, passos, horários e atualização de situação.

## Verificação integrada do build

O frontend não tem testes automatizados de interface. A validação manual mais recente do fluxo integrado gerou o build com `npm.cmd run build`, serviu `frontend/dist` pelo Caddy em `http://localhost:8080` e confirmou login e consultas pelos dois perfis demonstrativos. No JavaScript gerado, a base das chamadas é `/api`; o navegador usa o mesmo host e a mesma porta da tela. Essa execução local não representa uma publicação HTTPS.

Para repetir a verificação, siga a seção [Build e teste integrado com Caddy](../README.md#build-e-teste-integrado-com-caddy). Mantenha a API acessível ao contêiner na porta 8000 e confira também `http://127.0.0.1:8000/health`, que deve responder `{"status":"ok"}`. Durante o teste no navegador, a aba Rede deve mostrar chamadas para `localhost:8080/api/...`; o Caddy encaminha essas rotas à API.
