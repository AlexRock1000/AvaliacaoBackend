from datetime import date

from pydantic import BaseModel, Field


# Descreve os dados enviados para registrar um dos três tipos de passo da cartilha.
class PassoEntrada(BaseModel):
    tipo: str = Field(min_length=1)
    data: date
    observacao: str = Field(min_length=1)


# Define os campos de cada passo devolvido pela API.
class PassoSaida(BaseModel):
    id: int
    tatuagem_id: int
    tipo: str
    data: date
    observacao: str
