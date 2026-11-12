import sys
import unittest
from datetime import date, time
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from ia import modelos
from ia.ferramentas import FERRAMENTAS, dias_ate
from ia.sugestao import gerar_sugestao, preparar_projetos_para_sugestao


class TestFallbackIA(unittest.TestCase):
    # Confirmar os três provedores e a ordem do fallback sem chamadas externas.
    def test_monta_gemini_openrouter_claude_com_fallback(self):
        configuracao = SimpleNamespace(
            chave_do_gemini="gemini-ficticia",
            chave_do_openrouter="openrouter-ficticia",
            chave_do_claude="claude-ficticia",
        )
        gemini = Mock()
        openrouter = Mock()
        claude = Mock()
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
    def test_cria_agente_com_instrucao_tools_e_limite(self):
        resultado_agente = SimpleNamespace(
            text="Sugestão fictícia.",
            stopped_by_limit=False,
        )
        agente = Mock()
        agente.run.return_value = resultado_agente
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
                return_value=(None, None, None, Mock()),
            ),
            patch.object(modelos, "Agent", return_value=agente) as criar_agente,
        ):
            resposta = modelos.obter_resposta_com_ferramentas(
                "instrução fictícia",
                "entrada fictícia",
                FERRAMENTAS,
            )

        self.assertIs(resposta, resultado_agente)
        criar_agente.assert_called_once()
        self.assertEqual(criar_agente.call_args.kwargs["goal"], "instrução fictícia")
        self.assertEqual(criar_agente.call_args.kwargs["tools"], FERRAMENTAS)
        self.assertEqual(
            criar_agente.call_args.kwargs["max_iterations"],
            modelos.MAX_CHAMADAS_FERRAMENTAS + 1,
        )
        agente.run.assert_called_once_with("entrada fictícia")
        permitir_chamada = criar_agente.call_args.kwargs["on_tool_call"]
        self.assertTrue(
            all(
                permitir_chamada(SimpleNamespace())
                for _ in range(modelos.MAX_CHAMADAS_FERRAMENTAS)
            )
        )
        self.assertFalse(permitir_chamada(SimpleNamespace()))

    # Não aceitar uma resposta parcial se o Agent atingir o limite de iterações.
    def test_limite_de_iteracoes_vira_erro_explicito(self):
        agente = Mock()
        agente.run.return_value = SimpleNamespace(
            text="Resposta parcial fictícia.",
            stopped_by_limit=True,
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
                return_value=(None, None, None, Mock()),
            ),
            patch.object(modelos, "Agent", return_value=agente),
            self.assertRaisesRegex(
                modelos.ErroProvedoresIA, "não concluiu a resposta"
            ),
        ):
            modelos.obter_resposta_com_ferramentas(
                "instrução fictícia",
                "entrada fictícia",
                FERRAMENTAS,
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

    # Confirmar que o Jangada consegue gerar o esquema da tool Python escolhida.
    def test_jangada_aceita_tool_de_calculo(self):
        agente = modelos.Agent(
            Mock(),
            role="assistente fictício",
            goal="Calcular um prazo fictício.",
            tools=FERRAMENTAS,
            max_iterations=4,
        )

        self.assertEqual([ferramenta.name for ferramenta in agente._tools], ["dias_ate"])


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
        with patch("ia.sugestao.obter_resposta_com_ferramentas") as obter_resposta:
            resposta = gerar_sugestao([])

        obter_resposta.assert_not_called()
        self.assertIn("Não há projetos", resposta)

    # Enviar somente o payload fictício e a tool aprovada ao Agent.
    def test_gerar_sugestao_envia_entrada_e_tool(self):
        tatuagem = {"id": 123, "etapa": "sessão agendada", "passos": []}
        resposta = SimpleNamespace(text="Sugestão fictícia.")
        with patch(
            "ia.sugestao.obter_resposta_com_ferramentas",
            return_value=resposta,
        ) as chamar_agente:
            sugestao = gerar_sugestao([tatuagem])

        self.assertEqual(sugestao, "Sugestão fictícia.")
        entrada = chamar_agente.call_args.args[1]
        self.assertIn('"P-123"', entrada)
        self.assertEqual(chamar_agente.call_args.args[2], FERRAMENTAS)


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

    # Manter no catálogo somente a função selecionada para esta funcionalidade.
    def test_catalogo_contem_dias_ate(self):
        self.assertEqual(FERRAMENTAS, [dias_ate])


class TestRotaSugestaoIA(unittest.TestCase):
    # Isolar o import da rota para não inicializar o repositório nem exigir banco real.
    @classmethod
    def setUpClass(cls):
        servico_falso = ModuleType("servicos.tatuagem")
        servico_falso.listar_tatuagens = Mock()
        with patch.dict(sys.modules, {"servicos.tatuagem": servico_falso}):
            from rotas import ia as rota_ia

        cls.rota_ia = rota_ia

    # Garantir que a rota envia ao pacote de IA apenas os registros autorizados.
    def test_rota_devolve_sugestao_sem_persistir(self):
        tatuagens = [{"id": 123, "etapa": "pedida", "passos": []}]
        with (
            patch.object(
                self.rota_ia,
                "usuario_tem_permissao",
                return_value=False,
            ),
            patch.object(
                self.rota_ia.servico_tatuagem,
                "listar_tatuagens",
                return_value=tatuagens,
            ) as listar,
            patch.object(
                self.rota_ia,
                "gerar_sugestao",
                return_value="Sugestão fictícia.",
            ) as gerar,
        ):
            resposta = self.rota_ia.sugerir_prioridade({"id": 77})

        self.assertEqual(resposta, {"sugestao": "Sugestão fictícia."})
        listar.assert_called_once_with(cliente_id=77)
        gerar.assert_called_once_with(tatuagens)

    # Traduzir falhas dos provedores em 503 sem expor detalhes técnicos.
    def test_rota_responde_503_quando_provedores_falham(self):
        with (
            patch.object(
                self.rota_ia,
                "usuario_tem_permissao",
                return_value=False,
            ),
            patch.object(
                self.rota_ia.servico_tatuagem,
                "listar_tatuagens",
                return_value=[{"id": 123, "etapa": "pedida", "passos": []}],
            ),
            patch.object(
                self.rota_ia,
                "gerar_sugestao",
                side_effect=modelos.ErroProvedoresIA("falha técnica fictícia"),
            ),
        ):
            try:
                self.rota_ia.sugerir_prioridade({"id": 77})
            except Exception as erro:
                self.assertEqual(type(erro).__name__, "HTTPException")
                self.assertEqual(erro.status_code, 503)
                self.assertEqual(erro.detail, "Sugestão indisponível agora.")
            else:
                self.fail("A rota deveria responder com HTTP 503.")
