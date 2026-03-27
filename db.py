import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

SQLITE_DB_NAME = os.getenv("SQLITE_DB_NAME", "db.sqlite3")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

DATABASE_URL = f"sqlite:///{SQLITE_DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    connect_args={"check_same_thread": False},
)

def create_all_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]