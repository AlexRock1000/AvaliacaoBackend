import unittest
from datetime import date, time
from types import SimpleNamespace
from unittest.mock import patch

from ia.ferramentas import FERRAMENTAS, dias_ate
from ia import modelos
from ia.sugestao import gerar_sugestao
from servicos.ia import preparar_projetos_para_sugestao


class TestFallbackIA(unittest.TestCase):
    # Confirma que indisponibilidade do provedor principal aciona o próximo configurado.
    def test_tenta_google_antes_de_anthropic_e_openai(self):
        configuracao = SimpleNamespace(
            chave_google="chave-google",
            chave_anthropic="chave-anthropic",
            chave_openai="chave-openai",
        )
        with (
            patch.object(modelos, "obter_configuracao", return_value=configuracao),
            patch.object(
                modelos,
                "_chamar_provedor",
                side_effect=[OSError(), "resposta alternativa"],
            ) as chamar,
        ):
            resposta = modelos.obter_resposta("instrução", "entrada")

        self.assertEqual(resposta, "resposta alternativa")
        self.assertEqual(
            [chamada.args[0] for chamada in chamar.call_args_list],
            ["google", "anthropic"],
        )

    # Expõe o provedor e o modelo que atenderam sem mudar o texto usado pela rota.
    def test_resposta_detalhada_informa_provedor_modelo_e_texto(self):
        configuracao = SimpleNamespace(
            chave_google="chave-google",
            chave_anthropic=None,
            chave_openai=None,
        )
        with (
            patch.object(modelos, "obter_configuracao", return_value=configuracao),
            patch.object(
                modelos,
                "_chamar_provedor",
                return_value="Olá!",
            ),
        ):
            resposta = modelos.obter_resposta_detalhada("instrução", "entrada")

        self.assertEqual(resposta.provider, "Google")
        self.assertEqual(resposta.model, "gemini-3.8-flash")
        self.assertEqual(resposta.text, "Olá!")

    # Confirma que a cadeia alcança o último provedor antes de declarar indisponibilidade.
    def test_tenta_openai_quando_google_e_anthropic_falham(self):
        configuracao = SimpleNamespace(
            chave_google="chave-google",
            chave_anthropic="chave-anthropic",
            chave_openai="chave-openai",
        )
        with (
            patch.object(modelos, "obter_configuracao", return_value=configuracao),
            patch.object(
                modelos,
                "_chamar_provedor",
                side_effect=[OSError(), OSError(), OSError()],
            ) as chamar,
            self.assertRaisesRegex(modelos.ErroProvedoresIA, "OpenAI"),
        ):
            modelos.obter_resposta("instrução", "entrada")

        self.assertEqual(
            [chamada.args[0] for chamada in chamar.call_args_list],
            ["google", "anthropic", "openai"],
        )

    # Evita mascarar a falta total de credenciais como uma resposta de sucesso.
    def test_sem_chaves_informa_configuracao_ausente(self):
        configuracao = SimpleNamespace(
            chave_google=None,
            chave_anthropic=None,
            chave_openai=None,
        )
        with (
            patch.object(modelos, "obter_configuracao", return_value=configuracao),
            self.assertRaises(modelos.ErroProvedoresIA),
        ):
            modelos.obter_resposta("instrução", "entrada")


class TestDadosParaSugestao(unittest.TestCase):
    # Limita o contexto enviado ao modelo e preserva apenas sinais relevantes à decisão.
    def test_prepara_eventos_sem_imagem_ideia_ou_dados_pessoais(self):
        tatuagens = [
            {
                "id": 17,
                "cliente_id": 99,
                "ideia": "conteúdo privado",
                "imagem_referencia": "imagem privada",
                "etapa": "em sessões",
                "passos": [
                    {
                        "id": 1,
                        "tipo": "sessao",
                        "data": date(2026, 11, 12),
                        "horario": time(14, 30),
                        "situacao": "agendada",
                        "observacao": "nota privada",
                    },
                ],
            }
        ]

        projetos = preparar_projetos_para_sugestao(tatuagens)

        self.assertEqual(
            projetos,
            [
                {
                    "codigo": "P-17",
                    "etapa_atual": "em sessões",
                    "historico_recente": [
                        {"evento": "sessao", "data": "2026-11-12"}
                    ],
                    "proxima_acao_pendente": None,
                    "compromissos_prazos": ["2026-11-12 às 14:30"],
                }
            ],
        )

    # Não envia chamadas à API quando não há projetos autorizados para sugerir.
    def test_lista_vazia_nao_consulta_provedores(self):
        with patch("ia.sugestao.obter_resposta") as obter_resposta:
            resposta = gerar_sugestao([])

        obter_resposta.assert_not_called()
        self.assertIn("Não há projetos", resposta)


class TestFerramentasIA(unittest.TestCase):
    # Confirma que a tool conta dias corridos e informa prazos vencidos como negativos.
    def test_dias_ate_prazo_futuro_e_vencido(self):
        hoje = date(2026, 11, 10)
        with patch("ia.ferramentas.date") as data_falsa:
            data_falsa.today.return_value = hoje
            data_falsa.fromisoformat.side_effect = date.fromisoformat

            self.assertEqual(dias_ate("2026-11-15"), 5)
            self.assertEqual(dias_ate("2026-11-08"), -2)

    # Mantém no catálogo somente as funções selecionadas para esta funcionalidade.
    def test_catalogo_contem_dias_ate(self):
        self.assertEqual(FERRAMENTAS, [dias_ate])
