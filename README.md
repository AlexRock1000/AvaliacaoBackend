# Tinta Negra Tattoo Studio

Aplicação para acompanhar pedidos, desenhos, sessões e retoques em um estúdio de tatuagem. A cliente Bruna acompanha seus pedidos pelo celular; o tatuador Vitor organiza projetos e agenda pelo computador.

## Documentos e referências

- [Cartilha original](Docs/CARTILHA.md): referência inicial do projeto.
- [Briefing atualizado](Docs/BRIEFING.md): escopo implementado nesta versão.
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

Edite `backend/.env` para conter `ENDERECO_FRONTEND=http://localhost:5173` e inicie a API:

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

- **Autenticação:** login simples com usuário e senha para cliente e tatuador, emitindo token JWT em memória para proteger as rotas da API.
- **Cliente:** cria e edita pedidos enquanto estão na etapa inicial, anexa imagem de referência, acompanha etapa e histórico, consulta o desenho enviado e aprova ou pede ajustes.
- **Tatuador:** acompanha a visão geral, agenda e projetos; filtra tatuagens por etapa; envia o desenho; agenda sessões e registra o retoque.
- **Agenda:** o tatuador escolhe a duração inteira da sessão, a partir de uma hora. A disponibilidade considera a duração escolhida, evita sobreposições e mantém os horários entre 10h e 20h, fora do almoço; não há agendamentos às segundas-feiras.
- **Retoque:** quando a sessão é confirmada como realizada, o sistema cria uma reserva inicial de duas horas a partir de 15 dias depois. Na ficha do retoque, antes de confirmá-lo como realizado, o tatuador escolhe a duração a partir de uma hora e um horário compatível; a reserva é atualizada sem sobrepor outros agendamentos.
- **API:** lista e consulta tatuagens, filtra por etapa e cliente, cria e atualiza pedidos, consulta passos e horários disponíveis por data e duração, registra passos e atualiza a situação de sessões, e agora exige autenticação e autorização por perfil.

## Dados e organização

Os dados ficam em listas na memória do backend e são apagados quando a API reinicia. Imagens são mantidas como texto codificado junto ao pedido ou passo. O backend está dividido em `rotas/`, `servicos/`, `repositorios/` e `esquemas/`; o frontend usa React e `fetch`.

Para executar os testes automatizados, consulte [TESTES_AUTOMATIZADOS.md](Docs/TESTES_AUTOMATIZADOS.md).
