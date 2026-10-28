from fastapi import APIRouter, Depends, HTTPException, status

from esquemas.usuario import CadastroTatuadorEntrada, CadastroUsuarioEntrada, UsuarioSaida
from permissoes import PERMISSAO_CADASTRAR_TATUADOR
from seguranca import exigir_permissao
from servicos import usuario as servico_usuario

roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post("", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(entrada: CadastroUsuarioEntrada):
    """Cria conta de cliente sem permitir que o solicitante escolha o próprio perfil."""
    # GRUPOS E PERMISSÕES: cadastro público sempre recebe o grupo cliente no serviço.
    try:
        return servico_usuario.cadastrar(entrada.nome, entrada.email, entrada.senha)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro


@roteador.post("/tatuadores", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_tatuador(
    entrada: CadastroTatuadorEntrada,
    usuario: dict = Depends(exigir_permissao(PERMISSAO_CADASTRAR_TATUADOR)),
):
    """Cria conta de tatuador; somente a equipe autenticada pode cadastrar equipe."""
    try:
        return servico_usuario.cadastrar_tatuador(entrada.nome, entrada.email, entrada.senha)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro
