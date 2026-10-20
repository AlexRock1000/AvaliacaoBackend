import os
import sqlite3

from seguranca import hashear_senha, senha_esta_hasheada
from permissoes import GRUPOS_CADASTRO, PERMISSOES_CADASTRO


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
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            senha_hash TEXT NOT NULL
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
    if {"email", "senha_hash"}.issubset(colunas) and "password" not in colunas and "password_hash" not in colunas:
        return

    registros = conexao.execute("SELECT * FROM usuarios").fetchall()
    conexao.execute("ALTER TABLE usuarios RENAME TO usuarios_legado")
    _criar_tabela_usuarios(conexao)
    for registro in registros:
        senha = None
        for coluna_senha in ("senha_hash", "password_hash", "password"):
            if coluna_senha in colunas and registro[coluna_senha]:
                senha = registro[coluna_senha]
                break
        senha_hash = senha if senha_esta_hasheada(senha) else hashear_senha(senha or "")
        username = registro["username"]
        email = (
            registro["email"].strip().lower()
            if "email" in colunas and registro["email"]
            else f"{username}@tintanegra.local"
        )
        conexao.execute(
            """
            INSERT INTO usuarios (id, nome, tipo, username, email, senha_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (registro["id"], registro["nome"], registro["tipo"], username, email, senha_hash),
        )
    conexao.execute("DROP TABLE usuarios_legado")


# GRUPOS E PERMISSÕES: cria o catálogo e grava as permissões iniciais de cada persona.
def _preparar_tabelas_autorizacao(conexao):
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS permissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            descricao TEXT NOT NULL
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS grupo_permissoes (
            grupo_id INTEGER NOT NULL,
            permissao_id INTEGER NOT NULL,
            PRIMARY KEY (grupo_id, permissao_id),
            FOREIGN KEY(grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
            FOREIGN KEY(permissao_id) REFERENCES permissoes(id) ON DELETE CASCADE
        )
        """
    )

    # Mantém o catálogo conhecido pelo código disponível para referências do banco.
    for codigo, descricao in PERMISSOES_CADASTRO.items():
        conexao.execute(
            "INSERT OR IGNORE INTO permissoes (codigo, descricao) VALUES (?, ?)",
            (codigo, descricao),
        )

    # A matriz em permissoes.py é a configuração editável; o SQLite guarda os
    # vínculos efetivos que as rotas consultam, sincronizados a cada inicialização.
    for codigo, dados_grupo in GRUPOS_CADASTRO.items():
        existente = conexao.execute(
            "SELECT id FROM grupos WHERE codigo = ?", (codigo,)
        ).fetchone()
        if existente is None:
            cursor = conexao.execute(
                "INSERT INTO grupos (codigo, nome) VALUES (?, ?)",
                (codigo, dados_grupo["nome"]),
            )
            grupo_id = cursor.lastrowid
        else:
            grupo_id = existente["id"]

        # Sincroniza inclusões e remoções feitas na matriz antes de aceitar requisições.
        conexao.execute("DELETE FROM grupo_permissoes WHERE grupo_id = ?", (grupo_id,))
        for permissao_codigo in dados_grupo["permissoes"]:
            permissao = conexao.execute(
                "SELECT id FROM permissoes WHERE codigo = ?",
                (permissao_codigo,),
            ).fetchone()
            if permissao is None:
                raise RuntimeError(
                    f"Permissão inicial não cadastrada: {permissao_codigo}."
                )
            conexao.execute(
                "INSERT INTO grupo_permissoes (grupo_id, permissao_id) VALUES (?, ?)",
                (grupo_id, permissao["id"]),
            )


# GRUPOS E PERMISSÕES: cada conta recebe exatamente um grupo, definido pela persona.
def _preparar_vinculos_grupos(conexao):
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario_grupos (
            usuario_id INTEGER PRIMARY KEY,
            grupo_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY(grupo_id) REFERENCES grupos(id)
        )
        """
    )

    # Associa contas existentes sem vínculo; perfis desconhecidos recebem o grupo
    # de menor privilégio para impedir que uma migração antiga conceda acesso maior.
    contas = conexao.execute("SELECT id, tipo FROM usuarios").fetchall()
    codigos_grupo = set(GRUPOS_CADASTRO)
    for conta in contas:
        grupo_codigo = conta["tipo"] if conta["tipo"] in codigos_grupo else "cliente"
        grupo = conexao.execute(
            "SELECT id FROM grupos WHERE codigo = ?", (grupo_codigo,)
        ).fetchone()
        if grupo is None:
            raise RuntimeError(f"Grupo necessário não cadastrado: {grupo_codigo}.")
        conexao.execute(
            "INSERT OR IGNORE INTO usuario_grupos (usuario_id, grupo_id) VALUES (?, ?)",
            (conta["id"], grupo["id"]),
        )


def inicializar_banco():
    conexao = conectar()
    try:
        # GRUPOS E PERMISSÕES: cria grupos antes de migrar usuários e atribuir vínculos.
        _preparar_tabelas_autorizacao(conexao)
        _preparar_tabela_usuarios(conexao)
        _preparar_vinculos_grupos(conexao)
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
            (1, "Bruna", "cliente", "bruna", "bruna@tintanegra.local", "bruna123"),
            (2, "Vitor", "tatuador", "vitor", "vitor@tintanegra.local", "vitor123"),
        )
        for usuario_id, nome, tipo, username, email, senha in contas_demo:
            existente = conexao.execute(
                "SELECT 1 FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
            if existente is None:
                conexao.execute(
                    """
                    INSERT INTO usuarios (id, nome, tipo, username, email, senha_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (usuario_id, nome, tipo, username, email, hashear_senha(senha)),
                )

        # GRUPOS E PERMISSÕES: também associa as contas de demonstração recém-criadas.
        _preparar_vinculos_grupos(conexao)

        conexao.commit()
    finally:
        conexao.close()
