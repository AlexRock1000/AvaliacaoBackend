import base64
import binascii
import re


TAMANHO_MAXIMO_IMAGEM_BYTES = 5 * 1024 * 1024
TAMANHO_MAXIMO_DATA_URL = 128 + 4 * ((TAMANHO_MAXIMO_IMAGEM_BYTES + 2) // 3)


def validar_imagem_codificada(valor: str | None) -> str | None:
    """Valida data URLs de imagem e limita o conteúdo decodificado a 5 MB."""
    if valor is None:
        return None
    if len(valor) > TAMANHO_MAXIMO_DATA_URL:
        raise ValueError("A imagem deve ter no máximo 5 MB.")

    correspondencia = re.fullmatch(
        r"data:image/[A-Za-z0-9.+-]+;base64,([A-Za-z0-9+/]*={0,2})",
        valor,
    )
    if correspondencia is None or not correspondencia.group(1):
        raise ValueError("Envie uma imagem codificada em base64.")

    try:
        conteudo = base64.b64decode(correspondencia.group(1), validate=True)
    except (binascii.Error, ValueError) as erro:
        raise ValueError("Envie uma imagem codificada em base64 válida.") from erro

    if not conteudo:
        raise ValueError("A imagem não pode estar vazia.")
    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM_BYTES:
        raise ValueError("A imagem deve ter no máximo 5 MB.")
    return valor
