import re

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


class CredenciaisLogin(BaseModel):
    """Aceita o nome de usuário legado ou o e-mail cadastrado."""

    username: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UsuarioSaida(BaseModel):
    """Campos públicos de usuário; nunca contém senha nem hash."""

    id: int
    nome: str
    tipo: str
    username: str
    email: str