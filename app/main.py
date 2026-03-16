from fastapi import FastAPI, HTTPException
from app.models import TaskCreate, TaskUpdate, Task
from app.database import tasks_db

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "API Testing Platform is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def get_tasks():
    return tasks_db


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.title,
        "description": task.description,
        "completed": False
    }
    tasks_db.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskUpdate):
    for task in tasks_db:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["description"] = updated_task.description
            task["completed"] = updated_task.completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            deleted_task = tasks_db.pop(index)
            return {"message": "Task deleted", "task": deleted_task}
    raise HTTPException(status_code=404, detail="Task not found")