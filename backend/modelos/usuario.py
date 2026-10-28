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
    # GRUPOS E PERMISSÕES: dados de associação preenchidos pelas consultas com JOIN.
    grupo_id: int | None = None
    grupo_codigo: str | None = None
    grupo_nome: str | None = None

    def para_publico(self) -> dict:
        """Retorna somente campos seguros para respostas e autorização."""
        if self.id is None:
            raise ValueError("O usuário precisa estar salvo antes de ser exposto.")
        dados = {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "username": self.username,
            "email": self.email,
        }
        # GRUPOS E PERMISSÕES: expõe o grupo sem incluir senha ou hash na resposta.
        if self.grupo_id is not None and self.grupo_codigo and self.grupo_nome:
            dados["grupo"] = {
                "id": self.grupo_id,
                "codigo": self.grupo_codigo,
                "nome": self.grupo_nome,
            }
        return dados


def usuario_da_linha(linha) -> Usuario | None:
    """Converte uma linha PostgreSQL no modelo de domínio interno."""
    if linha is None:
        return None
    colunas = set(linha.keys())
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        tipo=linha["tipo"],
        username=linha["username"],
        email=linha["email"],
        senha_hash=linha["senha_hash"],
        # GRUPOS E PERMISSÕES: também aceita linhas sem JOIN durante uma migração.
        grupo_id=linha["grupo_id"] if "grupo_id" in colunas else None,
        grupo_codigo=linha["grupo_codigo"] if "grupo_codigo" in colunas else None,
        grupo_nome=linha["grupo_nome"] if "grupo_nome" in colunas else None,
    )
