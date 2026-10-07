from datetime import datetime, timedelta, timezone

import jwt

from configuracao import obter_configuracao
from seguranca_senhas import hashear_senha, verificar_senha


configuracao = obter_configuracao()
CHAVE_DO_TOKEN = configuracao.get("secret_key")
if not CHAVE_DO_TOKEN or CHAVE_DO_TOKEN == "tinta-negra-tattoo-studio-secret-2026":
    raise RuntimeError(
        "Configure uma CHAVE_DO_TOKEN única e aleatória no arquivo backend/.env."
    )

ALGORITMO_TOKEN = "HS256"


def gerar_token(usuario: dict) -> str:
    """Assina um token de sessão com validade de oito horas."""
    payload = {
        "sub": str(usuario["id"]),
        "nome": usuario["nome"],
        "tipo": usuario["tipo"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(payload, CHAVE_DO_TOKEN, algorithm=ALGORITMO_TOKEN)


def verificar_token(token: str) -> dict:
    """Valida assinatura e expiração do token recebido pela API."""
    try:
        return jwt.decode(token, CHAVE_DO_TOKEN, algorithms=[ALGORITMO_TOKEN])
    except jwt.PyJWTError as erro:
        raise ValueError("Token inválido ou expirado.") from erro


__all__ = ["gerar_token", "hashear_senha", "verificar_senha", "verificar_token"]
