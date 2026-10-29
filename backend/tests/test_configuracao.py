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
