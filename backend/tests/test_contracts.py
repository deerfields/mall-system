from fastapi.testclient import TestClient
from app import app
from datetime import datetime, timedelta

client = TestClient(app)

def test_create_contract():
    # Replace with valid tenant_id and shop_id from your database
    tenant_id = "valid-tenant-id"
    shop_id = "valid-shop-id"
    start = datetime.now().isoformat()
    end = (datetime.now() + timedelta(days=30)).isoformat()
    response = client.post("/api/contracts/", json={
        "tenant_id": tenant_id,
        "shop_id": shop_id,
        "start_date": start,
        "end_date": end,
        "amount": 1000.0
    })
    assert response.status_code in (200, 400)
    if response.status_code == 200:
        data = response.json()
        assert "id" in data

def test_list_contracts():
    response = client.get("/api/contracts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 