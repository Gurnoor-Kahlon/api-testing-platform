def _register_and_login(client, email: str):
    client.post("/auth/register", json={"email": email, "full_name": "User "+email.split("@")[0], "password": "Password123"})
    login = client.post("/auth/login", json={"email": email, "password": "Password123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_project_crud_isolated_by_user(client):
    headers_a = _register_and_login(client, "a@example.com")
    headers_b = _register_and_login(client, "b@example.com")

    created = client.post("/projects", headers=headers_a, json={"name": "Project A", "description": "owned by A"})
    assert created.status_code == 201
    project_id = created.json()["id"]

    own_list = client.get("/projects", headers=headers_a)
    other_list = client.get("/projects", headers=headers_b)
    assert len(own_list.json()) == 1
    assert other_list.json() == []

    forbidden_view = client.get(f"/projects/{project_id}", headers=headers_b)
    assert forbidden_view.status_code == 404

    update = client.put(f"/projects/{project_id}", headers=headers_a, json={"name": "Updated"})
    assert update.status_code == 200
    assert update.json()["name"] == "Updated"

    delete = client.delete(f"/projects/{project_id}", headers=headers_a)
    assert delete.status_code == 204


def test_projects_require_auth(client):
    response = client.get("/projects")
    assert response.status_code == 401
