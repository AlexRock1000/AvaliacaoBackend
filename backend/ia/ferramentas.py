from datetime import date, datetime


# Calcular dias corridos até um compromisso já informado, sem ler nem alterar dados.
def dias_ate(prazo: str) -> int:
    """Calcular dias até uma data explícita no formato DD-MM-AAAA."""
    data_prazo = datetime.strptime(prazo, "%d-%m-%Y").date()
    if data_prazo.strftime("%d-%m-%Y") != prazo:
        raise ValueError("O prazo deve estar no formato DD-MM-AAAA.")
    return (data_prazo - date.today()).days


# Entregar ao Agent somente a ferramenta de cálculo escolhida para a priorização.
FERRAMENTAS = [dias_ate]
