from fastapi import  APIRouter, HTTPException,Query
from sqlmodel import select
from sqlalchemy import or_
from routers.auth import get_current_user

from typing import Annotated
from fastapi import  Depends

from db import SessionDep
from models.users import User

from models.model import StockCreate, Stock, StockUpdate,Movimiento

router = APIRouter()


# POST - crear producto
@router.post("/stocks/", response_model=Stock,tags=["Stock"])

def create_stock(
    stock: StockCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):

    existente = session.exec(select(Stock).where(Stock.codigo == stock.codigo)).first()

    if existente:
        raise HTTPException(status_code=400, detail="El código ya existe")

    nuevo_stock = Stock(
        nombre=stock.nombre,
        cantidad=stock.cantidad,
        codigo=stock.codigo,
        owner_id=current_user.id,
    )

    session.add(nuevo_stock)
    session.commit()
    session.refresh(nuevo_stock)
    return nuevo_stock

# GET - listar todos
@router.get("/stocks/", response_model=list[Stock],tags=["Stock"])
def read_stocks(session: SessionDep):

    stocks = session.exec(select(Stock)).all()
    return stocks


# GET - traer uno por id
@router.get("/stocks/{stock_id}", response_model=Stock,tags=["Stock"])

def read_stock(stock_id: int, session: SessionDep):

    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return stock



@router.get("/stocks/listar/", tags=["Stock"])
def listar_stocks(
    buscar: str | None = Query(default=None),
    session: SessionDep = None
):
    query = select(Stock)

    if buscar and buscar.strip():
        termino = buscar.strip()
        query = query.where(
            or_(
                Stock.nombre.contains(termino),
                Stock.codigo.contains(termino)
            )
        )

    print(query)

    productos = session.exec(query).all()
    return productos

# PATCH - actualizar
@router.put("/stocks/{stock_id}", response_model=Stock, tags=["Stock"])
def update_stock(
    stock_id: int,
    stock_data: StockUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if stock.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tenés permiso para editar este producto",
        )

    datos_actualizados = stock_data.model_dump(exclude_unset=True)

    for key, value in datos_actualizados.items():
        setattr(stock, key, value)

    session.add(stock)
    session.commit()
    session.refresh(stock)
    return stock


@router.patch("/stocks/{stock_id}/cantidad", response_model=Stock, tags=["Stock"])
def modificar_cantidad(
    stock_id: int,
    cambio: int = Query(..., description="Cantidad a sumar o restar"),
    session: SessionDep = None
):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    nueva_cantidad = stock.cantidad + cambio

    if nueva_cantidad < 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad no puede quedar negativa"
        )

    stock.cantidad = nueva_cantidad

    session.add(stock)
    session.commit()
    session.refresh(stock)

    return stock

# DELETE - eliminar
@router.delete("/stocks/{stock_id}", tags=["Stock"])
def delete_stock(
    stock_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if stock.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tenés permiso para eliminar este producto",
        )

    session.delete(stock)
    session.commit()
    return {"message": "Producto eliminado"}

#sumar  

@router.patch("/stocks/{stock_id}/sumar", tags=["Stock"])
def sumar_stock(
    stock_id: int,
    cantidad: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if stock.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso")

    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    stock.cantidad += cantidad

    movimiento = Movimiento(
        stock_id=stock.id,
        tipo="entrada",
        cantidad=cantidad,
    )

    session.add(stock)
    session.add(movimiento)
    session.commit()
    session.refresh(stock)

    return {
        "mensaje": "Stock sumado correctamente",
        "stock": stock
    }


@router.patch("/stocks/{stock_id}/restar", tags=["Stock"])
def restar_stock(
    stock_id: int,
    cantidad: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if stock.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso")

    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    if stock.cantidad < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    stock.cantidad -= cantidad

    movimiento = Movimiento(
        stock_id=stock.id,
        tipo="salida",
        cantidad=cantidad,
    )

    session.add(stock)
    session.add(movimiento)
    session.commit()
    session.refresh(stock)

    return {
        "mensaje": "Stock restado correctamente",
        "stock": stock
    }




@router.get("/stocks/{stock_id}/movimientos", response_model=list[Movimiento], tags=["Movimientos"])
def obtener_movimientos(
    stock_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if stock.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso")

    movimientos = session.exec(
        select(Movimiento).where(Movimiento.stock_id == stock_id)
    ).all()

    return movimientos


@router.get("/stocks/{stock_id}/resumen", tags=["Movimientos"])
def resumen_movimientos(stock_id: int, session: SessionDep):
    stock = session.get(Stock, stock_id)

    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    movimientos = session.exec(
        select(Movimiento).where(Movimiento.stock_id == stock_id)
    ).all()

    entradas = [m for m in movimientos if m.tipo == "entrada"]
    salidas = [m for m in movimientos if m.tipo == "salida"]

    return {
        "producto": stock.nombre,
        "codigo": stock.codigo,
        "stock_actual": stock.cantidad,
        "veces_sumado": len(entradas),
        "veces_restado": len(salidas),
        "total_entradas": sum(m.cantidad for m in entradas),
        "total_salidas": sum(m.cantidad for m in salidas),
    }