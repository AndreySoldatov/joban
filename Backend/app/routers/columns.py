from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.routers.boards_db import Board
from app.routers.columns_db import Column
from app.db import SessionDep
from typing import List

router = APIRouter()

create_columns_responses = {
    "200": {"description": "Column create"}, 
}

@router.post("/boards/{board_id}/create_column", status_code=200, responses=create_columns_responses)
async def create_column(board_id: int, column: Column, session: SessionDep) -> Column:
    query = select(Column).where(Column.title == column.title, Column.board_id == column.board_id)
    db_column = session.exec(query).first()

    column.board_id = board_id
    session.add(column)
    session.commit()
    session.refresh(column)
    return column

