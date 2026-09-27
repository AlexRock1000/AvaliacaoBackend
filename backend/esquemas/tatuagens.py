from pydantic import BaseModel, Field


# Valida os dados que a pessoa envia ao pedir uma tatuagem.
class TatuagemEntrada(BaseModel):
    ideia: str = Field(min_length=3)
    local_corpo: str = Field(min_length=2)
    tamanho: str = Field(min_length=1)
    cliente_id: int = Field(gt=0)
    # Recebe a imagem de referência codificada para ficar junto ao pedido em memória.
    imagem_referencia: str | None = None


# Define os campos da tatuagem devolvidos pelas rotas.
class TatuagemSaida(BaseModel):
    id: int
    ideia: str
    local_corpo: str
    tamanho: str
    cliente_id: int
    etapa: str


# Acrescenta a imagem apenas na consulta individual, sem carregá-la na lista da agenda.
class TatuagemDetalheSaida(TatuagemSaida):
    imagem_referencia: str | None = None
