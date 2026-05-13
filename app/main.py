from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base
from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router
from app.routers.testruns import router as testruns_router
from app.routers.testsessions import router as testsessions_router
from app.routers.projects import router as projects_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "API Testing Platform is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(testruns_router)
app.include_router(testsessions_router)
app.include_router(projects_router)
