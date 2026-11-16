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

TOM E FORMATO DA RESPOSTA
Converse diretamente com a pessoa, em português brasileiro, com o mesmo tom informal e simples de uma conversa do dia a dia. Use frases curtas e naturais, sem linguagem técnica. Escreva em texto simples, sem Markdown: não use títulos, listas, marcadores, numeração, negrito, tabelas ou blocos de código. Responda em no máximo 50 linhas.
Quando der para comparar, diga naturalmente por qual projeto começaria e por quê, mencionando o código e a posição sugerida. Se houver mais projetos, explique a ordem com frases curtas, uma por linha, sem transformar a resposta em lista. Se não der para ordenar, explique em poucas palavras o que falta ou qual é o conflito. Evite uma introdução formal; comece já pela sugestão, como “Eu começaria pelo projeto P-123, porque...”.
Ao mencionar datas, use sempre DD-MM-AAAA. Apresente a ordem como recomendação para revisão, não como decisão definitiva.

ENTRADA VAGA OU FORA DO ASSUNTO
Se faltarem dados, diga brevemente o que falta. Se a entrada estiver fora do assunto, explique em uma frase que você ajuda a ordenar projetos e peça os dados. Não responda a outros pedidos."""


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
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d-%m-%Y")
    texto = str(valor)
    try:
        return date.fromisoformat(texto[:10]).strftime("%d-%m-%Y")
    except ValueError:
        return texto


# Exibir horários sem incluir detalhes internos do banco no payload enviado à IA.
def _formatar_horario(valor: time | str) -> str:
    return valor.strftime("%H:%M") if isinstance(valor, time) else str(valor)


# Impedir que uma resposta longa ultrapasse o limite mostrado no painel.
def _limitar_linhas_resposta(texto: str) -> str:
    linhas = texto.splitlines()
    if len(linhas) <= 50:
        return texto
    return "\n".join(
        [*linhas[:49], "… (resposta resumida ao limite de 50 linhas)"]
    )


# Solicitar uma recomendação sem enviar dados pessoais nem alterar projetos.
def gerar_sugestao(tatuagens: list[dict[str, Any]]) -> str:
    projetos = preparar_projetos_para_sugestao(tatuagens)
    if not projetos:
        return "Não há projetos disponíveis para sugerir uma ordem de atenção."

    entrada = json.dumps({"projetos": projetos}, ensure_ascii=False)
    resposta = obter_resposta_com_ferramentas(INSTRUCAO, entrada, FERRAMENTAS).text
    return _limitar_linhas_resposta(resposta)
