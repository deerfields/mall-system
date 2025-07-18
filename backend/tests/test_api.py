from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_task():
    response = client.post("/api/tasks", json={"title": "Test Task"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
    assert "status" in data

def test_get_tasks():
    # First, create a task to ensure at least one exists
    client.post("/api/tasks", json={"title": "Another Task"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(task["title"] == "Another Task" for task in data) 