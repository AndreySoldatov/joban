from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.routers.boards_db import Board
from app.db import SessionDep
from typing import List

router = APIRouter(prefix="/boards")

create_boards_responses = {
    "200": {"description": "Board create"}, 
}
@router.post("/new", status_code=200, responses=create_boards_responses)
async def create_board(board: Board, session: SessionDep) -> Board:
    query = select(Board).where(Board.title == board.title)
    db_board = session.exec(query).first()
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

get_boards_list_responses = {
    "200": {"description": "Boards list received"}, 
}
@router.get("", status_code=200, responses=get_boards_list_responses)
async def get_boards_list(session: SessionDep) -> List[Board]:
    query = select(Board)
    boards = session.exec(query).all()
    return boards

get_board_responses = {
    "200": {"description": "Board received"}, 
    "404": {"description": "Board not found"}, 
}

#TODO: внутри таблицы сразу должны быть и столбцы, и таски
@router.get("/{board_id}", status_code=200, responses=get_board_responses)
async def get_board(board_id: int, session: SessionDep) -> Board:
    query = select(Board).where(Board.id == board_id)
    board = session.exec(query).first()
    if not board:
        raise HTTPException(detail="Board not found", status_code=404)
    return board
