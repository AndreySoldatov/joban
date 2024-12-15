from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.routers.boards_db import Board, Column, Task
from app.db import SessionDep
from typing import List, Annotated
from app.dependencies import RestRequestModel
from pydantic import Field
from app.routers.auth import check_token

board_router = APIRouter(prefix="/boards")


class ColumnCreateRequest(RestRequestModel):
    title: str
    order_number: int


class BoardCreateRequest(RestRequestModel):
    title: str
    columns: List['ColumnCreateRequest']


@board_router.post("/new", status_code=200, dependencies=[Depends(check_token)])
async def create_board(board_req: BoardCreateRequest, session: SessionDep):
    board = Board(title=board_req.title,
                  columns=[Column(title=col.title, ord_num=col.order_number)
                           for col in board_req.columns]
                  )
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


@board_router.get("", status_code=200, dependencies=[Depends(check_token)])
async def get_boards_list(session: SessionDep) -> List[Board]:
    boards = session.exec(select(Board)).all()
    return boards


async def query_board(board_id: int, session: SessionDep) -> Board:
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(detail="Board not found", status_code=404)
    return board


@board_router.get("/{board_id}", status_code=200, dependencies=[Depends(check_token)])
async def get_board(board: Annotated[Board, Depends(query_board)]):
    columns = [{
        "boardId": col.board_id,
        "id": col.id,
        "orderNumber": col.ord_num,
        "title": col.title,
        "tasks": [{
            "title": t.title,
            "description": t.body,
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


@board_router.delete("/{board_id}", status_code=200, dependencies=[Depends(check_token)])
async def del_board(board: Annotated[Board, Depends(query_board)], session: SessionDep):
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


@board_router.put("/{board_id}", status_code=200, dependencies=[Depends(check_token)])
async def patch_board(new_board: BoardPatch, board: Annotated[Board, Depends(query_board)], session: SessionDep):
    board.title = new_board.title
    session.add(board)

    for c in new_board.columns:
        column = session.get(Column, c.id)
        if not column:
            raise HTTPException(status_code=404, detail="Column not found")
        column.title = c.title
        column.ord_num = c.order_number
        session.add(column)

        for t in c.tasks:
            task = session.get(Task, t.id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            task.title = t.title
            task.body = t.body
            task.ord_num = t.order_number
            session.add(task)

    session.commit()


task_router = APIRouter(prefix="/tasks")


class TaskCreateRequest(RestRequestModel):
    title: str
    description: str
    column_id: int


@task_router.post("/new", status_code=200, dependencies=[Depends(check_token)])
async def add_task(req: TaskCreateRequest, session: SessionDep):
    column = session.get(Column, req.column_id)
    column.tasks.append(Task(
        title=req.title,
        body=req.description,
    ))
    session.add(column)
    session.commit()


async def query_task(task_id: int, session: SessionDep) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(detail="Task not found", status_code=404)
    return task


@task_router.get("/{task_id}", status_code=200, dependencies=[Depends(check_token)])
async def get_task(task: Annotated[Task, Depends(query_task)]):
    return task


@task_router.delete("/{task_id}", status_code=200, dependencies=[Depends(check_token)])
async def del_task(task: Annotated[Task, Depends(query_task)], session: SessionDep):
    session.delete(task)
    session.commit()


class TaskPatchRequest(RestRequestModel):
    title: str = Field()
    description: str
    column_id: int


@task_router.put("/{task_id}", status_code=200, dependencies=[Depends(check_token)])
async def put_task(req: TaskPatchRequest, task: Annotated[Task, Depends(query_task)], session: SessionDep):
    task.title = req.title
    task.body = req.description
    task.col_id = req.column_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
