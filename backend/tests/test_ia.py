import unittest
from datetime import date, time
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ia import modelos
from ia.ferramentas import FERRAMENTAS, dias_ate, executar_ferramenta
from ia.sugestao import gerar_sugestao
from servicos.ia import preparar_projetos_para_sugestao


class TestFallbackIA(unittest.TestCase):
    # Confirmar os três provedores e a ordem do fallback sem chamadas externas.
    def test_monta_gemini_openrouter_claude_com_fallback(self):
        configuracao = SimpleNamespace(
            chave_do_gemini="gemini-ficticia",
            chave_do_openrouter="openrouter-ficticia",
            chave_do_claude="claude-ficticia",
        )
        gemini = SimpleNamespace()
        openrouter = SimpleNamespace()
        claude = SimpleNamespace()
        llm = object()
        with (
            patch.object(
                modelos,
                "LLM",
                side_effect=[gemini, openrouter, claude],
            ) as criar,
            patch.object(gemini, "with_fallback", return_value=llm) as fallback,
        ):
            provedores = modelos.criar_provedores(configuracao)

        self.assertEqual(provedores, (gemini, openrouter, claude, llm))
        self.assertEqual(
            [chamada.args for chamada in criar.call_args_list],
            [
                ("gemini", modelos.MODELO_GEMINI),
                ("openrouter", modelos.MODELO_OPENROUTER),
                ("anthropic", modelos.MODELO_CLAUDE),
            ],
        )
        self.assertEqual(
            [chamada.kwargs["api_key"] for chamada in criar.call_args_list],
            ["gemini-ficticia", "openrouter-ficticia", "claude-ficticia"],
        )
        fallback.assert_called_once_with(openrouter, claude)

    # Encaminhar a entrada e a instrução ao Jangada e devolver o texto recebido.
    def test_obter_resposta_usa_llm_com_instrucoes(self):
        resposta_modelo = SimpleNamespace(
            text="Sugestão fictícia.",
            provider="OpenRouter",
            model="openrouter/free",
        )
        llm = SimpleNamespace(
            complete=Mock(return_value=resposta_modelo)
        )
        configuracao = SimpleNamespace(
            chave_do_gemini="gemini-ficticia",
            chave_do_openrouter="openrouter-ficticia",
            chave_do_claude="claude-ficticia",
        )
        with (
            patch.object(modelos, "obter_configuracao", return_value=configuracao),
            patch.object(
                modelos,
                "criar_provedores",
                return_value=(None, None, None, llm),
            ),
        ):
            texto = modelos.obter_resposta("instrução fictícia", "entrada fictícia")

        self.assertEqual(texto, "Sugestão fictícia.")
        llm.complete.assert_called_once_with(
            "entrada fictícia", system="instrução fictícia"
        )

    # Expor o provider e o modelo que responderam para o teste manual de fallback.
    def test_resposta_detalhada_informa_provedor_e_modelo(self):
        resposta_modelo = SimpleNamespace(
            text="Resposta fictícia.",
            provider="OpenRouter",
            model="openrouter/free",
        )
        llm = SimpleNamespace(
            complete=Mock(return_value=resposta_modelo)
        )
        with (
            patch.object(
                modelos,
                "obter_configuracao",
                return_value=SimpleNamespace(
                    chave_do_gemini="gemini-ficticia",
                    chave_do_openrouter="openrouter-ficticia",
                    chave_do_claude="claude-ficticia",
                ),
            ),
            patch.object(
                modelos,
                "criar_provedores",
                return_value=(None, None, None, llm),
            ),
        ):
            resposta = modelos.obter_resposta_detalhada(
                "instrução fictícia", "entrada fictícia"
            )

        self.assertEqual(resposta.provider, "OpenRouter")
        self.assertEqual(resposta.model, "openrouter/free")
        self.assertEqual(resposta.text, "Resposta fictícia.")


class TestDadosParaSugestao(unittest.TestCase):
    # Limitar o contexto enviado ao modelo e excluir informações privadas do projeto.
    def test_prepara_eventos_sem_imagem_ideia_ou_dados_pessoais(self):
        tatuagens = [
            {
                "id": 17,
                "cliente_id": 99,
                "ideia": "conteúdo privado fictício",
                "imagem_referencia": "imagem privada fictícia",
                "etapa": "em sessões",
                "passos": [
                    {
                        "id": 1,
                        "tipo": "sessao",
                        "data": date(2026, 11, 12),
                        "horario": time(14, 30),
                        "situacao": "agendada",
                        "observacao": "nota privada fictícia",
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

    # Evitar chamar o modelo quando não há projetos autorizados para sugerir.
    def test_lista_vazia_nao_consulta_provedores(self):
        with patch("ia.sugestao.obter_resposta") as obter_resposta:
            resposta = gerar_sugestao([])

        obter_resposta.assert_not_called()
        self.assertIn("Não há projetos", resposta)


class TestFerramentasIA(unittest.TestCase):
    # Calcular dias corridos e representar datas vencidas com valores negativos.
    def test_dias_ate_prazo_futuro_e_vencido(self):
        hoje = date(2026, 11, 10)
        with patch("ia.ferramentas.date") as data_falsa:
            data_falsa.today.return_value = hoje

            self.assertEqual(dias_ate("15-11-2026"), 5)
            self.assertEqual(dias_ate("08-11-2026"), -2)

    # Recusar datas que não respeitam o formato acordado para a ferramenta.
    def test_dias_ate_rejeita_formato_invalido(self):
        with self.assertRaises(ValueError):
            dias_ate("2026-11-15")

    # Restringir a execução ao nome autorizado e aos argumentos esperados.
    def test_ferramenta_rejeita_nome_e_argumentos_nao_autorizados(self):
        with self.assertRaisesRegex(ValueError, "não está autorizada"):
            executar_ferramenta("consultar_banco", {})
        with self.assertRaisesRegex(ValueError, "exige somente prazo"):
            executar_ferramenta(
                "dias_ate", {"prazo": "15-11-2026", "extra": True}
            )

    # Manter no catálogo somente a função selecionada para esta funcionalidade.
    def test_catalogo_contem_dias_ate(self):
        self.assertEqual(FERRAMENTAS, [dias_ate])
