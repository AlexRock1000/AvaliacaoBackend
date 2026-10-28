"""Copia os dados de uma base SQLite local para uma base PostgreSQL vazia."""

import argparse
import sqlite3
import tempfile
from pathlib import Path

from banco import ROOT, conectar, inicializar_banco
from permissoes import GRUPOS_CADASTRO
from seguranca import hashear_senha, senha_esta_hasheada


CAMINHO_SQLITE_PADRAO = Path(ROOT) / "database.sqlite3"


def _preparar_tabela_usuarios_sqlite(conexao):
    """Normaliza uma cópia SQLite antiga para os campos atuais de usuário."""
    tabela_existe = conexao.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'usuarios'"
    ).fetchone()
    if tabela_existe is None:
        return

    colunas = {
        coluna["name"]
        for coluna in conexao.execute("PRAGMA table_info(usuarios)").fetchall()
    }
    if {"email", "senha_hash"}.issubset(colunas) and "password" not in colunas and "password_hash" not in colunas:
        return

    registros = conexao.execute("SELECT * FROM usuarios").fetchall()
    conexao.execute("ALTER TABLE usuarios RENAME TO usuarios_legado")
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
    for registro in registros:
        senha = next(
            (
                registro[coluna]
                for coluna in ("senha_hash", "password_hash", "password")
                if coluna in colunas and registro[coluna]
            ),
            "",
        )
        senha_hash = senha if senha_esta_hasheada(senha) else hashear_senha(senha)
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
    conexao.commit()


def _copiar_tabela(conexao_destino, nome, colunas, valores):
    if not valores:
        return 0
    campos = ", ".join(colunas)
    placeholders = ", ".join("%s" for _ in colunas)
    consulta = (
        f"INSERT INTO {nome} ({campos}) VALUES ({placeholders}) "
        "ON CONFLICT DO NOTHING"
    )
    conexao_destino.executemany(consulta, valores)
    return len(valores)


def _sincronizar_sequencias(conexao):
    for tabela in ("usuarios", "tatuagens", "passos"):
        conexao.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence(%s, 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM {tabela}
            """,
            (tabela,),
        )


def migrar_sqlite_para_postgresql(caminho_sqlite=CAMINHO_SQLITE_PADRAO):
    """Preserva usuários, tatuagens e passos sem alterar o arquivo SQLite original."""
    caminho_sqlite = Path(caminho_sqlite)
    if not caminho_sqlite.is_file():
        raise FileNotFoundError(f"Arquivo SQLite não encontrado: {caminho_sqlite}")

    inicializar_banco(semear_demos=False)
    conexao_destino = conectar()
    try:
        existentes = conexao_destino.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM usuarios) AS usuarios,
                (SELECT COUNT(*) FROM tatuagens) AS tatuagens,
                (SELECT COUNT(*) FROM passos) AS passos
            """
        ).fetchone()
        if any(existentes.values()):
            raise RuntimeError(
                "A migração exige tabelas de usuários, tatuagens e passos vazias no PostgreSQL."
            )
        conexao_destino.commit()

        with tempfile.TemporaryDirectory(prefix="tinta-negra-migracao-") as diretorio:
            copia_sqlite = Path(diretorio) / "origem.sqlite3"
            with sqlite3.connect(caminho_sqlite) as origem:
                with sqlite3.connect(copia_sqlite) as copia:
                    origem.backup(copia)

            conexao_sqlite = sqlite3.connect(copia_sqlite)
            conexao_sqlite.row_factory = sqlite3.Row
            try:
                _preparar_tabela_usuarios_sqlite(conexao_sqlite)
                tabelas = {
                    linha["name"]
                    for linha in conexao_sqlite.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }

                grupos_por_id = {}
                if "grupos" in tabelas:
                    grupos_por_id = {
                        linha["id"]: linha["codigo"]
                        for linha in conexao_sqlite.execute("SELECT id, codigo FROM grupos")
                    }
                tipo_por_usuario = {}
                if "usuario_grupos" in tabelas:
                    tipo_por_usuario = {
                        linha["usuario_id"]: grupos_por_id.get(linha["grupo_id"])
                        for linha in conexao_sqlite.execute(
                            "SELECT usuario_id, grupo_id FROM usuario_grupos"
                        )
                    }

                usuarios = []
                if "usuarios" in tabelas:
                    colunas_usuario = {
                        linha["name"]
                        for linha in conexao_sqlite.execute("PRAGMA table_info(usuarios)")
                    }
                    for linha in conexao_sqlite.execute("SELECT * FROM usuarios"):
                        registro = dict(linha)
                        username = str(registro.get("username") or "").strip().lower()
                        if not username:
                            email_origem = str(registro.get("email") or "").strip().lower()
                            username = email_origem.split("@", 1)[0]
                        email = str(
                            registro.get("email") or f"{username}@tintanegra.local"
                        ).strip().lower()
                        tipo = tipo_por_usuario.get(registro["id"]) or registro.get("tipo")
                        if tipo not in GRUPOS_CADASTRO:
                            tipo = "cliente"
                        senha = next(
                            (
                                registro.get(coluna)
                                for coluna in ("senha_hash", "password_hash", "password")
                                if coluna in colunas_usuario and registro.get(coluna)
                            ),
                            "",
                        )
                        senha_hash = senha if senha_esta_hasheada(senha) else hashear_senha(senha)
                        usuarios.append(
                            (
                                registro["id"],
                                registro.get("nome") or username,
                                tipo,
                                username,
                                email,
                                senha_hash,
                            )
                        )

                tatuagens = []
                if "tatuagens" in tabelas:
                    colunas_tatuagem = {
                        linha["name"]
                        for linha in conexao_sqlite.execute("PRAGMA table_info(tatuagens)")
                    }
                    for linha in conexao_sqlite.execute("SELECT * FROM tatuagens"):
                        registro = dict(linha)
                        tatuagens.append(
                            (
                                registro["id"],
                                registro["ideia"],
                                registro["local_corpo"],
                                str(registro["tamanho"]),
                                registro["cliente_id"],
                                registro["etapa"],
                                registro.get("imagem_referencia")
                                if "imagem_referencia" in colunas_tatuagem
                                else None,
                            )
                        )

                passos = []
                if "passos" in tabelas:
                    colunas_passo = {
                        linha["name"]
                        for linha in conexao_sqlite.execute("PRAGMA table_info(passos)")
                    }
                    for linha in conexao_sqlite.execute("SELECT * FROM passos"):
                        registro = dict(linha)
                        passos.append(
                            (
                                registro["id"],
                                registro["tatuagem_id"],
                                registro["tipo"],
                                registro.get("data") if "data" in colunas_passo else None,
                                registro.get("horario") if "horario" in colunas_passo else None,
                                registro.get("duracao_horas")
                                if "duracao_horas" in colunas_passo
                                else None,
                                registro.get("observacao")
                                if "observacao" in colunas_passo
                                else None,
                                registro.get("imagem") if "imagem" in colunas_passo else None,
                                registro.get("situacao") if "situacao" in colunas_passo else None,
                            )
                        )
            finally:
                conexao_sqlite.close()

        with conexao_destino.transaction():
            _copiar_tabela(
                conexao_destino,
                "usuarios",
                ("id", "nome", "tipo", "username", "email", "senha_hash"),
                usuarios,
            )
            _copiar_tabela(
                conexao_destino,
                "tatuagens",
                ("id", "ideia", "local_corpo", "tamanho", "cliente_id", "etapa", "imagem_referencia"),
                tatuagens,
            )
            _copiar_tabela(
                conexao_destino,
                "passos",
                ("id", "tatuagem_id", "tipo", "data", "horario", "duracao_horas", "observacao", "imagem", "situacao"),
                passos,
            )
            _sincronizar_sequencias(conexao_destino)

        contagens = {
            tabela: len(registros)
            for tabela, registros in (
                ("usuarios", usuarios),
                ("tatuagens", tatuagens),
                ("passos", passos),
            )
        }
    except Exception:
        conexao_destino.rollback()
        raise
    finally:
        conexao_destino.close()

    inicializar_banco()
    print(
        "Migração concluída: "
        f"{contagens['usuarios']} usuários, "
        f"{contagens['tatuagens']} tatuagens e {contagens['passos']} passos copiados."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Copia os dados de backend/database.sqlite3 para PostgreSQL."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=CAMINHO_SQLITE_PADRAO,
        help="caminho do arquivo SQLite de origem",
    )
    argumentos = parser.parse_args()
    migrar_sqlite_para_postgresql(argumentos.source)


if __name__ == "__main__":
    main()
