import unittest
import sqlite3
import tempfile
from pathlib import Path

from banco import _preparar_tabela_usuarios
from seguranca import hashear_senha, verificar_senha


class TestSegurancaSenhas(unittest.TestCase):
    def test_hash_verifica_senha_correta_e_rejeita_senha_incorreta(self):
        senha_hash = hashear_senha("minha-senha-segura")

        self.assertNotEqual(senha_hash, "minha-senha-segura")
        self.assertTrue(verificar_senha("minha-senha-segura", senha_hash))
        self.assertFalse(verificar_senha("outra-senha", senha_hash))

    def test_senhas_iguais_recebem_hashes_diferentes(self):
        primeiro_hash = hashear_senha("senha-repetida")
        segundo_hash = hashear_senha("senha-repetida")

        self.assertNotEqual(primeiro_hash, segundo_hash)
        self.assertTrue(verificar_senha("senha-repetida", primeiro_hash))
        self.assertTrue(verificar_senha("senha-repetida", segundo_hash))

    def test_migracao_legada_converte_senha_em_hash(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho_banco = Path(diretorio) / "legado.sqlite3"
            conexao = sqlite3.connect(caminho_banco)
            conexao.row_factory = sqlite3.Row
            conexao.execute(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
                """
            )
            conexao.execute(
                "INSERT INTO usuarios VALUES (1, 'Bruna', 'cliente', 'bruna', 'bruna123')"
            )

            _preparar_tabela_usuarios(conexao)

            usuario = conexao.execute(
                "SELECT senha_hash FROM usuarios WHERE username = 'bruna'"
            ).fetchone()
            colunas = [coluna[1] for coluna in conexao.execute("PRAGMA table_info(usuarios)")]
            conexao.close()

        self.assertIn("email", colunas)
        self.assertIn("senha_hash", colunas)
        self.assertNotIn("password", colunas)
        self.assertTrue(verificar_senha("bruna123", usuario["senha_hash"]))

    def test_migracao_preenche_email_para_usuarios_anteriores(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho_banco = Path(diretorio) / "legado.sqlite3"
            conexao = sqlite3.connect(caminho_banco)
            conexao.row_factory = sqlite3.Row
            conexao.execute(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL
                )
                """
            )
            conexao.execute(
                "INSERT INTO usuarios VALUES (1, 'Vitor', 'tatuador', 'vitor', ?) ",
                (hashear_senha("senha-teste"),),
            )

            _preparar_tabela_usuarios(conexao)

            usuario = conexao.execute(
                "SELECT email FROM usuarios WHERE username = 'vitor'"
            ).fetchone()
            conexao.close()

        self.assertEqual(usuario["email"], "vitor@tintanegra.local")


if __name__ == "__main__":
    unittest.main()