import os
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "chave-de-testes-nao-utilizar-fora-da-suite")

from banco import conectar
from esquemas.tatuagens import TatuagemEntrada
from main import aplicativo
from repositorios import tatuagem as repositorio_tatuagem
from repositorios import usuario as repositorio_usuario
from seguranca import verificar_senha
from servicos import tatuagem as servico_tatuagem


class TestAutenticacao(unittest.TestCase):
    def setUp(self):
        repositorio_tatuagem._tatuagens.clear()
        self._limpar_cadastros_de_teste()
        self.cliente = TestClient(aplicativo)

    def tearDown(self):
        repositorio_tatuagem._tatuagens.clear()
        self._limpar_cadastros_de_teste()

    def _limpar_cadastros_de_teste(self):
        conexao = conectar()
        try:
            conexao.execute(
                """
                DELETE FROM usuarios
                WHERE email = 'ana@example.com'
                   OR email = 'nao-tatuador@example.com'
                   OR email LIKE '%@copilot-tests.invalid'
                   OR email LIKE 'ana-%@example.com'
                   OR email LIKE 'duplicado-%@example.com'
                   OR email LIKE 'nao-tatuador-%@example.com'
                """
            )
            conexao.commit()
        finally:
            conexao.close()

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
                "SELECT senha_hash FROM usuarios WHERE username = 'bruna'"
            ).fetchone()["senha_hash"]
        finally:
            conexao.close()

        usuario = repositorio_usuario.buscar_usuario_por_id(1)
        self.assertTrue(verificar_senha("bruna123", senha_armazenada))
        self.assertNotIn("password", usuario)
        self.assertNotIn("senha_hash", usuario)

    def test_cadastro_cria_cliente_e_permite_login_por_email(self):
        email = f"ana-{uuid4().hex}@copilot-tests.invalid"
        resposta = self.cliente.post(
            "/usuarios",
            json={"nome": "Ana Cliente", "email": email.upper(), "senha": "senha-segura-123"},
        )

        self.assertEqual(resposta.status_code, 201, resposta.text)
        dados_usuario = resposta.json()
        self.assertEqual(dados_usuario["tipo"], "cliente")
        self.assertEqual(dados_usuario["email"], email)
        self.assertNotIn("senha", dados_usuario)
        self.assertNotIn("senha_hash", dados_usuario)

        token = self._login(email, "senha-segura-123")
        self.assertTrue(token)

    def test_cadastro_rejeita_email_duplicado(self):
        dados = {
            "nome": "Ana",
            "email": f"duplicado-{uuid4().hex}@copilot-tests.invalid",
            "senha": "senha-segura-123",
        }
        primeira = self.cliente.post("/usuarios", json=dados)
        segunda = self.cliente.post("/usuarios", json=dados)

        self.assertEqual(primeira.status_code, 201, primeira.text)
        self.assertEqual(segunda.status_code, 409)

    def test_cadastro_nao_permite_escolher_perfil_de_tatuador(self):
        resposta = self.cliente.post(
            "/usuarios",
            json={
                "nome": "Conta indevida",
                "email": f"nao-tatuador-{uuid4().hex}@copilot-tests.invalid",
                "senha": "senha-segura-123",
                "tipo": "tatuador",
            },
        )

        self.assertEqual(resposta.status_code, 201, resposta.text)
        self.assertEqual(resposta.json()["tipo"], "cliente")

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
