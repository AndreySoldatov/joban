from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.routers.boards_db import Board
from app.routers.columns_db import Column
from app.db import SessionDep
from typing import List

from sqlalchemy import delete

router = APIRouter()

create_columns_responses = {
    "200": {"description": "Column create"},
}


@router.post("/boards/{board_id}/create_column", status_code=200, responses=create_columns_responses)
async def create_column(board_id: int, column: Column, session: SessionDep) -> Column:
    query = select(Column).where(Column.title == column.title,
                                 Column.board_id == column.board_id)
    db_column = session.exec(query).first()

    column.board_id = board_id
    session.add(column)
    session.commit()
    session.refresh(column)
    return column

get_columns_list_responses = {
    "200": {"description": "Columns list received"},
}


@router.get("/boards/{board_id}/get_columns_list", status_code=200, responses=create_columns_responses)
async def get_columns_list(session: SessionDep) -> List[Column]:
    query = select(Column)
    columns = session.exec(query).all()
    return columns


@router.delete("/boards/{board_id}/delete_all_columns", status_code=204)
async def delete_all_columns_by_boards(board_id: int, session: SessionDep) -> None:
    query = delete(Column).where(Column.board_id == board_id)
    result = session.execute(query)
    session.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail="No tasks found for the given column")


@router.delete("/boards/{board_id}/{col_id}/delete_column", status_code=204)
async def delete_task_by_id(col_id: int, session: SessionDep) -> None:
    query = select(Column).where(Column.id == col_id)
    task = session.exec(query).first()

    if not task:
        raise HTTPException(status_code=404, detail="Column not found")

    delete_query = delete(Column).where(Column.id == col_id)
    session.execute(delete_query)
    session.commit()

    return {"detail": f"Column '{task.title}' has been deleted successfully."}
