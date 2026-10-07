from fastapi import APIRouter, Depends, HTTPException, status

from autenticacao import CredenciaisLogin, gerar_token, obter_usuario_atual
from servicos import usuario as servico_usuario

roteador = APIRouter(tags=["Autenticação"])


@roteador.post("/login")
def login(credenciais: CredenciaisLogin):
    usuario = servico_usuario.autenticar_usuario(
        credenciais.username,
        str(credenciais.email) if credenciais.email else None,
        credenciais.password,
    )
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")

    return {
        "token": gerar_token(usuario),
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "tipo": usuario["tipo"],
            "username": usuario["username"],
        },
    }


@roteador.get("/me")
def me(usuario: dict = Depends(obter_usuario_atual)):
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "tipo": usuario["tipo"],
        "username": usuario["username"],
    }
