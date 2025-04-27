import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def token():
    """
    Fixture to sign up a new user and return its token for goals tests.
    """
    username = "goaluser"
    response = client.post("/api/signup", json={"username": username})
    assert response.status_code == 200
    return response.json()["token"]

def test_default_goals(token):
    """
    After signup, default goals from config should be set for the user.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Fetch metrics config to identify default goals
    config_resp = client.get("/api/metrics/config")
    assert config_resp.status_code == 200
    metrics = config_resp.json()
    default_metrics = [m for m in metrics if m.get("default_goal") is not None]
    if not default_metrics:
        pytest.skip("No default goals configured")
    # Fetch user goals
    get_resp = client.get("/api/goals", headers=headers)
    assert get_resp.status_code == 200
    goals = get_resp.json()
    assert isinstance(goals, list)
    goals_map = {g["metric_key"]: g for g in goals}
    for m in default_metrics:
        key = m["key"]
        default_goal = m["default_goal"]
        assert key in goals_map
        assert goals_map[key]["target_value"] == default_goal

def test_set_goal_success(token):
    """
    Setting a goal with a valid metric key should succeed and return the goal.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Choose a valid metric key
    config_resp = client.get("/api/metrics/config")
    assert config_resp.status_code == 200
    keys = [item["key"] for item in config_resp.json()]
    assert keys, "No metrics defined in config"
    metric_key = keys[0]
    target_value = 100.0
    payload = {"metric_key": metric_key, "target_value": target_value}
    resp = client.post("/api/goals", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("metric_key") == metric_key
    assert data.get("target_value") == target_value
    assert isinstance(data.get("id"), int)
    assert isinstance(data.get("user_id"), int)
    assert isinstance(data.get("created_at"), str)

def test_set_goal_invalid_metric_key(token):
    """
    Setting a goal with an invalid metric key should return 400 with hint of valid keys.
    """
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"metric_key": "invalid_key", "target_value": 50.0}
    resp = client.post("/api/goals", json=payload, headers=headers)
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data
    assert "hint" in data and isinstance(data["hint"], list)
    # Hint list should match configured keys
    config_resp = client.get("/api/metrics/config")
    valid_keys = [item["key"] for item in config_resp.json()]
    assert set(data["hint"]) == set(valid_keys)

def test_read_goals(token):
    """
    After setting multiple goals, GET /api/goals should return all user goals.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Set two distinct goals
    config_resp = client.get("/api/metrics/config")
    keys = [item["key"] for item in config_resp.json()]
    if len(keys) < 2:
        pytest.skip("Not enough metrics defined to test multiple goals")
    key1, key2 = keys[0], keys[1]
    val1, val2 = 10.0, 20.0
    # Create goals
    resp1 = client.post("/api/goals", json={"metric_key": key1, "target_value": val1}, headers=headers)
    assert resp1.status_code == 200
    resp2 = client.post("/api/goals", json={"metric_key": key2, "target_value": val2}, headers=headers)
    assert resp2.status_code == 200
    # Retrieve goals
    get_resp = client.get("/api/goals", headers=headers)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert isinstance(data, list)
    # Ensure at least the two goals exist
    metrics_returned = {item["metric_key"]: item for item in data}
    assert key1 in metrics_returned and key2 in metrics_returned
    assert metrics_returned[key1]["target_value"] == val1
    assert metrics_returned[key2]["target_value"] == val2