import sqlite3

from banco import conectar, inicializar_banco
from modelos.usuario import Usuario, usuario_da_linha

inicializar_banco()


def buscar_usuario_por_id(usuario_id) -> dict | None:
    """Busca uma conta por identificador sem expor seu hash de senha."""
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT * FROM usuarios WHERE id = ?", (int(usuario_id),)
        ).fetchone()
        usuario = usuario_da_linha(linha)
        return usuario.para_publico() if usuario else None
    finally:
        conexao.close()


def buscar_por_email(email: str) -> Usuario | None:
    """Busca modelo interno pelo e-mail normalizado, incluindo hash privado."""
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT * FROM usuarios WHERE email = ? COLLATE NOCASE",
            (email.strip().lower(),),
        ).fetchone()
        return usuario_da_linha(linha)
    finally:
        conexao.close()


def buscar_por_username(username: str) -> Usuario | None:
    """Busca modelo interno pelo username demonstrativo ou legado."""
    conexao = conectar()
    try:
        linha = conexao.execute(
            "SELECT * FROM usuarios WHERE username = ? COLLATE NOCASE",
            (username.strip().lower(),),
        ).fetchone()
        return usuario_da_linha(linha)
    finally:
        conexao.close()


def salvar(usuario: Usuario) -> Usuario:
    """Persiste usuário já validado e hasheado pelo serviço."""
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """
            INSERT INTO usuarios (nome, tipo, username, email, senha_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario.nome, usuario.tipo, usuario.username, usuario.email, usuario.senha_hash),
        )
        conexao.commit()
        linha = conexao.execute(
            "SELECT * FROM usuarios WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        salvo = usuario_da_linha(linha)
        if salvo is None:
            raise RuntimeError("Não foi possível recuperar o usuário salvo.")
        return salvo
    except sqlite3.IntegrityError as erro:
        conexao.rollback()
        raise ValueError("Este e-mail já está cadastrado.") from erro
    finally:
        conexao.close()
