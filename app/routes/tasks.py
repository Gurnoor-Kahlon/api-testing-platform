from fastapi import APIRouter, HTTPException
from app.models import TaskCreate, TaskUpdate, Task
from app.database import tasks_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[Task])
def get_tasks():
    return tasks_db


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.title,
        "description": task.description,
        "completed": False,
    }
    tasks_db.append(new_task)
    return new_task


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskUpdate):
    for task in tasks_db:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["description"] = updated_task.description
            task["completed"] = updated_task.completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            deleted_task = tasks_db.pop(index)
            return {"message": "Task deleted", "task": deleted_task}
    raise HTTPException(status_code=404, detail="Task not found")