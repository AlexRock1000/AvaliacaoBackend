import unittest
from datetime import date, time
from types import SimpleNamespace
from unittest.mock import patch

from ia.ferramentas import FERRAMENTAS, dias_ate, executar_ferramenta
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
        with patch("ia.sugestao.obter_resposta_com_ferramentas") as obter_resposta:
            resposta = gerar_sugestao([])

        obter_resposta.assert_not_called()
        self.assertIn("Não há projetos", resposta)


class TestFerramentasIA(unittest.TestCase):
    # Confirma que a tool conta dias corridos e informa prazos vencidos como negativos.
    def test_dias_ate_prazo_futuro_e_vencido(self):
        hoje = date(2026, 11, 10)
        with patch("ia.ferramentas.date") as data_falsa:
            data_falsa.today.return_value = hoje

            self.assertEqual(dias_ate("15-11-2026"), 5)
            self.assertEqual(dias_ate("08-11-2026"), -2)

    def test_dias_ate_rejeita_formato_invalido(self):
        with self.assertRaises(ValueError):
            dias_ate("2026-11-15")

    def test_ferramenta_rejeita_nome_e_argumentos_nao_autorizados(self):
        with self.assertRaisesRegex(ValueError, "não está autorizada"):
            executar_ferramenta("consultar_banco", {})
        with self.assertRaisesRegex(ValueError, "exige somente prazo"):
            executar_ferramenta(
                "dias_ate", {"prazo": "15-11-2026", "extra": True}
            )

    # Mantém no catálogo somente as funções selecionadas para esta funcionalidade.
    def test_catalogo_contem_dias_ate(self):
        self.assertEqual(FERRAMENTAS, [dias_ate])


class TestAgenteIA(unittest.TestCase):
    def test_processa_chamada_de_ferramenta_openai_e_retorno_final(self):
        configuracao = SimpleNamespace(
            chave_google=None,
            chave_anthropic=None,
            chave_openai="chave-openai",
        )
        respostas = [
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "function": {
                                        "name": "dias_ate",
                                        "arguments": '{"prazo":"15-11-2026"}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Faltam 5 dias.",
                        }
                    }
                ]
            },
        ]
        with (
            patch.object(modelos, "obter_configuracao", return_value=configuracao),
            patch.object(modelos, "_solicitar_json", side_effect=respostas) as solicitar,
            patch("ia.ferramentas.date") as data_falsa,
        ):
            data_falsa.today.return_value = date(2026, 11, 10)
            resultado = modelos.obter_resposta_com_ferramentas(
                "instrução", "entrada"
            )

        self.assertEqual(resultado.text, "Faltam 5 dias.")
        self.assertEqual(solicitar.call_count, 2)
        self.assertEqual(
            solicitar.call_args_list[0].args[1]["Authorization"],
            "Bearer chave-openai",
        )
        historico = solicitar.call_args_list[1].args[2]["messages"]
        self.assertEqual(historico[-1]["content"], '{"result": 5}')

    def test_limita_chamadas_de_ferramentas(self):
        chamada = {
            "id": "call-1",
            "name": "dias_ate",
            "arguments": {"prazo": "15-11-2026"},
        }
        resposta = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": f"call-{indice}",
                                "function": {
                                    "name": "dias_ate",
                                    "arguments": '{"prazo":"15-11-2026"}',
                                },
                            }
                            for indice in range(
                                modelos.MAX_CHAMADAS_FERRAMENTAS + 1
                            )
                        ],
                    }
                }
            ]
        }
        orcamento = [modelos.MAX_CHAMADAS_FERRAMENTAS]
        with self.assertRaisesRegex(ValueError, "limite de chamadas"):
            modelos._processar_turno_com_ferramentas(
                "openai",
                resposta,
                [],
                orcamento,
            )
        self.assertEqual(orcamento, [modelos.MAX_CHAMADAS_FERRAMENTAS])
