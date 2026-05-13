def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
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


def test_get_all_tasks(client, auth_headers):
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Task 1",
            "description": "First task"
        }
    )

    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"


def test_get_task_by_id(client, auth_headers):
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Task 1",
            "description": "First task"
        }
    )

    response = client.get("/tasks/1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Task 1"


def test_get_task_not_found(client, auth_headers):
    response = client.get("/tasks/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_task(client, auth_headers):
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Old title",
            "description": "Old description"
        }
    )

    response = client.put(
        "/tasks/1",
        headers=auth_headers,
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


def test_update_task_not_found(client, auth_headers):
    response = client.put(
        "/tasks/999",
        headers=auth_headers,
        json={
            "title": "New title",
            "description": "New description",
            "completed": True
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_task(client, auth_headers):
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Delete me",
            "description": "Temporary task"
        }
    )

    response = client.delete("/tasks/1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task deleted"
    assert data["task"]["id"] == 1


def test_delete_task_not_found(client, auth_headers):
    response = client.delete("/tasks/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_invalid_title(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "",
            "description": "Valid description"
        }
    )
    assert response.status_code == 422


def test_create_task_invalid_description(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Valid title",
            "description": ""
        }
    )
    assert response.status_code == 422


def test_tasks_requires_auth_header(client):
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_tasks_rejects_invalid_token(client):
    response = client.get(
        "/tasks",
        headers={"Authorization": "Bearer wrongtoken"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}