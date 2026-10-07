import hashlib
import hmac
import secrets


ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000
TAMANHO_SALT = 16


def senha_esta_hasheada(valor: str | None) -> bool:
    return isinstance(valor, str) and valor.startswith(f"{ALGORITMO}$")


def hashear_senha(senha: str) -> str:
    salt = secrets.token_bytes(TAMANHO_SALT)
    derivacao = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, ITERACOES
    )
    return f"{ALGORITMO}${ITERACOES}${salt.hex()}${derivacao.hex()}"


def verificar_senha(senha: str, senha_armazenada: str | None) -> bool:
    if not senha_esta_hasheada(senha_armazenada):
        return False

    try:
        algoritmo, iteracoes_texto, salt_texto, derivacao_esperada = senha_armazenada.split("$")
        iteracoes = int(iteracoes_texto)
        salt = bytes.fromhex(salt_texto)
        derivacao_esperada_bytes = bytes.fromhex(derivacao_esperada)
    except (ValueError, TypeError):
        return False

    if algoritmo != ALGORITMO or not 100_000 <= iteracoes <= 2_000_000:
        return False

    derivacao = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, iteracoes
    )
    return hmac.compare_digest(derivacao, derivacao_esperada_bytes)