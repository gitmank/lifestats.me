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
    # Response should be a non-empty list of metrics with key, name, and unit fields
    assert isinstance(data, list) and data, "Metrics config should be a non-empty list"
    for item in data:
        assert "key" in item and "name" in item and "unit" in item, "Each metric must have key, name, and unit"

def test_add_and_read_metric_entry(token):
    """
    Add a metric entry and verify it appears in the aggregated metrics.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Choose a valid metric key from config and add an entry
    config_resp = client.get("/api/metrics/config")
    assert config_resp.status_code == 200
    keys = [item["key"] for item in config_resp.json()]
    assert keys, "No metrics defined in config"
    metric_key = keys[0]
    payload = {"metric_key": metric_key, "value": 750.5}
    post_resp = client.post("/api/metrics", json=payload, headers=headers)
    assert post_resp.status_code == 200
    entry = post_resp.json()
    assert entry["metric_key"] == metric_key
    assert entry["value"] == payload["value"]
    assert isinstance(entry.get("id"), int)
    assert isinstance(entry.get("user_id"), int)

    # Read aggregated metrics
    get_resp = client.get("/api/metrics", headers=headers)
    assert get_resp.status_code == 200
    agg = get_resp.json()
    # The daily average for the metric should equal the value added
    assert isinstance(agg, dict)
    daily = agg.get("daily", {})
    assert daily.get("average_values", {}).get(metric_key) == payload["value"]
    
def test_add_invalid_metric_key(token):
    """
    Posting a metric with a key not in config should return 400 with hint of valid keys.
    """
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"metric_key": "invalid_key", "value": 123.45}
    resp = client.post("/api/metrics", json=payload, headers=headers)
    assert resp.status_code == 400
    data = resp.json()
    # Error detail and hint should be present
    assert "detail" in data
    assert "hint" in data
    assert isinstance(data["hint"], list)
    # The hint list should match the configured metric keys
    config_resp = client.get("/api/metrics/config")
    valid_keys = [item["key"] for item in config_resp.json()]
    assert set(data["hint"]) == set(valid_keys)
    
def test_sum_multiple_entries_same_day(token):
    """
    Multiple entries for the same metric on the same day should be summed in the daily aggregate.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Choose a metric key different from the one used in test_add_and_read_metric_entry
    config_resp = client.get("/api/metrics/config")
    assert config_resp.status_code == 200
    keys = [item["key"] for item in config_resp.json()]
    assert len(keys) >= 2, "Need at least two metrics defined to run this test"
    # Avoid the first key used previously
    metric = keys[1]
    val1 = 2.5
    val2 = 1.5
    # Post two entries
    resp1 = client.post("/api/metrics", json={"metric_key": metric, "value": val1}, headers=headers)
    assert resp1.status_code == 200
    resp2 = client.post("/api/metrics", json={"metric_key": metric, "value": val2}, headers=headers)
    assert resp2.status_code == 200
    # Retrieve aggregated metrics
    get_resp = client.get("/api/metrics", headers=headers)
    assert get_resp.status_code == 200
    agg = get_resp.json()
    # The daily average (sum over 1 day) should equal the sum of both values
    daily = agg.get("daily", {})
    assert daily.get("average_values", {}).get(metric) == val1 + val2