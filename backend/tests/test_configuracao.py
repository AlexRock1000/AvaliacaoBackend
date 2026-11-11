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

    def test_le_chaves_dos_tres_provedores_de_ia(self):
        with patch.dict(
            os.environ,
            {
                "GOOGLE_API_KEY": "google-teste",
                "ANTHROPIC_API_KEY": "anthropic-teste",
                "OPENAI_API_KEY": "openai-teste",
            },
        ):
            configuracao = obter_configuracao()

        self.assertEqual(configuracao.chave_google, "google-teste")
        self.assertEqual(configuracao.chave_anthropic, "anthropic-teste")
        self.assertEqual(configuracao.chave_openai, "openai-teste")
