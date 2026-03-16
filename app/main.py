from fastapi import FastAPI
from app.routes.tasks import router as tasks_router

app = FastAPI(title="Automated API Testing Platform")


@app.get("/")
def read_root():
    return {"message": "API Testing Platform is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(tasks_router)