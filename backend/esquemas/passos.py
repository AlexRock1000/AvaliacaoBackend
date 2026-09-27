from datetime import date, time

from pydantic import BaseModel, Field


# Descreve os dados enviados para registrar um dos três tipos de passo da cartilha.
class PassoEntrada(BaseModel):
    tipo: str = Field(min_length=1)
    data: date
    # Guarda o horário combinado quando o passo registra uma sessão.
    horario: time | None = None
    observacao: str = Field(min_length=1)
    # Guarda o desenho enviado como imagem codificada, sem criar arquivos neste ciclo.
    imagem: str | None = None


# Define os campos de cada passo devolvido pela API.
class PassoSaida(BaseModel):
    id: int
    tatuagem_id: int
    tipo: str
    data: date
    # Devolve o horário combinado da sessão para a cliente consultar.
    horario: time | None = None
    observacao: str
    # Devolve a imagem do desenho no histórico para a cliente e o tatuador consultarem.
    imagem: str | None = None
