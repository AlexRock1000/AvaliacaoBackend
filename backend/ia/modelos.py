import os
from dataclasses import dataclass

# Evita uma segunda leitura automática do .env pelo Jangada; a aplicação centraliza
# o carregamento das configurações em configuracao.py.
os.environ.setdefault("JANGADA_NO_DOTENV", "1")

from configuracao import Configuracao, obter_configuracao
from jangada_ai import LLM, errors


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


# Preserva a interface usada pela funcionalidade atual até ela passar a usar Agent.
def obter_resposta(instrucao: str, entrada: str) -> str:
    configuracao = obter_configuracao()
    _, _, _, llm = criar_provedores(configuracao)
    try:
        resposta = llm.complete(entrada, system=instrucao)
    except errors.LLMError as erro:
        raise ErroProvedoresIA(
            "Nenhum provedor de IA conseguiu responder."
        ) from erro
    return resposta.text


# Expõe o provedor efetivamente utilizado sem mudar a resposta esperada pela rota.
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
