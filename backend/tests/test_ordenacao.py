import unittest

from esquemas.tatuagens import TatuagemEntrada
from repositorios import tatuagem as repositorio_tatuagem
from servicos import tatuagem as servico_tatuagem


class TestOrdenacaoTatuagens(unittest.TestCase):
    def setUp(self):
        repositorio_tatuagem._tatuagens.clear()

    def tearDown(self):
        repositorio_tatuagem._tatuagens.clear()

    def criar_tatuagem(self, ideia, cliente_id=1, etapa="pedida"):
        tatuagem = servico_tatuagem.criar_tatuagem(
            TatuagemEntrada(
                ideia=ideia,
                local_corpo="Braco",
                tamanho="10 cm",
                cliente_id=cliente_id,
            )
        )
        if etapa != "pedida":
            repositorio_tatuagem.atualizar_etapa(tatuagem["id"], etapa)
        return tatuagem

    def test_lista_geral_prioriza_ids_mais_altos_independente_da_etapa(self):
        primeiro = self.criar_tatuagem("Rosa antiga", etapa="finalizada")
        segundo = self.criar_tatuagem("Lua em andamento", etapa="desenho aprovado")
        terceiro = self.criar_tatuagem("Flor nova")

        tatuagens = servico_tatuagem.listar_tatuagens()

        self.assertEqual([item["id"] for item in tatuagens], [terceiro["id"], segundo["id"], primeiro["id"]])

    def test_filtro_por_cliente_preserva_ordem_do_mais_recente(self):
        primeiro = self.criar_tatuagem("Rosa da cliente", cliente_id=1)
        self.criar_tatuagem("Lua de outra cliente", cliente_id=2)
        segundo = self.criar_tatuagem("Flor da cliente", cliente_id=1)

        tatuagens = servico_tatuagem.listar_tatuagens(cliente_id=1)

        self.assertEqual([item["id"] for item in tatuagens], [segundo["id"], primeiro["id"]])

    def test_filtro_por_etapa_preserva_ordem_do_mais_recente(self):
        primeiro = self.criar_tatuagem("Rosa pedida")
        self.criar_tatuagem("Lua aprovada", etapa="desenho aprovado")
        segundo = self.criar_tatuagem("Flor pedida")

        tatuagens = servico_tatuagem.listar_tatuagens(etapa="pedida")

        self.assertEqual([item["id"] for item in tatuagens], [segundo["id"], primeiro["id"]])


if __name__ == "__main__":
    unittest.main()
