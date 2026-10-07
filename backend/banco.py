import os
import sqlite3


ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "database.sqlite3")


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    conexao = conectar()
    try:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )
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

        conexao.execute(
            """
            INSERT OR IGNORE INTO usuarios (id, nome, tipo, username, password)
            VALUES
                (1, 'Bruna', 'cliente', 'bruna', 'bruna123'),
                (2, 'Vitor', 'tatuador', 'vitor', 'vitor123')
            """
        )

        conexao.commit()
    finally:
        conexao.close()
