import os
from dataclasses import dataclass

from dotenv import load_dotenv


ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT, ".env"))


@dataclass(frozen=True)
class Configuracao:
    endereco_frontend: str | None
    chave_do_token: str | None
    url_do_banco: str | None


def obter_configuracao() -> Configuracao:
    """Lê as configurações locais usadas pela API e pela conexão do banco."""
    url_do_banco = os.getenv("DATABASE_URL", "").strip()

    return Configuracao(
        endereco_frontend=os.getenv("ENDERECO_FRONTEND"),
        chave_do_token=os.getenv("CHAVE_DO_TOKEN") or os.getenv("SECRET_KEY"),
        url_do_banco=url_do_banco or None,
    )
