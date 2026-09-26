# Mantém os dados deste ciclo em listas na memória, sem depender de um banco.
_tatuagens = []


# Na camada de repositórios, entrega os dados guardados para o serviço aplicar filtros.
def listar_tatuagens():
    return _tatuagens


# Na camada de repositórios, localiza o registro em memória para o serviço consultá-lo.
def buscar_tatuagem_por_id(tatuagem_id):
    for tatuagem in _tatuagens:
        if tatuagem["id"] == tatuagem_id:
            return tatuagem
    return None


# Na camada de repositórios, guarda o pedido em memória com identificador e histórico vazio.
def adicionar_tatuagem(dados):
    identificador = len(_tatuagens) + 1
    tatuagem = {"id": identificador, **dados, "passos": []}
    _tatuagens.append(tatuagem)
    return tatuagem


# Na camada de repositórios, lê o histórico em memória da tatuagem encontrada.
def listar_passos(tatuagem_id):
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is None:
        return None
    return tatuagem["passos"]


# Na camada de repositórios, guarda o passo em memória junto à tatuagem correspondente.
def adicionar_passo(tatuagem_id, dados):
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    identificador = sum(len(item["passos"]) for item in _tatuagens) + 1
    passo = {"id": identificador, "tatuagem_id": tatuagem_id, **dados}
    tatuagem["passos"].append(passo)
    return passo


# Na camada de repositórios, persiste a etapa que o serviço decidiu após validar o passo.
def atualizar_etapa(tatuagem_id, etapa):
    tatuagem = buscar_tatuagem_por_id(tatuagem_id)
    if tatuagem is not None:
        tatuagem["etapa"] = etapa
