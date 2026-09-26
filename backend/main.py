from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configuracao import obter_configuracao
from rotas.tatuagens import roteador as roteador_tatuagens


# Cria o aplicativo e libera chamadas somente para o endereço configurado do front.
aplicativo = FastAPI(title="Tinta Negra Tattoo Studio")
configuracao = obter_configuracao()
endereco_frontend = configuracao["endereco_frontend"]

# Só registra o CORS quando o endereço foi preenchido no arquivo de ambiente.
if endereco_frontend:
    aplicativo.add_middleware(
        CORSMiddleware,
        allow_origins=[endereco_frontend],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

aplicativo.include_router(roteador_tatuagens)
