from fastapi import FastAPI
from app.routes.tasks import router as tasks_router
from app.routes.auth import router as auth_router

app = FastAPI(title="Automated API Testing Platform")


@app.get("/")
def read_root():
    return {"message": "API Testing Platform is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(tasks_router)