from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sqlmodel import select
from sqlalchemy import delete

from app.db import SessionDep
from app.routers.boards_db import Task
from typing import List

router = APIRouter()

create_task_responses = {
    "200": {"description": "Task created successfully"},
}

# TODO: col_id приходит в body


@router.post("/boards/{board_id}/task", status_code=200, responses=create_task_responses)
async def create_task(board_id: int, col_id: int, task: Task, session: SessionDep):
    query = select(Task).where(
        Task.title == task.title, Task.col_id == task.col_id)
    db_task = session.exec(query).first()

    task.col_id = col_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

get_task_responses = {
    "200": {"description": "Task list received"},
}
# TODO:удалить


@router.get("/boards/{board_id}/{col_id}/get_tasks_list", status_code=200, responses=create_task_responses)
async def get_tasks_list(session: SessionDep) -> List[Task]:
    query = select(Task)
    task = session.exec(query).all()
    return task

# TODO:удалить


@router.delete("/boards/{board_id}/{col_id}/delete_all_tasks", status_code=204)
async def delete_all_tasks_by_column(col_id: int, session: SessionDep) -> None:
    query = delete(Task).where(Task.col_id == col_id)
    result = session.execute(query)
    session.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail="No tasks found for the given column")

# TODO:"/boards/{board_id}/tasks/{task_id}"


@router.delete("/boards/{board_id}/{col_id}/{task_id}/delete_task", status_code=204)
async def delete_task_by_id(task_id: int, session: SessionDep) -> None:
    query = select(Task).where(Task.id == task_id)
    task = session.exec(query).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    delete_query = delete(Task).where(Task.id == task_id)
    session.execute(delete_query)
    session.commit()

    return {"detail": f"Task '{task.title}' has been deleted successfully."}
