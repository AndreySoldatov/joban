from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sqlmodel import select
from app.db import SessionDep
from app.routers.tasks_db import Task
from app.routers.columns_db import Column
from typing import List

router = APIRouter()

# /{board_id}/{column_id}/{task_id}

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
