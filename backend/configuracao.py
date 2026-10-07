import os

from dotenv import load_dotenv


# Lê do arquivo local o endereço exato do front permitido pelo CORS.
def obter_configuracao():
    load_dotenv()
    return {
        "endereco_frontend": os.getenv("ENDERECO_FRONTEND"),
        "chave_do_token": os.getenv("CHAVE_DO_TOKEN") or os.getenv("SECRET_KEY"),
    }
