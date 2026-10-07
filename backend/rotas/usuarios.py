from fastapi import APIRouter, HTTPException, status

from esquemas.usuario import CadastroUsuarioEntrada, UsuarioSaida
from servicos import usuario as servico_usuario

roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post("", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(entrada: CadastroUsuarioEntrada):
    """Cria conta de cliente sem permitir que o solicitante escolha o próprio perfil."""
    try:
        return servico_usuario.cadastrar(entrada.nome, entrada.email, entrada.senha)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro
