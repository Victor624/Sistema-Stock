from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_all_tables
from routers import stock
from routers.auth import router as auth_router

app = FastAPI(
    title="Aplicacion-Stock",
    version="1.0.0"
)

app.include_router(stock.router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_all_tables()

@app.get("/")
def root():
    return {"message": "API funcionando"}

