import sys

from configuracao import obter_configuracao
from jangada_ai import LLM, errors

from ia.modelos import ErroProvedoresIA, obter_resposta_detalhada


def testar_primeira_reserva():
    # Forçar um identificador inválido no Gemini apenas nesta execução.
    configuracao = obter_configuracao()
    gemini = LLM(
        "gemini",
        "modelo-inexistente-para-teste",
        api_key=configuracao.chave_do_gemini,
    )
    openrouter = LLM(
        "openrouter",
        "openrouter/free",
        api_key=configuracao.chave_do_openrouter,
    )

    # Isolar o OpenRouter como reserva para não acionar o Claude pago no teste.
    try:
        resposta = gemini.with_fallback(openrouter).complete(
            "Diga olá em uma frase.",
            system="Responda brevemente.",
        )
    except errors.LLMError as erro:
        raise SystemExit(
            f"O teste de fallback não recebeu resposta do Gemini nem do OpenRouter: {erro}"
        ) from erro

    # Mostrar apenas metadados da resposta e o texto fictício do teste.
    print(resposta.provider, resposta.model, "respondeu:", resposta.text)


if "--testar-primeira-reserva" in sys.argv:
    testar_primeira_reserva()
else:
    # Conferir os metadados do provedor que respondeu na configuração normal.
    try:
        resposta = obter_resposta_detalhada(
            "Responda brevemente.",
            "Diga olá em uma frase.",
        )
    except ErroProvedoresIA as erro:
        raise SystemExit(
            f"Nenhum provedor configurado conseguiu responder: {erro}"
        ) from erro

    print(resposta.provider, resposta.model, "respondeu:", resposta.text)
