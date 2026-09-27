from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from esquemas.passos import PassoEntrada, PassoSaida, SituacaoSessaoEntrada
from esquemas.tatuagens import TatuagemDetalheSaida, TatuagemEntrada, TatuagemSaida
from servicos import tatuagem as servico_tatuagem


# Agrupa os endereços HTTP relacionados a tatuagens e seus passos.
roteador = APIRouter(prefix="/tatuagens", tags=["Tatuagens"])


# Lista opções de início para sessões de duas horas na data escolhida.
@roteador.get("/horarios-disponiveis", response_model=list[str])
def listar_horarios_disponiveis(data: date = Query(...)):
    return servico_tatuagem.listar_horarios_disponiveis(data)


# Na camada de rotas, recebe filtros HTTP e chama o serviço para obter a lista.
@roteador.get("", response_model=list[TatuagemSaida])
def listar_tatuagens(
    etapa: str | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
):
    return servico_tatuagem.listar_tatuagens(etapa, cliente_id)


# Na camada de rotas, escolhe a resposta HTTP 404 quando o serviço não encontra o item.
@roteador.get("/{tatuagem_id}", response_model=TatuagemDetalheSaida)
def mostrar_tatuagem(tatuagem_id: int):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    return tatuagem


# Na camada de rotas, recebe o JSON e responde HTTP 201 após o serviço criar o pedido.
@roteador.post("", response_model=TatuagemSaida, status_code=status.HTTP_201_CREATED)
def pedir_tatuagem(entrada: TatuagemEntrada):
    return servico_tatuagem.criar_tatuagem(entrada)


# Na camada de rotas, devolve o histórico e escolhe HTTP 404 se a tatuagem não existe.
@roteador.get("/{tatuagem_id}/passos", response_model=list[PassoSaida])
def listar_passos(tatuagem_id: int):
    passos = servico_tatuagem.listar_passos(tatuagem_id)
    if passos is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    return passos


# Na camada de rotas, converte a recusa do serviço em HTTP 422, sem decidir a regra.
@roteador.post(
    "/{tatuagem_id}/passos",
    response_model=PassoSaida,
    status_code=status.HTTP_201_CREATED,
)
def registrar_passo(tatuagem_id: int, entrada: PassoEntrada):
    resultado = servico_tatuagem.registrar_passo(tatuagem_id, entrada)
    if resultado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    if isinstance(resultado, str):
        raise HTTPException(status_code=422, detail=resultado)
    return resultado


@roteador.patch("/{tatuagem_id}/passos/{passo_id}/situacao", response_model=PassoSaida)
def atualizar_situacao_sessao(tatuagem_id: int, passo_id: int, entrada: SituacaoSessaoEntrada):
    resultado = servico_tatuagem.atualizar_situacao_sessao(tatuagem_id, passo_id, entrada.situacao)
    if resultado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    if isinstance(resultado, str):
        raise HTTPException(status_code=422, detail=resultado)
    return resultado
