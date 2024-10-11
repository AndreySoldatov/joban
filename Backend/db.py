from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

slqite_db_name = "joban-data.db"
sqlite_url = f"sqlite:///{slqite_db_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    login: str = Field(max_length=20, index=True)
    password: str = Field(max_length=16)