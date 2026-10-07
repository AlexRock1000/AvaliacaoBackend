from fastapi import APIRouter, HTTPException, status

from autenticacao import CredenciaisLogin, gerar_token, obter_usuario_atual
from repositorios import usuario as repositorio_usuario

roteador = APIRouter(tags=["Autenticação"])


@roteador.post("/login")
def login(credenciais: CredenciaisLogin):
    usuario = repositorio_usuario.autenticar(credenciais.username, credenciais.password)
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
def me(usuario: dict = obter_usuario_atual):
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "tipo": usuario["tipo"],
        "username": usuario["username"],
    }
