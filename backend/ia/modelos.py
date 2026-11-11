import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from configuracao import obter_configuracao


ORDEM_PROVEDORES = ("google", "anthropic", "openai")
MODELOS = {
    "google": "gemini-3.8-flash",
    "anthropic": "claude-haiku-4-5",
    "openai": "gpt-4o-mini",
}
NOMES_PROVEDORES = {
    "google": "Google",
    "anthropic": "Anthropic",
    "openai": "OpenAI",
}


class ErroProvedoresIA(RuntimeError):
    """Informa que nenhum dos provedores configurados conseguiu responder."""


@dataclass(frozen=True)
class RespostaModelo:
    provider: str
    model: str
    text: str


# Envia um pedido JSON à API sem incluir credenciais no endereço da requisição.
def _solicitar_json(url: str, cabecalhos: dict, dados: dict) -> dict:
    corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
    requisicao = Request(
        url,
        data=corpo,
        headers={"Content-Type": "application/json", **cabecalhos},
        method="POST",
    )
    with urlopen(requisicao, timeout=30) as resposta:
        resultado = json.loads(resposta.read().decode("utf-8"))
    if not isinstance(resultado, dict):
        raise ValueError("A resposta do provedor não é um objeto JSON.")
    return resultado


# Converte a resposta de cada API para texto, recusando formatos incompletos.
def _extrair_texto(provedor: str, resposta: dict) -> str:
    if provedor == "google":
        partes = resposta["candidates"][0]["content"]["parts"]
        texto = "\n".join(parte["text"] for parte in partes if "text" in parte)
    elif provedor == "anthropic":
        texto = "\n".join(
            bloco["text"] for bloco in resposta["content"] if bloco.get("type") == "text"
        )
    else:
        texto = resposta["choices"][0]["message"]["content"]

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("O provedor retornou uma resposta vazia.")
    return texto.strip()


# Chama um provedor específico usando a autenticação e o formato exigidos por sua API.
def _chamar_provedor(provedor: str, chave: str, instrucao: str, entrada: str) -> str:
    modelo = MODELOS[provedor]
    if provedor == "google":
        resposta = _solicitar_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
            {"x-goog-api-key": chave},
            {
                "systemInstruction": {"parts": [{"text": instrucao}]},
                "contents": [{"role": "user", "parts": [{"text": entrada}]}],
            },
        )
    elif provedor == "anthropic":
        resposta = _solicitar_json(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": chave, "anthropic-version": "2023-06-01"},
            {
                "model": modelo,
                "max_tokens": 1200,
                "system": instrucao,
                "messages": [{"role": "user", "content": entrada}],
            },
        )
    else:
        resposta = _solicitar_json(
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {chave}"},
            {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": instrucao},
                    {"role": "user", "content": entrada},
                ],
            },
        )
    return _extrair_texto(provedor, resposta)


# Tenta os provedores configurados e informa qual deles produziu a resposta.
def obter_resposta_detalhada(instrucao: str, entrada: str) -> RespostaModelo:
    configuracao = obter_configuracao()
    chaves = {
        "google": configuracao.chave_google,
        "anthropic": configuracao.chave_anthropic,
        "openai": configuracao.chave_openai,
    }
    provedores_configurados = [
        provedor for provedor in ORDEM_PROVEDORES if chaves[provedor]
    ]
    if not provedores_configurados:
        raise ErroProvedoresIA(
            "Nenhum provedor de IA está configurado. Defina GOOGLE_API_KEY, "
            "ANTHROPIC_API_KEY ou OPENAI_API_KEY."
        )

    falhas = []
    for provedor in provedores_configurados:
        try:
            texto = _chamar_provedor(
                provedor, chaves[provedor], instrucao, entrada
            )
            return RespostaModelo(
                provider=NOMES_PROVEDORES[provedor],
                model=MODELOS[provedor],
                text=texto,
            )
        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            ValueError,
            KeyError,
            IndexError,
            TypeError,
        ) as erro:
            if isinstance(erro, HTTPError):
                detalhe = f"HTTP {erro.code}"
            else:
                detalhe = type(erro).__name__
            falhas.append(f"{NOMES_PROVEDORES[provedor]} ({detalhe})")

    raise ErroProvedoresIA(
        "Nenhum provedor de IA respondeu com sucesso: " + "; ".join(falhas)
    )


# Preserva a interface simples usada pela funcionalidade de sugestão da API.
def obter_resposta(instrucao: str, entrada: str) -> str:
    return obter_resposta_detalhada(instrucao, entrada).text
