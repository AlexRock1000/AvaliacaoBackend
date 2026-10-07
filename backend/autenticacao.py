from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from configuracao import obter_configuracao
from repositorios import usuario as repositorio_usuario

configuracao = obter_configuracao()
SEGREDO = configuracao.get("secret_key") or "tinta-negra-tattoo-studio-secret-2026"
ALGORITMO = "HS256"

security = HTTPBearer(auto_error=False)


class CredenciaisLogin(BaseModel):
    username: str
    password: str


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    tipo: str
    username: str


def gerar_token(usuario: dict) -> str:
    payload = {
        "sub": str(usuario["id"]),
        "nome": usuario["nome"],
        "tipo": usuario["tipo"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(payload, SEGREDO, algorithm=ALGORITMO)


def verificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SEGREDO, algorithms=[ALGORITMO])
    except jwt.PyJWTError as erro:
        raise ValueError("Token inválido ou expirado.") from erro


def obter_usuario_atual(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação ausente.")

    try:
        payload = verificar_token(credentials.credentials)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro)) from erro

    usuario = repositorio_usuario.buscar_usuario_por_id(payload.get("sub"))
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return usuario


def exigir_perfil(*tipos_permitidos):
    def dependente(usuario: dict = Depends(obter_usuario_atual)):
        if usuario["tipo"] not in tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return usuario

    return dependente


def garantir_acesso_tatuagem(usuario: dict, tatuagem: dict):
    if usuario["tipo"] == "cliente" and tatuagem["cliente_id"] != usuario["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este pedido não pertence a este perfil de cliente.",
        )
