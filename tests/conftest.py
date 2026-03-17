import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import tasks_db


@pytest.fixture
def client():
    tasks_db.clear()
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer testtoken123"}