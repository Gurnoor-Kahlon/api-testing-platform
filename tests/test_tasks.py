from fastapi.testclient import TestClient
from app.main import app
from app.database import tasks_db

client = TestClient(app)


def setup_function():
    tasks_db.clear()


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Learn PyTest",
            "description": "Write API tests"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Learn PyTest"
    assert data["description"] == "Write API tests"
    assert data["completed"] is False


def test_get_all_tasks():
    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "First task"
        }
    )

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"


def test_get_task_by_id():
    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "First task"
        }
    )

    response = client.get("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Task 1"


def test_get_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_task():
    client.post(
        "/tasks",
        json={
            "title": "Old title",
            "description": "Old description"
        }
    )

    response = client.put(
        "/tasks/1",
        json={
            "title": "New title",
            "description": "New description",
            "completed": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["description"] == "New description"
    assert data["completed"] is True


def test_update_task_not_found():
    response = client.put(
        "/tasks/999",
        json={
            "title": "New title",
            "description": "New description",
            "completed": True
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_task():
    client.post(
        "/tasks",
        json={
            "title": "Delete me",
            "description": "Temporary task"
        }
    )

    response = client.delete("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task deleted"
    assert data["task"]["id"] == 1


def test_delete_task_not_found():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_create_task_invalid_title():
    response = client.post(
        "/tasks",
        json={
            "title": "",
            "description": "Valid description"
        }
    )
    assert response.status_code == 422


def test_create_task_invalid_description():
    response = client.post(
        "/tasks",
        json={
            "title": "Valid title",
            "description": ""
        }
    )
    assert response.status_code == 422