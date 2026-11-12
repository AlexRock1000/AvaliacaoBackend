import os
from dataclasses import dataclass
from typing import Any, Callable

# Evita uma segunda leitura automática do .env pelo Jangada; a aplicação centraliza
# o carregamento das configurações em configuracao.py.
os.environ.setdefault("JANGADA_NO_DOTENV", "1")

from configuracao import Configuracao, obter_configuracao
from jangada_ai import Agent, LLM, errors


MAX_CHAMADAS_FERRAMENTAS = 3


# Centraliza os identificadores dos modelos usados nesta cadeia de fallback.
MODELO_GEMINI = "gemini-3.8-flash"
MODELO_OPENROUTER = "openrouter/free"
MODELO_CLAUDE = "claude-haiku-4-5-20251001"


# Padroniza a falha final para que a rota possa responder sem expor detalhes técnicos.
class ErroProvedoresIA(RuntimeError):
    """Indica que os provedores configurados não conseguiram gerar uma resposta."""


# Mantém metadados úteis para conferir qual provedor e modelo responderam.
@dataclass(frozen=True)
class RespostaModelo:
    provider: str
    model: str
    text: str


# Monta os três provedores com credenciais explícitas e deixa o Jangada ordenar
# as tentativas e aplicar retry/fallback conforme os erros documentados.
def criar_provedores(configuracao: Configuracao) -> tuple[LLM, LLM, LLM, LLM]:
    gemini = LLM(
        "gemini",
        MODELO_GEMINI,
        api_key=configuracao.chave_do_gemini,
    )
    openrouter = LLM(
        "openrouter",
        MODELO_OPENROUTER,
        api_key=configuracao.chave_do_openrouter,
    )
    claude = LLM(
        "anthropic",
        MODELO_CLAUDE,
        api_key=configuracao.chave_do_claude,
    )
    llm = gemini.with_fallback(openrouter, claude)
    return gemini, openrouter, claude, llm


# Envia a entrada pelo Jangada e converte falhas normalizadas para o contrato da rota.
def obter_resposta_detalhada(instrucao: str, entrada: str) -> RespostaModelo:
    configuracao = obter_configuracao()
    _, _, _, llm = criar_provedores(configuracao)
    try:
        resposta = llm.complete(entrada, system=instrucao)
    except errors.LLMError as erro:
        raise ErroProvedoresIA(
            "Nenhum provedor de IA conseguiu responder."
        ) from erro
    return RespostaModelo(
        provider=resposta.provider,
        model=resposta.model,
        text=resposta.text,
    )


# Executar o ciclo síncrono do Agent com as ferramentas permitidas e limite de uso.
def obter_resposta_com_ferramentas(
    instrucao: str,
    entrada: str,
    ferramentas: list[Callable[..., Any]],
) -> Any:
    configuracao = obter_configuracao()
    _, _, _, llm = criar_provedores(configuracao)
    chamadas = 0

    # Bloquear chamadas além da cota local sem executar ferramentas adicionais.
    def limitar_chamadas(chamada: Any) -> bool:
        nonlocal chamadas
        if chamadas >= MAX_CHAMADAS_FERRAMENTAS:
            return False
        chamadas += 1
        return True

    agente = Agent(
        llm,
        role="assistente de apoio à priorização de projetos de tatuagem",
        goal=instrucao,
        tools=ferramentas,
        on_tool_call=limitar_chamadas,
        max_iterations=MAX_CHAMADAS_FERRAMENTAS + 1,
    )
    try:
        resposta = agente.run(entrada)
    except errors.LLMError as erro:
        raise ErroProvedoresIA(
            "Nenhum provedor de IA conseguiu responder."
        ) from erro
    if resposta.stopped_by_limit:
        raise ErroProvedoresIA(
            "O agente não concluiu a resposta dentro do limite de etapas."
        )
    if not resposta.text.strip():
        raise ErroProvedoresIA("O agente retornou uma resposta vazia.")
    return resposta


# Preservar a interface simples usada pela função de sugestão atual.
def obter_resposta(instrucao: str, entrada: str) -> str:
    return obter_resposta_detalhada(instrucao, entrada).text
