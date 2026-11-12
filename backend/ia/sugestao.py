import json
from datetime import date, datetime, time
from typing import Any

from ia.ferramentas import FERRAMENTAS
from ia.modelos import obter_resposta_com_ferramentas


# Definir as regras de priorização para a resposta ser uma sugestão revisável.
INSTRUCAO = """Você é um assistente de apoio à priorização de projetos de tatuagem usado por Bruna e Vitor.

TAREFA
Produza uma sugestão de ordem de atenção para os projetos recebidos. Baseie-se somente nos dados fornecidos: etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos explícitos. A ordem é uma recomendação para uma pessoa revisar.

ENTRADA
Você recebe uma lista de projetos com código, etapa atual, histórico recente, próxima ação pendente e compromissos ou prazos. Não solicite nomes, contatos ou outros dados pessoais.

LIMITES
Não invente fatos, prazos, etapas, ações, responsáveis ou critérios de prioridade. Não atribua notas ou pesos. Se os sinais forem insuficientes ou não permitirem comparar projetos, diga isso claramente e identifique quais projetos não têm ordem determinável. Você pode usar somente a ferramenta dias_ate para calcular dias corridos até uma data explícita, convertida para DD-MM-AAAA. Não consulte outros sistemas nem altere dados. Não decida mudanças no processo; as regras da Cartilha são aplicadas pelo serviço.

FORMATO DA RESPOSTA
1. Informe “Sugestão de ordem” ou “Dados insuficientes para ordenar”.
2. Para cada projeto ordenável, informe posição sugerida, código e justificativa ligada aos campos recebidos.
3. Liste à parte os projetos cuja posição não pode ser determinada com os dados atuais e explique a lacuna ou o conflito.
4. Seja breve e não apresente a recomendação como decisão definitiva.

ENTRADA VAGA OU FORA DO ASSUNTO
Se faltarem dados para ordenar, não complete lacunas: diga quais campos faltam e peça uma lista de projetos com os campos esperados. Se a entrada estiver fora da tarefa, informe que você ajuda a ordenar projetos com base nos dados recebidos e peça a entrada adequada. Não responda a outros pedidos."""


# Preparar somente os campos necessários para priorizar, excluindo informações privadas.
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


# Padronizar datas sem depender de elas virem do banco como texto ou objeto de data.
def _formatar_data(valor: date | datetime | str | None) -> str | None:
    if valor is None:
        return None
    return valor.isoformat() if isinstance(valor, (date, datetime)) else str(valor)


# Exibir horários sem incluir detalhes internos do banco no payload enviado à IA.
def _formatar_horario(valor: time | str) -> str:
    return valor.strftime("%H:%M") if isinstance(valor, time) else str(valor)


# Solicitar uma recomendação sem enviar dados pessoais nem alterar projetos.
def gerar_sugestao(tatuagens: list[dict[str, Any]]) -> str:
    projetos = preparar_projetos_para_sugestao(tatuagens)
    if not projetos:
        return "Não há projetos disponíveis para sugerir uma ordem de atenção."

    entrada = json.dumps({"projetos": projetos}, ensure_ascii=False)
    return obter_resposta_com_ferramentas(INSTRUCAO, entrada, FERRAMENTAS).text
