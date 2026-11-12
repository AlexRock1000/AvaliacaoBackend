from datetime import date, datetime


# Calcula dias até um prazo explícito para apoiar a comparação dos projetos.
def dias_ate(prazo: str) -> int:
    """Conta dias de hoje até o prazo, informado no formato DD-MM-AAAA"""
    data_prazo = datetime.strptime(prazo, "%d-%m-%Y").date()
    if data_prazo.strftime("%d-%m-%Y") != prazo:
        raise ValueError("O prazo deve estar no formato DD-MM-AAAA.")
    return (data_prazo - date.today()).days


FERRAMENTAS = [dias_ate]

ESQUEMA_FERRAMENTAS = {
    "dias_ate": {
        "description": "Calcula dias corridos até uma data explícita no formato DD-MM-AAAA.",
        "parameters": {
            "type": "object",
            "properties": {
                "prazo": {
                    "type": "string",
                    "description": "Data no formato DD-MM-AAAA.",
                }
            },
            "required": ["prazo"],
            "additionalProperties": False,
        },
    }
}


def executar_ferramenta(nome: str, argumentos: dict) -> int:
    if nome != "dias_ate":
        raise ValueError(f"A ferramenta '{nome}' não está autorizada.")
    if (
        not isinstance(argumentos, dict)
        or set(argumentos) != {"prazo"}
        or not isinstance(argumentos["prazo"], str)
    ):
        raise ValueError("A ferramenta dias_ate exige somente prazo como texto.")
    return dias_ate(argumentos["prazo"])
