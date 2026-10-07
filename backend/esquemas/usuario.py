from pydantic import BaseModel, EmailStr, Field, model_validator


class UsuarioCadastroEntrada(BaseModel):
    """Valida os dados públicos de cadastro; o perfil não é escolhido pelo cliente."""

    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class UsuarioSaida(BaseModel):
    """Expõe dados do perfil sem incluir a senha ou seu hash."""

    id: int
    nome: str
    tipo: str
    username: str
    email: EmailStr


class CredenciaisLogin(BaseModel):
    """Aceita login pelo username legado ou pelo email cadastrado."""

    username: str | None = None
    email: EmailStr | None = None
    password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validar_identificador(self):
        if not self.username and not self.email:
            raise ValueError("Informe o username ou o email para entrar.")
        return self
