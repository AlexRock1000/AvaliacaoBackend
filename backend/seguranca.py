import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from configuracao import obter_configuracao


ALGORITMO_HASH = "pbkdf2_sha256"
ITERACOES_HASH = 600_000
TAMANHO_SALT = 16
ALGORITMO_TOKEN = "HS256"
_CONFIGURACAO = obter_configuracao()
_SEGREDO_TOKEN = _CONFIGURACAO.get("chave_do_token")


def validar_chave_token():
    """Falha no startup se a chave do token estiver ausente ou for conhecida."""
    _obter_segredo_token()


def _obter_segredo_token() -> str:
    segredo = _SEGREDO_TOKEN
    if not segredo or segredo == "tinta-negra-tattoo-studio-secret-2026":
        raise RuntimeError(
            "Configure CHAVE_DO_TOKEN ou SECRET_KEY com um valor aleatório em backend/.env."
        )
    return segredo

_AUTORIZACAO_BEARER = HTTPBearer(auto_error=False)


def hashear_senha(senha: str) -> str:
    """Gera hash PBKDF2 com salt aleatório exclusivo por senha."""
    salt = secrets.token_bytes(TAMANHO_SALT)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, ITERACOES_HASH
    )
    return f"{ALGORITMO_HASH}${ITERACOES_HASH}${salt.hex()}${hash_bytes.hex()}"


def senha_esta_hasheada(valor: str | None) -> bool:
    """Identifica hashes válidos pelo prefixo do formato interno."""
    return isinstance(valor, str) and valor.startswith(f"{ALGORITMO_HASH}$")


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    """Compara uma senha com hash persistido sem comparação temporal simples."""
    if not isinstance(senha_hash, str):
        return False
    try:
        algoritmo, iteracoes_texto, salt_texto, hash_esperado_texto = senha_hash.split("$")
        iteracoes = int(iteracoes_texto)
        salt = bytes.fromhex(salt_texto)
        hash_esperado = bytes.fromhex(hash_esperado_texto)
    except (ValueError, TypeError):
        return False
    if algoritmo != ALGORITMO_HASH or not 100_000 <= iteracoes <= 2_000_000:
        return False
    hash_calculado = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, iteracoes
    )
    return hmac.compare_digest(hash_calculado, hash_esperado)


def gerar_token(usuario: dict) -> str:
    """Emite token JWT de oito horas contendo apenas identificador e perfil."""
    payload = {
        "sub": str(usuario["id"]),
        "nome": usuario["nome"],
        "tipo": usuario["tipo"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(payload, _obter_segredo_token(), algorithm=ALGORITMO_TOKEN)


def verificar_token(token: str) -> dict:
    """Valida a assinatura e a expiração do token recebido."""
    try:
        return jwt.decode(token, _obter_segredo_token(), algorithms=[ALGORITMO_TOKEN])
    except jwt.PyJWTError as erro:
        raise ValueError("Token inválido ou expirado.") from erro


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_AUTORIZACAO_BEARER),
) -> dict:
    """Resolve o usuário do token sem importar serviço durante a carga do módulo."""
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente.",
        )
    try:
        payload = verificar_token(credenciais.credentials)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro)) from erro

    from servicos import usuario as servico_usuario

    usuario = servico_usuario.buscar_por_id(payload.get("sub"))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )
    return usuario


def exigir_perfil(*tipos_permitidos):
    """Gera dependência FastAPI que limita o endpoint aos perfis informados."""
    def dependente(usuario: dict = Depends(obter_usuario_atual)) -> dict:
        if usuario["tipo"] not in tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return usuario

    return dependente


def garantir_acesso_tatuagem(usuario: dict, tatuagem: dict):
    """Impede que uma cliente consulte ou altere pedido pertencente a outra."""
    if usuario["tipo"] == "cliente" and tatuagem["cliente_id"] != usuario["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este pedido não pertence a este perfil de cliente.",
        )