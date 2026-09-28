from datetime import date, datetime, time, timedelta

from esquemas.passos import PassoEntrada
from esquemas.tatuagens import TatuagemEntrada
from repositorios import tatuagem as repositorio_tatuagem


# Na camada de serviços, filtra os dados do repositório conforme os critérios da tela.
def listar_tatuagens(etapa=None, cliente_id=None):
    tatuagens = repositorio_tatuagem.listar_tatuagens()
    if etapa is not None:
        tatuagens = [tatuagem for tatuagem in tatuagens if tatuagem["etapa"] == etapa]
    if cliente_id is not None:
        tatuagens = [tatuagem for tatuagem in tatuagens if tatuagem["cliente_id"] == cliente_id]
    return sorted(tatuagens, key=lambda tatuagem: tatuagem["id"], reverse=True)


# Na camada de serviços, encaminha a busca ao repositório para não acessar a lista diretamente.
def buscar_tatuagem(tatuagem_id):
    return repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)


# Na camada de serviços, monta o pedido e define a etapa inicial antes de guardá-lo.
def criar_tatuagem(entrada: TatuagemEntrada):
    dados = entrada.model_dump()
    dados["etapa"] = "pedida"
    return repositorio_tatuagem.adicionar_tatuagem(dados)


# Permite corrigir o pedido apenas enquanto ele ainda aguarda o início da preparação.
def atualizar_pedido(tatuagem_id: int, entrada: TatuagemEntrada):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        raise LookupError("Tatuagem não encontrada.")
    if tatuagem["cliente_id"] != entrada.cliente_id:
        raise PermissionError("Este pedido não pertence a este perfil de cliente.")
    if tatuagem["etapa"] != "pedida":
        raise ValueError("O pedido não pode mais ser alterado depois que o estúdio inicia a preparação.")

    dados = {
        "ideia": entrada.ideia,
        "local_corpo": entrada.local_corpo,
        "tamanho": entrada.tamanho,
    }
    if "imagem_referencia" in entrada.model_fields_set:
        dados["imagem_referencia"] = entrada.imagem_referencia
    return repositorio_tatuagem.atualizar_pedido(tatuagem_id, dados)


# Na camada de serviços, confere a tatuagem e então solicita seu histórico ao repositório.
def listar_passos(tatuagem_id):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    return repositorio_tatuagem.listar_passos(tatuagem_id)


# Calcula os inícios de sessão possíveis e remove horários que se sobrepõem a reservas existentes.
def listar_horarios_disponiveis(data, duracao_horas=2, ignorar_passo_id=None):
    agora = datetime.now()
    if data.weekday() == 0 or data < agora.date():
        return []

    duracao = timedelta(hours=duracao_horas)
    inicio_almoco = datetime.combine(data, time(hour=12))
    fim_almoco = datetime.combine(data, time(hour=13))
    horarios = []

    # Mantém cada reserva dentro da janela atual do estúdio, das 10h às 20h.
    for hora in range(10, 21 - duracao_horas):
        horario = time(hour=hora)
        inicio = datetime.combine(data, horario)
        fim = inicio + duracao
        if data == agora.date() and inicio <= agora:
            continue
        if inicio < fim_almoco and fim > inicio_almoco:
            continue

        ocupado = False
        for tatuagem in repositorio_tatuagem.listar_tatuagens():
            for passo in tatuagem["passos"]:
                horario_marcado = passo.get("horario")
                if passo["id"] != ignorar_passo_id and passo["tipo"] in ("sessao", "retoque_combinado") and passo.get("situacao", "agendada") == "agendada" and passo["data"] == data and horario_marcado is not None:
                    inicio_marcado = datetime.combine(data, horario_marcado)
                    duracao_marcada = timedelta(hours=passo.get("duracao_horas", 2) or 2)
                    fim_marcado = inicio_marcado + duracao_marcada
                    if inicio < fim_marcado and inicio_marcado < fim:
                        ocupado = True
                        break
            if ocupado:
                break

        if not ocupado:
            horarios.append(horario.strftime("%H:%M"))

    return horarios


# Na camada de serviços, aplica a regra da cartilha e devolve texto quando precisa recusar.
def registrar_passo(tatuagem_id: int, entrada: PassoEntrada):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None

    etapa = tatuagem["etapa"]
    tipo = entrada.tipo
    reserva_retoque = None

    if tipo not in ("desenho_enviado", "desenho_aprovado", "desenho_reprovado", "sessao", "retoque_combinado", "retoque"):
        return "O passo deve registrar o desenho enviado, a decisão da cliente, sessão ou retoque."
    if tipo == "desenho_enviado" and etapa not in ("pedida", "ajustes no desenho"):
        return "O desenho só pode ser enviado para um pedido recebido ou que precisa de ajustes."
    if tipo == "desenho_enviado" and not entrada.imagem:
        return "Envie a imagem do desenho para a cliente analisar."
    if tipo in ("desenho_aprovado", "desenho_reprovado") and etapa != "aguardando aprovação":
        return "A cliente só pode responder depois que o desenho for enviado."
    if tipo == "sessao" and etapa not in ("desenho aprovado", "em sessões"):
        return "A sessão só pode ser registrada depois da aprovação do desenho."
    if tipo == "sessao" and entrada.horario is None:
        return "Escolha um horário disponível para a sessão."
    if tipo == "sessao" and entrada.horario.strftime("%H:%M") not in listar_horarios_disponiveis(entrada.data, entrada.duracao_horas):
        return "Esse horário não está mais disponível. Escolha outro horário."
    if tipo == "retoque_combinado" and etapa != "em sessões":
        return "O retoque só pode ser combinado depois de pelo menos uma sessão."
    if tipo == "retoque" and etapa != "aguardando retoque":
        return "O retoque só pode ser registrado como realizado depois de combinado."
    if tipo == "retoque":
        reserva_retoque = next(
            (passo for passo in tatuagem["passos"] if passo["tipo"] == "retoque_combinado" and passo.get("situacao", "agendada") == "agendada"),
            None,
        )
        if reserva_retoque is None:
            return "O agendamento do retoque não foi encontrado."

    # Traduz o passo aceito para a próxima etapa que será guardada.
    etapas_por_tipo = {
        "desenho_enviado": "aguardando aprovação",
        "desenho_aprovado": "desenho aprovado",
        "desenho_reprovado": "ajustes no desenho",
        "sessao": "em sessões",
        "retoque_combinado": "aguardando retoque",
        "retoque": "finalizada",
    }
    dados_passo = entrada.model_dump()
    if tipo not in ("sessao", "retoque"):
        dados_passo["duracao_horas"] = None
    resultado = repositorio_tatuagem.adicionar_passo(tatuagem_id, dados_passo)
    if reserva_retoque is not None:
        reserva_retoque["situacao"] = "realizada"
    repositorio_tatuagem.atualizar_etapa(tatuagem_id, etapas_por_tipo[tipo])
    return resultado


def atualizar_situacao_sessao(tatuagem_id: int, passo_id: int, situacao: str):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    passo = next((item for item in tatuagem["passos"] if item["id"] == passo_id), None)
    if passo is None or passo["tipo"] != "sessao":
        return "A sessão não foi encontrada."
    if passo.get("situacao", "agendada") != "agendada":
        return "Somente sessões agendadas podem ser atualizadas."
    if situacao == "realizada":
        data_retoque = date.today() + timedelta(days=15)
        horarios = []
        for _ in range(370):
            if data_retoque.weekday() != 0:
                horarios = listar_horarios_disponiveis(data_retoque, duracao_horas=2)
                if horarios:
                    break
            data_retoque += timedelta(days=1)
        if not horarios:
            return "Não foi possível encontrar um horário para agendar o retoque."

        passo["situacao"] = situacao
        passo["observacao"] = "Sessão realizada."
        repositorio_tatuagem.adicionar_passo(
            tatuagem_id,
            {
                "tipo": "retoque_combinado",
                "data": data_retoque,
                "horario": datetime.strptime(horarios[0], "%H:%M").time(),
                "duracao_horas": 2,
                "observacao": "Retoque agendado automaticamente para 15 dias após a sessão.",
                "imagem": None,
                "situacao": "agendada",
            },
        )
        repositorio_tatuagem.atualizar_etapa(tatuagem_id, "aguardando retoque")
    elif situacao == "cancelada":
        passo["situacao"] = situacao
        passo["observacao"] = "Sessão cancelada."
    return passo


# Atualiza a duração e o horário do retoque, mantendo o horário livre para o tempo escolhido.
def atualizar_agendamento_retoque(tatuagem_id, passo_id, entrada):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None

    passo = next((item for item in tatuagem["passos"] if item["id"] == passo_id), None)
    if passo is None or passo["tipo"] != "retoque_combinado" or passo.get("situacao", "agendada") != "agendada":
        return "O retoque agendado não foi encontrado."

    horarios = listar_horarios_disponiveis(
        passo["data"], entrada.duracao_horas, ignorar_passo_id=passo_id
    )
    if entrada.horario.strftime("%H:%M") not in horarios:
        return "Esse horário não comporta a duração escolhida. Selecione outro horário livre."

    passo["horario"] = entrada.horario
    passo["duracao_horas"] = entrada.duracao_horas
    return passo
