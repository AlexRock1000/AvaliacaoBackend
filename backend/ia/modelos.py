import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from configuracao import obter_configuracao
from ia.ferramentas import ESQUEMA_FERRAMENTAS, executar_ferramenta


MAX_CHAMADAS_FERRAMENTAS = 3


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


def _definicoes_ferramentas(provedor: str) -> list[dict]:
    definicoes = []
    for nome, esquema in ESQUEMA_FERRAMENTAS.items():
        if provedor == "google":
            definicoes.append(
                {
                    "name": nome,
                    "description": esquema["description"],
                    "parameters": esquema["parameters"],
                }
            )
        elif provedor == "anthropic":
            definicoes.append(
                {
                    "name": nome,
                    "description": esquema["description"],
                    "input_schema": esquema["parameters"],
                }
            )
        else:
            definicoes.append(
                {
                    "type": "function",
                    "function": {
                        "name": nome,
                        "description": esquema["description"],
                        "parameters": esquema["parameters"],
                    },
                }
            )
    return definicoes


def _solicitar_turno_com_ferramentas(
    provedor: str,
    chave: str,
    instrucao: str,
    historico: list[dict],
) -> dict:
    modelo = MODELOS[provedor]
    ferramentas = _definicoes_ferramentas(provedor)
    if provedor == "google":
        dados = {
            "systemInstruction": {"parts": [{"text": instrucao}]},
            "contents": historico,
            "tools": [{"functionDeclarations": ferramentas}],
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{modelo}:generateContent"
        )
        cabecalhos = {"x-goog-api-key": chave}
    elif provedor == "anthropic":
        dados = {
            "model": modelo,
            "max_tokens": 1200,
            "system": instrucao,
            "messages": historico,
            "tools": ferramentas,
        }
        url = "https://api.anthropic.com/v1/messages"
        cabecalhos = {"x-api-key": chave, "anthropic-version": "2023-06-01"}
    else:
        dados = {
            "model": modelo,
            "messages": [{"role": "system", "content": instrucao}, *historico],
            "tools": ferramentas,
            "tool_choice": "auto",
        }
        url = "https://api.openai.com/v1/chat/completions"
        cabecalhos = {"Authorization": f"Bearer {chave}"}
    return _solicitar_json(url, cabecalhos, dados)


def _executar_chamada_ferramenta(chamada: dict, orcamento: list[int]) -> int | str:
    if orcamento[0] <= 0:
        raise ValueError("O limite de chamadas de ferramentas foi atingido.")
    orcamento[0] -= 1
    try:
        return executar_ferramenta(chamada["name"], chamada["arguments"])
    except ValueError as erro:
        return f"Erro da ferramenta: {erro}"


def _validar_limite_ferramentas(chamadas: list[dict], orcamento: list[int]) -> None:
    if len(chamadas) > orcamento[0]:
        raise ValueError("O limite de chamadas de ferramentas foi atingido.")


def _processar_turno_com_ferramentas(
    provedor: str,
    resposta: dict,
    historico: list[dict],
    orcamento: list[int],
) -> str | None:
    if provedor == "google":
        partes = resposta["candidates"][0]["content"]["parts"]
        chamadas = [
            {
                "name": parte["functionCall"]["name"],
                "arguments": parte["functionCall"].get("args", {}),
            }
            for parte in partes
            if "functionCall" in parte
        ]
        _validar_limite_ferramentas(chamadas, orcamento)
        historico.append({"role": "model", "parts": partes})
        resultados = [
            {
                "functionResponse": {
                    "name": chamada["name"],
                    "response": {
                        "result": _executar_chamada_ferramenta(
                            chamada, orcamento
                        )
                    },
                }
            }
            for chamada in chamadas
        ]
        if resultados:
            historico.append({"role": "user", "parts": resultados})
        texto = "\n".join(parte["text"] for parte in partes if "text" in parte)
    elif provedor == "anthropic":
        blocos = resposta["content"]
        chamadas = [
            {
                "id": bloco["id"],
                "name": bloco["name"],
                "arguments": bloco["input"],
            }
            for bloco in blocos
            if bloco.get("type") == "tool_use"
        ]
        _validar_limite_ferramentas(chamadas, orcamento)
        historico.append({"role": "assistant", "content": blocos})
        resultados = [
            {
                "type": "tool_result",
                "tool_use_id": chamada["id"],
                "content": json.dumps(
                    {
                        "result": _executar_chamada_ferramenta(
                            chamada, orcamento
                        )
                    },
                    ensure_ascii=False,
                ),
            }
            for chamada in chamadas
        ]
        if resultados:
            historico.append({"role": "user", "content": resultados})
        texto = "\n".join(
            bloco["text"] for bloco in blocos if bloco.get("type") == "text"
        )
    else:
        mensagem = resposta["choices"][0]["message"]
        chamadas = [
            {
                "id": chamada["id"],
                "name": chamada["function"]["name"],
                "arguments": json.loads(chamada["function"]["arguments"]),
            }
            for chamada in mensagem.get("tool_calls", [])
        ]
        _validar_limite_ferramentas(chamadas, orcamento)
        historico.append(mensagem)
        for chamada in chamadas:
            resultado = _executar_chamada_ferramenta(
                chamada, orcamento
            )
            historico.append(
                {
                    "role": "tool",
                    "tool_call_id": chamada["id"],
                    "content": json.dumps({"result": resultado}, ensure_ascii=False),
                }
            )
        texto = mensagem.get("content") or ""

    if chamadas:
        return None
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("O provedor retornou uma resposta vazia.")
    return texto.strip()


def _chamar_provedor_com_ferramentas(
    provedor: str,
    chave: str,
    instrucao: str,
    entrada: str,
    orcamento: list[int],
) -> str:
    if provedor == "google":
        historico = [{"role": "user", "parts": [{"text": entrada}]}]
    else:
        historico = [{"role": "user", "content": entrada}]
    while True:
        resposta = _solicitar_turno_com_ferramentas(
            provedor, chave, instrucao, historico
        )
        texto = _processar_turno_com_ferramentas(
            provedor, resposta, historico, orcamento
        )
        if texto is not None:
            return texto


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


def obter_resposta_com_ferramentas(instrucao: str, entrada: str) -> RespostaModelo:
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
    orcamento = [MAX_CHAMADAS_FERRAMENTAS]
    for provedor in provedores_configurados:
        try:
            texto = _chamar_provedor_com_ferramentas(
                provedor, chaves[provedor], instrucao, entrada, orcamento
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
