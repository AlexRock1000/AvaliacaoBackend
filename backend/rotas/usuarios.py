from fastapi import APIRouter, HTTPException, status

from esquemas.usuario import UsuarioCadastroEntrada, UsuarioSaida
from servicos import usuario as servico_usuario


roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])


@roteador.post("", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(entrada: UsuarioCadastroEntrada):
    """Registra uma conta pública como cliente e nunca devolve dados da senha."""
    try:
        return servico_usuario.cadastrar_usuario(entrada)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro
