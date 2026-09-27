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
    return tatuagens


# Na camada de serviços, encaminha a busca ao repositório para não acessar a lista diretamente.
def buscar_tatuagem(tatuagem_id):
    return repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)


# Na camada de serviços, monta o pedido e define a etapa inicial antes de guardá-lo.
def criar_tatuagem(entrada: TatuagemEntrada):
    dados = entrada.model_dump()
    dados["etapa"] = "pedida"
    return repositorio_tatuagem.adicionar_tatuagem(dados)


# Na camada de serviços, confere a tatuagem e então solicita seu histórico ao repositório.
def listar_passos(tatuagem_id):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    return repositorio_tatuagem.listar_passos(tatuagem_id)


# Na camada de serviços, aplica a regra da cartilha e devolve texto quando precisa recusar.
def registrar_passo(tatuagem_id: int, entrada: PassoEntrada):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None

    etapa = tatuagem["etapa"]
    tipo = entrada.tipo

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
    if tipo == "retoque_combinado" and etapa != "em sessões":
        return "O retoque só pode ser combinado depois de pelo menos uma sessão."
    if tipo == "retoque" and etapa != "aguardando retoque":
        return "O retoque só pode ser registrado como realizado depois de combinado."

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
    resultado = repositorio_tatuagem.adicionar_passo(tatuagem_id, dados_passo)
    repositorio_tatuagem.atualizar_etapa(tatuagem_id, etapas_por_tipo[tipo])
    return resultado
