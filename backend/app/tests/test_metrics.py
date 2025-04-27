import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def token():
    """
    Fixture to sign up a new user and return its token.
    """
    username = "charlie"
    response = client.post("/api/signup", json={"username": username})
    assert response.status_code == 200
    return response.json()["token"]

def test_get_metrics_config():
    """
    GET /api/metrics/config should return available metrics.
    """
    response = client.get("/api/metrics/config")
    assert response.status_code == 200
    data = response.json()
    # Ensure at least the water_intake metric is present
    keys = {item["key"] for item in data}
    assert "water_intake" in keys
    assert "calorie_intake" in keys

def test_add_and_read_metric_entry(token):
    """
    Add a metric entry and verify it appears in the aggregated metrics.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Add a water intake entry
    payload = {"metric_key": "water_intake", "value": 750.5}
    post_resp = client.post("/api/metrics", json=payload, headers=headers)
    assert post_resp.status_code == 200
    entry = post_resp.json()
    assert entry["metric_key"] == payload["metric_key"]
    assert entry["value"] == payload["value"]
    assert isinstance(entry.get("id"), int)
    assert isinstance(entry.get("user_id"), int)

    # Read aggregated metrics
    get_resp = client.get("/api/metrics", headers=headers)
    assert get_resp.status_code == 200
    agg = get_resp.json()
    # The daily average for water_intake should equal the value added
    assert isinstance(agg, dict)
    assert agg.get("daily", {}).get("water_intake") == payload["value"]