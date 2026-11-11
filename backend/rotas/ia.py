from fastapi import APIRouter, Depends, HTTPException, status

from ia.modelos import ErroProvedoresIA
from ia.sugestao import gerar_sugestao
from permissoes import (
    PERMISSAO_LISTAR_TATUAGENS,
    PERMISSAO_LISTAR_TODAS_TATUAGENS,
)
from seguranca import exigir_permissao, usuario_tem_permissao
from servicos import ia as servico_ia
from servicos import tatuagem as servico_tatuagem


roteador = APIRouter(prefix="/ia", tags=["Inteligência artificial"])


# Gera uma sugestão apenas com projetos dentro do escopo de acesso do usuário.
@roteador.post("/sugestao-prioridade")
def sugerir_prioridade(
    usuario: dict = Depends(exigir_permissao(PERMISSAO_LISTAR_TATUAGENS)),
):
    cliente_id = (
        None
        if usuario_tem_permissao(usuario, PERMISSAO_LISTAR_TODAS_TATUAGENS)
        else usuario["id"]
    )
    tatuagens = servico_tatuagem.listar_tatuagens(cliente_id=cliente_id)
    projetos = servico_ia.preparar_projetos_para_sugestao(tatuagens)
    try:
        return {"sugestao": gerar_sugestao(projetos)}
    except ErroProvedoresIA as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(erro),
        ) from erro
