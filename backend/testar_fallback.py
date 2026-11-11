from ia.modelos import ErroProvedoresIA, obter_resposta_detalhada


try:
    resposta = obter_resposta_detalhada(
        "Responda brevemente.",
        "Diga olá em uma frase.",
    )
except ErroProvedoresIA as erro:
    raise SystemExit(f"Nenhum provedor configurado conseguiu responder: {erro}") from erro

print(resposta.provider, resposta.model, "respondeu:", resposta.text)
