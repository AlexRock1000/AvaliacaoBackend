import re
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, Field, field_validator


class TamanhoEmCentimetros(BaseModel):
    tamanho: str = Field(min_length=1)

    @field_validator("tamanho", mode="before")
    @classmethod
    def validar_tamanho(cls, valor):
        if isinstance(valor, bool) or not isinstance(valor, (str, int, float, Decimal)):
            raise ValueError("Informe o tamanho usando apenas números, em centímetros.")

        texto = str(valor).strip().lower()
        if texto.endswith("cm"):
            texto = texto[:-2].strip()
        if not re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", texto):
            raise ValueError("Informe o tamanho usando apenas números, em centímetros.")

        try:
            medida = Decimal(texto.replace(",", "."))
        except InvalidOperation as erro:
            raise ValueError("Informe o tamanho usando apenas números, em centímetros.") from erro
        if not medida.is_finite() or medida <= 0:
            raise ValueError("O tamanho deve ser maior que zero.")

        return f"{format(medida.normalize(), 'f')} cm"


# Valida os dados que a pessoa envia ao pedir uma tatuagem.
class TatuagemEntrada(TamanhoEmCentimetros):
    ideia: str = Field(min_length=3)
    local_corpo: str = Field(min_length=2)
    cliente_id: int = Field(gt=0)
    # Recebe a imagem de referência codificada para ficar junto ao pedido em memória.
    imagem_referencia: str | None = None


class TatuagemAtualizacaoEntrada(TatuagemEntrada):
    pass


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
