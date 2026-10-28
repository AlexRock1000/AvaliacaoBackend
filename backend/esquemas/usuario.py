import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CadastroUsuarioEntrada(BaseModel):
    """Valida os dados permitidos para criar uma conta de cliente."""

    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=6, max_length=254)
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        email = valor.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Informe um endereço de e-mail válido.")
        return email


class CadastroTatuadorEntrada(CadastroUsuarioEntrada):
    """Valida os dados para criar uma conta de tatuador por uma rota protegida."""


# GRUPOS E PERMISSÕES: forma pública da associação usuário-grupo.
class GrupoUsuarioSaida(BaseModel):
    id: int
    codigo: str
    nome: str


class UsuarioSaida(BaseModel):
    """Campos públicos de usuário; nunca contém senha nem hash."""

    id: int
    nome: str
    tipo: str
    username: str
    email: str
    # GRUPOS E PERMISSÕES: permite que clientes da API identifiquem o grupo associado.
    grupo: GrupoUsuarioSaida


class Token(BaseModel):
    """Resposta OAuth2 com o token de acesso e seu tipo bearer."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
