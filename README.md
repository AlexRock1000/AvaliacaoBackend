# Nervo Tattoo Studio

Aplicação para acompanhar pedidos, etapas e histórico de tatuagens de um estúdio pequeno. O projeto segue as jornadas da Bruna, cliente que usa o celular, e do Vitor, tatuador que organiza o trabalho no computador.

## Referências

- [Cartilha do projeto](Docs/CARTILHA.md)
- [Regras da aula 5](REGRAS.md)
- [Visual no Figma](https://www.figma.com/make/wLYOJUSL3igbq7cDs07YNY/Sistema-para-est%C3%BAdio-de-tatuagem?t=KweCrSBwk0mXwx39-1)

## Rodar o back

No PowerShell, em um terminal:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.exemplo .env }
uvicorn main:aplicativo --reload
```

A API fica em `http://localhost:8000`; a documentação interativa fica em `http://localhost:8000/docs`. Confirme que `backend/.env` contém `ENDERECO_FRONTEND=http://localhost:5173`, pois o back libera o CORS somente para esse endereço.

## Rodar o front

Em outro terminal, na raiz do projeto:

```powershell
cd frontend
npm install
npm run dev
```

Abra o endereço que o Vite mostrar no terminal (normalmente `http://localhost:5173`). A tela permite escolher o perfil Bruna ou Vitor.

## Telas e API

- **Pedir tatuagem:** registra ideia, local do corpo e tamanho.
- **Minhas tatuagens:** filtra os pedidos da cliente e mostra o histórico de passos.
- **A agenda:** lista e filtra tatuagens por etapa.
- **A ficha:** registra desenho aprovado, sessão ou retoque.

O back guarda os dados em listas na memória. Ao reiniciar a API, os pedidos e passos voltam a ficar vazios.

As rotas ficam em `backend/rotas/`, as decisões e regras em `backend/servicos/`, os dados em `backend/repositorios/` e os esquemas em `backend/esquemas/`.
