from pydantic import BaseModel, Field


# Valida os dados que a pessoa envia ao pedir uma tatuagem.
class TatuagemEntrada(BaseModel):
    ideia: str = Field(min_length=3)
    local_corpo: str = Field(min_length=2)
    tamanho: str = Field(min_length=1)
    cliente_id: int = Field(gt=0)


# Define os campos da tatuagem devolvidos pelas rotas.
class TatuagemSaida(BaseModel):
    id: int
    ideia: str
    local_corpo: str
    tamanho: str
    cliente_id: int
    etapa: str
