from fastapi import APIRouter, HTTPException, Query, status

from esquemas.passos import PassoEntrada, PassoSaida
from esquemas.tatuagens import TatuagemEntrada, TatuagemSaida
from servicos import tatuagem as servico_tatuagem


# Agrupa os endereços HTTP relacionados a tatuagens e seus passos.
roteador = APIRouter(prefix="/tatuagens", tags=["Tatuagens"])


# Lista tatuagens e aplica os filtros opcionais recebidos pela consulta HTTP.
@roteador.get("", response_model=list[TatuagemSaida])
def listar_tatuagens(
    etapa: str | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
):
    return servico_tatuagem.listar_tatuagens(etapa, cliente_id)


# Busca uma tatuagem pelo identificador e responde 404 quando não existe.
@roteador.get("/{tatuagem_id}", response_model=TatuagemSaida)
def mostrar_tatuagem(tatuagem_id: int):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    return tatuagem


# Registra um pedido novo e usa 201 para indicar que ele foi criado.
@roteador.post("", response_model=TatuagemSaida, status_code=status.HTTP_201_CREATED)
def pedir_tatuagem(entrada: TatuagemEntrada):
    return servico_tatuagem.criar_tatuagem(entrada)


# Lista o histórico de passos da tatuagem indicada e sinaliza se ela não existe.
@roteador.get("/{tatuagem_id}/passos", response_model=list[PassoSaida])
def listar_passos(tatuagem_id: int):
    passos = servico_tatuagem.listar_passos(tatuagem_id)
    if passos is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    return passos


# Registra um passo aceito ou converte a recusa da regra em resposta HTTP 422.
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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=resultado)
    return resultado
