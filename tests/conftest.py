import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from tests.report_results import send_test_result

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_app.db")

if TEST_DATABASE_URL.startswith("sqlite"):
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"email": "owner@example.com", "full_name": "Owner User", "password": "Password123"})
    login_response = client.post("/auth/login", json={"email": "owner@example.com", "password": "Password123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        if "tests/selenium/" in item.nodeid:
            return
        if os.getenv("DISABLE_RESULT_REPORTING") == "1":
            return
        send_test_result(item.name, "passed" if report.passed else "failed", report.duration)
