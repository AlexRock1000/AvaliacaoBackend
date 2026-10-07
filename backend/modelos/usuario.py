from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    """Representa o registro persistido de usuário, incluindo seu hash privado."""

    id: int | None
    nome: str
    tipo: str
    username: str
    email: str
    senha_hash: str

    def para_publico(self) -> dict:
        """Retorna somente campos seguros para respostas e autorização."""
        if self.id is None:
            raise ValueError("O usuário precisa estar salvo antes de ser exposto.")
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "username": self.username,
            "email": self.email,
        }


def usuario_da_linha(linha) -> Usuario | None:
    """Converte uma linha SQLite no modelo de domínio interno."""
    if linha is None:
        return None
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        tipo=linha["tipo"],
        username=linha["username"],
        email=linha["email"],
        senha_hash=linha["senha_hash"],
    )