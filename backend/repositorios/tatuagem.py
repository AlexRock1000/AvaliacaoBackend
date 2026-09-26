# Mantém os dados deste ciclo em listas na memória, sem depender de um banco.
_tatuagens = []
_proximo_id_tatuagem = 1
_proximo_id_passo = 1


# Devolve a lista para a camada de serviço aplicar filtros e decisões.
def listar_tatuagens():
    return _tatuagens


# Encontra uma tatuagem pelo identificador ou devolve None se não existir.
def buscar_tatuagem_por_id(tatuagem_id):
    for tatuagem in _tatuagens:
        if tatuagem["id"] == tatuagem_id:
            return tatuagem
    return None


# Guarda o pedido com um identificador novo e uma lista de passos vazia.
def adicionar_tatuagem(dados):
    global _proximo_id_tatuagem
    tatuagem = {"id": _proximo_id_tatuagem, **dados, "passos": []}
    _tatuagens.append(tatuagem)
    _proximo_id_tatuagem += 1
    return tatuagem


# Devolve o histórico guardado para a tatuagem encontrada.
def listar_passos(tatuagem_id):
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    return tatuagem["passos"]


# Guarda um passo com identificador e referência à tatuagem correspondente.
def adicionar_passo(tatuagem_id, dados):
    global _proximo_id_passo
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    passo = {"id": _proximo_id_passo, "tatuagem_id": tatuagem_id, **dados}
    tatuagem["passos"].append(passo)
    _proximo_id_passo += 1
    return passo


# Atualiza a etapa depois que o serviço aprovou a ordem do passo.
def atualizar_etapa(tatuagem_id, etapa):
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is not None:
        tatuagem["etapa"] = etapa
