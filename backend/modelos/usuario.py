from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Usuario:
    """Representa os dados persistidos de uma conta, inclusive o hash privado."""

    nome: str
    tipo: str
    username: str
    email: str
    senha_hash: str
    id: int | None = None
