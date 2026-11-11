from datetime import date, datetime, time
from typing import Any


# Mantém somente eventos recentes e compromissos explícitos no contexto enviado ao modelo.
def preparar_projetos_para_sugestao(
    tatuagens: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    projetos = []
    for tatuagem in tatuagens:
        passos = sorted(tatuagem.get("passos", []), key=lambda passo: passo["id"])
        historico = [
            {
                "evento": passo["tipo"],
                "data": _formatar_data(passo.get("data")),
            }
            for passo in passos[-3:]
        ]
        compromissos = []
        for passo in passos:
            if (
                passo["tipo"] in {"sessao", "retoque_combinado"}
                and (passo.get("situacao") or "agendada") == "agendada"
                and passo.get("data") is not None
            ):
                compromisso = _formatar_data(passo["data"])
                if compromisso is None:
                    continue
                if passo.get("horario") is not None:
                    compromisso += f" às {_formatar_horario(passo['horario'])}"
                compromissos.append(compromisso)

        projetos.append(
            {
                "codigo": f"P-{tatuagem['id']}",
                "etapa_atual": tatuagem["etapa"],
                "historico_recente": historico,
                "proxima_acao_pendente": None,
                "compromissos_prazos": compromissos,
            }
        )
    return projetos


# Padroniza datas sem depender de elas virem do banco como texto ou objeto de data.
def _formatar_data(valor: date | datetime | str | None) -> str | None:
    if valor is None:
        return None
    return valor.isoformat() if isinstance(valor, (date, datetime)) else str(valor)


# Exibe horários como texto sem incluir detalhes internos do banco no payload.
def _formatar_horario(valor: time | str) -> str:
    return valor.strftime("%H:%M") if isinstance(valor, time) else str(valor)
