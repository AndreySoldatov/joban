from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.routers.boards_db import Board, Column, Task
from app.db import SessionDep
from typing import List
from app.dependencies import RestRequestModel
from pydantic import Field

router = APIRouter(prefix="/boards")

create_boards_responses = {
    "200": {"description": "Board create"},
}

class ColumnCreateRequest(RestRequestModel):
    title: str = Field()
    order_number: int = Field()

class BoardCreateRequest(RestRequestModel):
    title: str = Field()
    columns: List['ColumnCreateRequest']

@router.post("/new", status_code=200, responses=create_boards_responses)
async def create_board(board_req: BoardCreateRequest, session: SessionDep):
    board = Board(title=board_req.title, 
                  columns=[Column(title=col.title, ord_num=col.order_number) for col in board_req.columns]
                )
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

@router.get("/{board_id}", status_code=200)
async def get_board(board_id: int, session: SessionDep):
    board = session.exec(select(Board).where(Board.id == board_id)).first()
    if not board:
        raise HTTPException(detail="Board not found", status_code=404)
    
    columns = [{
        "boardId": col.board_id,
        "id": col.id,
        "orderNumber": col.ord_num,
        "title": col.title,
        "tasks": [{
            "title": t.title,
            "body": t.body,
            "columnId": t.col_id,
            "orderNumber": t.ord_num,
            "id": t.id
        } for t in col.tasks]
    } for col in board.columns]

    return {
        "id": board.id,
        "title": board.title,
        "columns": columns,
    }

@router.delete("/{board_id}", status_code=200)
async def del_board(board_id: int, session: SessionDep):
    board = session.exec(select(Board).where(Board.id == board_id)).first()
    session.delete(board)
    session.commit()


class TaskPatch(RestRequestModel):
    id: int
    title: str
    order_number: int
    body: str

class ColumnPatch(RestRequestModel):
    id: int
    title: str
    order_number: int
    tasks: List[TaskPatch]

class BoardPatch(RestRequestModel):
    title: str
    columns: List[ColumnPatch]

@router.patch("/{board_id}", status_code=200)
async def del_board(new_board: BoardPatch, board_id: int, session: SessionDep):
    board = session.get(Board, board_id)
    board.title = new_board.title
    session.add(board)

    for c in new_board.columns:
        column = session.get(Column, c.id)
        column.title = c.title
        column.ord_num = c.order_number
        session.add(column)

        for t in c.tasks:
            task = session.get(Task, t.id)
            task.title = t.title
            task.body = t.body
            task.ord_num = t.order_number
            session.add(task)
    
    session.commit()


class TaskCreateRequest(RestRequestModel):
    title: str = Field()
    description: str = Field()
    column_id: int = Field()
    order_number: int

@router.post("/{board_id}/tasks/new", status_code=200)
async def add_task(req: TaskCreateRequest, board_id: int, session: SessionDep):
    column = session.exec(select(Column).where(Column.id == req.column_id)).first()
    column.tasks.append(Task(
        title=req.title, 
        body=req.description
    ))
    session.add(column)
    session.commit()