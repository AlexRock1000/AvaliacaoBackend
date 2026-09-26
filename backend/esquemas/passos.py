from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# Aceita somente os três tipos de passo descritos na cartilha.
class PassoEntrada(BaseModel):
    tipo: Literal["desenho_aprovado", "sessao", "retoque"]
    data: date
    observacao: str = Field(min_length=1)


# Define os campos de cada passo devolvido pela API.
class PassoSaida(BaseModel):
    id: int
    tatuagem_id: int
    tipo: str
    data: date
    observacao: str
