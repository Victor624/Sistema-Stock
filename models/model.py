from sqlmodel import Field, SQLModel
from pydantic import field_validator
from typing import Optional
from datetime import datetime





class StockBase(SQLModel):
    nombre: str
    cantidad: int
    codigo: str = Field(index=True, sa_column_kwargs={"unique": True})

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        if len(value) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return value

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("El código no puede estar vacío")
        return value

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value):
        if value < 0:
            raise ValueError("La cantidad no puede ser negativa")
        return value


class StockCreate(StockBase):
    pass


class StockUpdate(SQLModel):
    nombre: str | None = None
    cantidad: int | None = None
    codigo: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        if len(value) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return value

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("El código no puede estar vacío")
        return value

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value):
        if value is None:
            return value
        if value < 0:
            raise ValueError("La cantidad no puede ser negativa")
        return value


class Stock(StockBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")



class MovimientoBase(SQLModel):
    stock_id: int
    tipo: str  # "entrada" o "salida"
    cantidad: int
    fecha: datetime = Field(default_factory=datetime.today)


class Movimiento(MovimientoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MovimientoCreate(SQLModel):
    cantidad: int

