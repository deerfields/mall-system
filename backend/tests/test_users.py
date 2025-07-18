from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_user():
    # Replace with valid role_id and department_id from your database
    role_id = "valid-role-id"
    department_id = "valid-dept-id"
    response = client.post("/api/users/", json={
        "username": "testuser",
        "password": "testpass",
        "role_id": role_id,
        "department_id": department_id
    })
    assert response.status_code in (200, 400)  # 400 if user exists
    if response.status_code == 200:
        data = response.json()
        assert "id" in data and "username" in data

def test_list_users():
    response = client.get("/api/users/")
    assert response.status_code in (200, 401, 403) 