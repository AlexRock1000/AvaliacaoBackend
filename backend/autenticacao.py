from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from esquemas.usuario import CredenciaisLogin, UsuarioSaida
from repositorios import usuario as repositorio_usuario
from seguranca import gerar_token, verificar_token

security = HTTPBearer(auto_error=False)


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


__all__ = [
    "CredenciaisLogin",
    "UsuarioSaida",
    "exigir_perfil",
    "garantir_acesso_tatuagem",
    "gerar_token",
    "obter_usuario_atual",
    "verificar_token",
]
