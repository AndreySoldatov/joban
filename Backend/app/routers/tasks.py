from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sqlmodel import select
from app.db import SessionDep
from app.routers.tasks_db import Task
from app.routers.columns_db import Column
from typing import List

router = APIRouter()

create_task_responses = {
    "200": {"description": "Task created successfully"},
}

@router.post("/boards/{board_id}/{col_id}/create_task", status_code=200, responses=create_task_responses)
async def create_task(board_id: int, col_id: int, task: Task, session: SessionDep):
    query = select(Task).where(Task.title == task.title, Task.col_id == task.col_id)
    db_task = session.exec(query).first()

    task.col_id = col_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

get_task_responses = {
    "200": {"description": "Task list received"},
}
@router.get("/boards/{board_id}/{col_id}/get_tasks_list", status_code=200, responses=create_task_responses)
async def get_tasks_list(session: SessionDep) -> List[Task]:
    query = select(Task)
    task = session.exec(query).all()
    return task