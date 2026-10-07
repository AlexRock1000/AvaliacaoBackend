from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from autenticacao import exigir_perfil, garantir_acesso_tatuagem, obter_usuario_atual
from esquemas.passos import AgendamentoRetoqueEntrada, PassoEntrada, PassoSaida, SituacaoSessaoEntrada
from esquemas.tatuagens import TatuagemAtualizacaoEntrada, TatuagemDetalheSaida, TatuagemEntrada, TatuagemSaida
from servicos import tatuagem as servico_tatuagem


# Agrupa os endereços HTTP relacionados a tatuagens e seus passos.
roteador = APIRouter(prefix="/tatuagens", tags=["Tatuagens"])


# Lista horários que comportam a duração inteira escolhida para a sessão.
@roteador.get("/horarios-disponiveis", response_model=list[str])
def listar_horarios_disponiveis(
    data: date = Query(...),
    duracao_horas: int = Query(default=2, ge=1),
    ignorar_passo_id: int | None = Query(default=None),
    usuario: dict = Depends(obter_usuario_atual),
):
    del usuario
    return servico_tatuagem.listar_horarios_disponiveis(data, duracao_horas, ignorar_passo_id)


# Na camada de rotas, recebe filtros HTTP e chama o serviço para obter a lista.
@roteador.get("", response_model=list[TatuagemSaida])
def listar_tatuagens(
    etapa: str | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
    usuario: dict = Depends(obter_usuario_atual),
):
    if usuario["tipo"] == "cliente":
        cliente_id = usuario["id"]
    elif cliente_id is not None and usuario["tipo"] != "tatuador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para filtrar por cliente.")
    return servico_tatuagem.listar_tatuagens(etapa, cliente_id)


# Na camada de rotas, escolhe a resposta HTTP 404 quando o serviço não encontra o item.
@roteador.get("/{tatuagem_id}", response_model=TatuagemDetalheSaida)
def mostrar_tatuagem(tatuagem_id: int, usuario: dict = Depends(obter_usuario_atual)):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    garantir_acesso_tatuagem(usuario, tatuagem)
    return tatuagem


# Na camada de rotas, recebe o JSON e responde HTTP 201 após o serviço criar o pedido.
@roteador.post("", response_model=TatuagemSaida, status_code=status.HTTP_201_CREATED)
def pedir_tatuagem(entrada: TatuagemEntrada, usuario: dict = Depends(obter_usuario_atual)):
    if usuario["tipo"] != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas clientes podem criar pedidos.")
    entrada.cliente_id = usuario["id"]
    return servico_tatuagem.criar_tatuagem(entrada)


@roteador.put("/{tatuagem_id}", response_model=TatuagemSaida)
def atualizar_pedido(
    tatuagem_id: int,
    entrada: TatuagemAtualizacaoEntrada,
    usuario: dict = Depends(obter_usuario_atual),
):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    garantir_acesso_tatuagem(usuario, tatuagem)
    if usuario["tipo"] != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas clientes podem editar o pedido.")
    entrada.cliente_id = usuario["id"]
    try:
        return servico_tatuagem.atualizar_pedido(tatuagem_id, entrada)
    except LookupError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro
    except PermissionError as erro:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro


# Na camada de rotas, devolve o histórico e escolhe HTTP 404 se a tatuagem não existe.
@roteador.get("/{tatuagem_id}/passos", response_model=list[PassoSaida])
def listar_passos(tatuagem_id: int, usuario: dict = Depends(obter_usuario_atual)):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    garantir_acesso_tatuagem(usuario, tatuagem)
    return servico_tatuagem.listar_passos(tatuagem_id)


# Na camada de rotas, converte a recusa do serviço em HTTP 422, sem decidir a regra.
@roteador.post(
    "/{tatuagem_id}/passos",
    response_model=PassoSaida,
    status_code=status.HTTP_201_CREATED,
)
def registrar_passo(
    tatuagem_id: int,
    entrada: PassoEntrada,
    usuario: dict = Depends(obter_usuario_atual),
):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    garantir_acesso_tatuagem(usuario, tatuagem)
    if usuario["tipo"] == "cliente" and entrada.tipo not in {"desenho_aprovado", "desenho_reprovado"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Clientes só podem aprovar ou pedir ajustes no desenho.")
    resultado = servico_tatuagem.registrar_passo(tatuagem_id, entrada)
    if isinstance(resultado, str):
        raise HTTPException(status_code=422, detail=resultado)
    return resultado


@roteador.patch("/{tatuagem_id}/passos/{passo_id}/situacao", response_model=PassoSaida)
def atualizar_situacao_sessao(
    tatuagem_id: int,
    passo_id: int,
    entrada: SituacaoSessaoEntrada,
    usuario: dict = Depends(obter_usuario_atual),
):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    garantir_acesso_tatuagem(usuario, tatuagem)
    if usuario["tipo"] != "tatuador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas tatuadores podem atualizar a situação da sessão.")
    resultado = servico_tatuagem.atualizar_situacao_sessao(tatuagem_id, passo_id, entrada.situacao)
    if isinstance(resultado, str):
        raise HTTPException(status_code=422, detail=resultado)
    return resultado


# Atualiza a reserva do retoque antes da realização para evitar conflito com outros horários.
@roteador.patch("/{tatuagem_id}/passos/{passo_id}/agendamento", response_model=PassoSaida)
def atualizar_agendamento_retoque(
    tatuagem_id: int,
    passo_id: int,
    entrada: AgendamentoRetoqueEntrada,
    usuario: dict = Depends(obter_usuario_atual),
):
    tatuagem = servico_tatuagem.buscar_tatuagem(tatuagem_id)
    if tatuagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tatuagem não encontrada.")
    garantir_acesso_tatuagem(usuario, tatuagem)
    if usuario["tipo"] != "tatuador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas tatuadores podem ajustar o agendamento do retoque.")
    resultado = servico_tatuagem.atualizar_agendamento_retoque(tatuagem_id, passo_id, entrada)
    if isinstance(resultado, str):
        raise HTTPException(status_code=422, detail=resultado)
    return resultado
