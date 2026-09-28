import os

from dotenv import load_dotenv


# Lê do arquivo local o endereço exato do front permitido pelo CORS.
def obter_configuracao():
    load_dotenv()
    return {"endereco_frontend": os.getenv("ENDERECO_FRONTEND")}
