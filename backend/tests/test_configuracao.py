import os
import unittest
from unittest.mock import patch

from configuracao import obter_configuracao


class TestConfiguracaoBanco(unittest.TestCase):
    def test_url_postgresql_padrao_seleciona_driver_instalado(self):
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://usuario:senha@db.exemplo.com:5432/app"},
        ):
            configuracao = obter_configuracao()

        self.assertEqual(
            configuracao.url_do_banco,
            "postgresql+psycopg2://usuario:senha@db.exemplo.com:5432/app",
        )

    def test_url_com_driver_explicito_permanece_inalterada(self):
        url = "postgresql+psycopg2://usuario:senha@db.exemplo.com:5432/app"
        with patch.dict(os.environ, {"DATABASE_URL": url}):
            configuracao = obter_configuracao()

        self.assertEqual(configuracao.url_do_banco, url)

    def test_le_chaves_dos_provedores_planejados(self):
        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "gemini-teste",
                "OPENROUTER_API_KEY": "openrouter-teste",
                "ANTHROPIC_API_KEY": "anthropic-teste",
            },
        ):
            configuracao = obter_configuracao()

        self.assertEqual(configuracao.chave_do_gemini, "gemini-teste")
        self.assertEqual(configuracao.chave_do_openrouter, "openrouter-teste")
        self.assertEqual(configuracao.chave_do_claude, "anthropic-teste")
