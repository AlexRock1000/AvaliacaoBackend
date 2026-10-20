from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from esquemas.usuario import Token, UsuarioSaida
from seguranca import criar_token, obter_usuario_atual
from servicos import usuario as servico_usuario

roteador = APIRouter(tags=["Autenticação"])


@roteador.post("/login", response_model=Token)
def login(formulario: OAuth2PasswordRequestForm = Depends()):
    """Autentica formulário OAuth2 e devolve token bearer de acesso."""
    usuario = servico_usuario.autenticar(formulario.username, formulario.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )
    return {"access_token": criar_token(usuario["id"]), "token_type": "bearer"}


@roteador.get("/me", response_model=UsuarioSaida)
def me(usuario: dict = Depends(obter_usuario_atual)):
    """Retorna a identidade pública associada ao bearer token atual."""
    return usuario
