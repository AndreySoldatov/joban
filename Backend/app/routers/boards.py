from fastapi import APIRouter
from sqlmodel import select
from app.routers.boards_db import Board
from app.db import SessionDep
from typing import List

router = APIRouter(prefix="/boards")

create_boards_responses = {
    "200": {"description": "Board create"}, 
}

@router.post("/create_board", status_code=200, responses=create_boards_responses)
async def create_board(board: Board, session: SessionDep) -> Board:
    query = select(Board).where(Board.title == board.title)
    db_board = session.exec(query).first()
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

get_boards_responses = {
    "200": {"description": "Boards received"}, 
}

@router.get("/get_boards", status_code=200, responses=get_boards_responses)
async def get_board(session: SessionDep) -> List[Board]:
    query = select(Board)
    boards = session.exec(query).all()
    return boards
