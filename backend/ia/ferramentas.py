from datetime import date


# Calcula dias até um prazo explícito para apoiar a comparação dos projetos.
def dias_ate(prazo: str) -> int:
    """Conta dias de hoje até o prazo, informado no formato DD-MM-AAAA."""
    return (date.fromisoformat(prazo) - date.today()).days


FERRAMENTAS = [dias_ate]
