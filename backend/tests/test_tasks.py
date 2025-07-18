from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_task():
    # Replace with valid department_id from your database
    department_id = "valid-dept-id"
    response = client.post("/api/tasks/", json={
        "title": "Test Task",
        "description": "Sample",
        "department_id": department_id
    })
    assert response.status_code in (200, 401, 403)
    if response.status_code == 200:
        data = response.json()
        assert "id" in data

def test_list_tasks():
    response = client.get("/api/tasks/")
    assert response.status_code in (200, 401, 403) 