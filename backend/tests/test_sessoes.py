import unittest
from datetime import date, timedelta

from pydantic import ValidationError

from esquemas.passos import PassoEntrada, PassoSaida, SituacaoSessaoEntrada
from esquemas.tatuagens import TatuagemEntrada
from repositorios import tatuagem as repositorio_tatuagem
from servicos import tatuagem as servico_tatuagem


class TestSessoes(unittest.TestCase):
    def setUp(self):
        repositorio_tatuagem._tatuagens.clear()

    def tearDown(self):
        repositorio_tatuagem._tatuagens.clear()

    def criar_projeto_com_desenho_aprovado(self):
        tatuagem = servico_tatuagem.criar_tatuagem(
            TatuagemEntrada(
                ideia="Rosa de teste",
                local_corpo="Antebraço",
                tamanho="12 cm",
                cliente_id=1,
            )
        )
        hoje = date.today()
        desenho = servico_tatuagem.registrar_passo(
            tatuagem["id"],
            PassoEntrada(
                tipo="desenho_enviado",
                data=hoje,
                observacao="Desenho enviado para aprovação.",
                imagem="data:image/png;base64,dGVzdGU=",
            ),
        )
        self.assertNotIsInstance(desenho, str)
        aprovacao = servico_tatuagem.registrar_passo(
            tatuagem["id"],
            PassoEntrada(tipo="desenho_aprovado", data=hoje, observacao="Aprovado pela cliente."),
        )
        self.assertNotIsInstance(aprovacao, str)
        return tatuagem["id"]

    def obter_data_e_horario_disponiveis(self):
        data_sessao = date.today() + timedelta(days=7)
        while data_sessao.weekday() == 0:
            data_sessao += timedelta(days=1)
        horarios = servico_tatuagem.listar_horarios_disponiveis(data_sessao)
        self.assertTrue(horarios)
        return data_sessao, horarios[0]

    def agendar_sessao(self, tatuagem_id, data_sessao, horario):
        return servico_tatuagem.registrar_passo(
            tatuagem_id,
            PassoEntrada(
                tipo="sessao",
                data=data_sessao,
                horario=horario,
                observacao="Sessão agendada. Duração: 2 horas.",
            ),
        )

    def test_agendamento_reserva_horario_e_cancelamento_libera_horario(self):
        tatuagem_id = self.criar_projeto_com_desenho_aprovado()
        data_sessao, horario = self.obter_data_e_horario_disponiveis()

        sessao = self.agendar_sessao(tatuagem_id, data_sessao, horario)
        self.assertEqual(sessao["situacao"], "agendada")
        self.assertNotIn(horario, servico_tatuagem.listar_horarios_disponiveis(data_sessao))

        cancelada = servico_tatuagem.atualizar_situacao_sessao(
            tatuagem_id, sessao["id"], "cancelada"
        )
        self.assertEqual(cancelada["situacao"], "cancelada")
        self.assertEqual(cancelada["observacao"], "Sessão cancelada.")
        self.assertIn(horario, servico_tatuagem.listar_horarios_disponiveis(data_sessao))

    def test_confirmacao_marca_sessao_como_realizada(self):
        tatuagem_id = self.criar_projeto_com_desenho_aprovado()
        data_sessao, horario = self.obter_data_e_horario_disponiveis()
        sessao = self.agendar_sessao(tatuagem_id, data_sessao, horario)

        realizada = servico_tatuagem.atualizar_situacao_sessao(
            tatuagem_id, sessao["id"], "realizada"
        )

        self.assertEqual(realizada["situacao"], "realizada")
        self.assertEqual(realizada["observacao"], "Sessão realizada.")
        self.assertEqual(PassoSaida.model_validate(realizada).situacao, "realizada")

    def test_sessao_encerrada_nao_pode_ser_atualizada_novamente(self):
        tatuagem_id = self.criar_projeto_com_desenho_aprovado()
        data_sessao, horario = self.obter_data_e_horario_disponiveis()
        sessao = self.agendar_sessao(tatuagem_id, data_sessao, horario)
        servico_tatuagem.atualizar_situacao_sessao(tatuagem_id, sessao["id"], "cancelada")

        resultado = servico_tatuagem.atualizar_situacao_sessao(
            tatuagem_id, sessao["id"], "realizada"
        )

        self.assertIsInstance(resultado, str)

    def test_situacao_invalida_e_rejeitada_pelo_esquema_da_api(self):
        with self.assertRaises(ValidationError):
            SituacaoSessaoEntrada(situacao="pendente")


if __name__ == "__main__":
    unittest.main()
