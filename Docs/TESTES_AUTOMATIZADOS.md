# Testes automatizados

Esta documentação descreve como validar o fluxo de sessões do estúdio.

## Backend

A suíte usa `unittest`, incluído no Python, para verificar as regras de sessão sem iniciar um servidor. Os dados em memória são limpos antes e depois de cada teste.

Os cenários cobertos são:

- criar um projeto, enviar o desenho, aprová-lo e agendar uma sessão;
- verificar que o agendamento reserva o horário;
- cancelar a sessão e verificar que o horário volta a ficar disponível;
- confirmar uma sessão como realizada;
- gerar automaticamente um horário de retoque a partir de 15 dias depois, sem marcar segundas-feiras;
- reservar o horário do retoque para impedir colisão com outra sessão;
- rejeitar uma segunda alteração de uma sessão já encerrada;
- rejeitar situações não permitidas.

No PowerShell, a partir da pasta `backend`, instale as dependências do projeto uma vez e execute a suíte:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Se o ambiente virtual já tiver sido criado conforme o [README](../README.md), use:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Frontend

O projeto ainda não tem uma suíte de testes de interface. Para verificar automaticamente que as telas e os componentes compilam para produção, execute na pasta `frontend`:

```powershell
npm.cmd run build
```

O build verifica a compilação do React e do CSS; os testes do backend verificam as regras e os estados do agendamento usados pela API.
