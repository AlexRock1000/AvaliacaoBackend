from fastapi import APIRouter, Depends, HTTPException, status

from esquemas.usuario import CredenciaisLogin, UsuarioSaida
from seguranca import gerar_token, obter_usuario_atual
from servicos import usuario as servico_usuario

roteador = APIRouter(tags=["Autenticação"])


@roteador.post("/login")
def login(credenciais: CredenciaisLogin):
    """Autentica por username legado ou e-mail e retorna token e perfil público."""
    usuario = servico_usuario.autenticar(credenciais.username, credenciais.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )
    return {"token": gerar_token(usuario), "usuario": usuario}


@roteador.get("/me", response_model=UsuarioSaida)
def me(usuario: dict = Depends(obter_usuario_atual)):
    """Retorna a identidade pública associada ao bearer token atual."""
    return usuario
