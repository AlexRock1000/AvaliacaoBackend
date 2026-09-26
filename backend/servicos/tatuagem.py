from esquemas.passos import PassoEntrada
from esquemas.tatuagens import TatuagemEntrada
from repositorios import tatuagem as repositorio_tatuagem


# Filtra a lista conforme os critérios opcionais pedidos pela tela.
def listar_tatuagens(etapa=None, cliente_id=None):
    tatuagens = repositorio_tatuagem.listar_tatuagens()
    if etapa is not None:
        tatuagens = [tatuagem for tatuagem in tatuagens if tatuagem["etapa"] == etapa]
    if cliente_id is not None:
        tatuagens = [tatuagem for tatuagem in tatuagens if tatuagem["cliente_id"] == cliente_id]
    return tatuagens


# Procura uma tatuagem pelo identificador sem expor a lista do repositório.
def buscar_tatuagem(tatuagem_id):
    return repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)


# Monta os dados iniciais do pedido e define sua primeira etapa.
def criar_tatuagem(entrada: TatuagemEntrada):
    dados = entrada.model_dump()
    dados["etapa"] = "pedida"
    return repositorio_tatuagem.adicionar_tatuagem(dados)


# Busca o histórico apenas quando a tatuagem existe.
def listar_passos(tatuagem_id):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    return repositorio_tatuagem.listar_passos(tatuagem_id)


# Aplica a ordem da cartilha e devolve o motivo em texto quando precisa recusar.
def registrar_passo(tatuagem_id: int, entrada: PassoEntrada):
    tatuagem = repositorio_tatuagem.buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None

    etapa = tatuagem["etapa"]
    tipo = entrada.tipo

    if tipo == "desenho_aprovado" and etapa != "pedida":
        return "O desenho só pode ser aprovado quando a tatuagem está pedida."
    if tipo == "sessao" and etapa not in ("desenho aprovado", "em sessões"):
        return "A sessão só pode ser registrada depois da aprovação do desenho."
    if tipo == "retoque" and etapa != "em sessões":
        return "O retoque só pode ser registrado depois de pelo menos uma sessão."

    # Traduz o passo aceito para a próxima etapa que será guardada.
    etapas_por_tipo = {
        "desenho_aprovado": "desenho aprovado",
        "sessao": "em sessões",
        "retoque": "finalizada",
    }
    dados_passo = entrada.model_dump()
    resultado = repositorio_tatuagem.adicionar_passo(tatuagem_id, dados_passo)
    repositorio_tatuagem.atualizar_etapa(tatuagem_id, etapas_por_tipo[tipo])
    return resultado
