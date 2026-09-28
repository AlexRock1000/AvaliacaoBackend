# Testes e validação

## Backend

Os testes usam `unittest` e exercitam os serviços sem iniciar o servidor. Cada teste limpa a lista em memória antes e depois da execução.

Os cenários cobertos são:

- ordenação decrescente por identificador nas listas geral e filtradas por cliente ou etapa;
- fluxo de envio e aprovação do desenho para preparar uma sessão;
- reserva de horário, cancelamento e liberação do horário;
- confirmação de sessão realizada e criação automática do agendamento de retoque;
- escolha de horário de retoque a partir de 15 dias, sem segunda-feira e sem colisão com outra reserva;
- recusa de alteração de sessão já encerrada;
- validação de situação permitida pelo esquema de entrada.

No PowerShell, a partir da pasta `backend`, instale as dependências uma vez e rode a suíte:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Com o ambiente virtual do [README](../README.md):

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Frontend

Não há testes automatizados de interface. Para verificar se o React e o CSS compilam para produção, na pasta `frontend` execute:

```powershell
npm.cmd run build
```

## Verificação manual da API

Inicie o backend e acesse `http://localhost:8000/docs`. A documentação interativa permite conferir as rotas de tatuagens, passos, horários e atualização de situação.
