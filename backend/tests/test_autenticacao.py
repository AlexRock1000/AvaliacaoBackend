import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "chave-de-testes-nao-utilizar-fora-da-suite")

from banco import conectar
from esquemas.tatuagens import TatuagemEntrada
from main import aplicativo
from repositorios import tatuagem as repositorio_tatuagem
from repositorios import usuario as repositorio_usuario
from servicos import tatuagem as servico_tatuagem


class TestAutenticacao(unittest.TestCase):
    def setUp(self):
        repositorio_tatuagem._tatuagens.clear()
        self.cliente = TestClient(aplicativo)

    def tearDown(self):
        repositorio_tatuagem._tatuagens.clear()

    def _login(self, username, password):
        resposta = self.cliente.post("/login", json={"username": username, "password": password})
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()["token"]

    def test_login_com_credenciais_validas_retorna_token(self):
        token = self._login("bruna", "bruna123")
        self.assertTrue(token)

    def test_senha_armazenada_com_hash_e_nao_exposta_no_usuario(self):
        conexao = conectar()
        try:
            senha_armazenada = conexao.execute(
                "SELECT password_hash FROM usuarios WHERE username = 'bruna'"
            ).fetchone()["password_hash"]
        finally:
            conexao.close()

        usuario = repositorio_usuario.buscar_usuario_por_id(1)
        self.assertTrue(senha_armazenada.startswith("pbkdf2_sha256$"))
        self.assertNotIn("password", usuario)
        self.assertNotIn("password_hash", usuario)

    def test_login_com_senha_incorreta_retorna_nao_autorizado(self):
        resposta = self.cliente.post(
            "/login", json={"username": "bruna", "password": "senha-errada"}
        )
        self.assertEqual(resposta.status_code, 401)

    def test_cliente_nao_pode_acessar_tatuagem_de_outra_pessoa(self):
        servico_tatuagem.criar_tatuagem(
            TatuagemEntrada(
                ideia="Tatuagem da Bruna",
                local_corpo="Costas",
                tamanho="18 cm",
                cliente_id=1,
            )
        )
        servico_tatuagem.criar_tatuagem(
            TatuagemEntrada(
                ideia="Tatuagem do cliente 2",
                local_corpo="Braço",
                tamanho="12 cm",
                cliente_id=2,
            )
        )

        token_bruna = self._login("bruna", "bruna123")
        resposta = self.cliente.get(
            "/tatuagens/2",
            headers={"Authorization": f"Bearer {token_bruna}"},
        )

        self.assertEqual(resposta.status_code, 403)

    def test_tatuador_pode_listar_todas_as_tatuagens(self):
        servico_tatuagem.criar_tatuagem(
            TatuagemEntrada(
                ideia="Cliente 1",
                local_corpo="Costas",
                tamanho="18 cm",
                cliente_id=1,
            )
        )
        servico_tatuagem.criar_tatuagem(
            TatuagemEntrada(
                ideia="Cliente 2",
                local_corpo="Braço",
                tamanho="12 cm",
                cliente_id=2,
            )
        )

        token_vitor = self._login("vitor", "vitor123")
        resposta = self.cliente.get(
            "/tatuagens",
            headers={"Authorization": f"Bearer {token_vitor}"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.json()), 2)


if __name__ == "__main__":
    unittest.main()
