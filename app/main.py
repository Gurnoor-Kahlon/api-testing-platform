from fastapi import FastAPI

from app.database import Base, engine
from app.routes.tasks import router as tasks_router
from app.routes.auth import router as auth_router
from app.routes.testruns import router as testruns_router

app = FastAPI(title="Automated API Testing Platform")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "API Testing Platform is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Register routers (keep them together)
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(testruns_router)