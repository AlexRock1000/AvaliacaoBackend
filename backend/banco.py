import os
import sqlite3

from seguranca_senhas import hashear_senha, senha_esta_hasheada


ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "database.sqlite3")


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def _criar_tabela_usuarios(conexao):
    conexao.execute(
        """
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )


def _preparar_tabela_usuarios(conexao):
    tabela_existe = conexao.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'usuarios'"
    ).fetchone()
    if tabela_existe is None:
        _criar_tabela_usuarios(conexao)
        return

    colunas = {
        coluna["name"]
        for coluna in conexao.execute("PRAGMA table_info(usuarios)").fetchall()
    }
    if "password_hash" in colunas and "email" in colunas and "password" not in colunas:
        return

    registros = conexao.execute("SELECT * FROM usuarios").fetchall()
    conexao.execute("ALTER TABLE usuarios RENAME TO usuarios_legado")
    _criar_tabela_usuarios(conexao)
    for registro in registros:
        senha = registro["password_hash"] if "password_hash" in colunas else None
        if not senha and "password" in colunas:
            senha = registro["password"]
        senha_hash = senha if senha_esta_hasheada(senha) else hashear_senha(senha or "")
        email = registro["email"] if "email" in colunas else None
        if not email:
            email = f"{registro['username']}@example.invalid"
        conexao.execute(
            """
            INSERT INTO usuarios (id, nome, tipo, username, email, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                registro["id"],
                registro["nome"],
                registro["tipo"],
                registro["username"],
                email,
                senha_hash,
            ),
        )
    conexao.execute("DROP TABLE usuarios_legado")


def inicializar_banco():
    conexao = conectar()
    try:
        _preparar_tabela_usuarios(conexao)
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS tatuagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ideia TEXT NOT NULL,
                local_corpo TEXT NOT NULL,
                tamanho TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                etapa TEXT NOT NULL,
                imagem_referencia TEXT
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS passos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tatuagem_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                data TEXT,
                horario TEXT,
                duracao_horas INTEGER,
                observacao TEXT,
                imagem TEXT,
                situacao TEXT,
                FOREIGN KEY(tatuagem_id) REFERENCES tatuagens(id) ON DELETE CASCADE
            )
            """
        )

        contas_demo = (
            (1, "Bruna", "cliente", "bruna", "bruna@example.invalid", "bruna123"),
            (2, "Vitor", "tatuador", "vitor", "vitor@example.invalid", "vitor123"),
        )
        for usuario_id, nome, tipo, username, email, senha in contas_demo:
            existente = conexao.execute(
                "SELECT 1 FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
            if existente is None:
                conexao.execute(
                    """
                    INSERT INTO usuarios (id, nome, tipo, username, email, password_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (usuario_id, nome, tipo, username, email, hashear_senha(senha)),
                )

        conexao.commit()
    finally:
        conexao.close()
