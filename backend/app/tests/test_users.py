import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_signup_success():
    """
    Signing up a new user should return username and token.
    """
    response = client.post("/api/signup", json={"username": "alice"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert "token" in data and isinstance(data["token"], str) and data["token"]

def test_signup_duplicate():
    """
    Signing up the same user twice should fail with 400.
    """
    # First signup
    response1 = client.post("/api/signup", json={"username": "bob"})
    assert response1.status_code == 200
    # Duplicate signup
    response2 = client.post("/api/signup", json={"username": "bob"})
    assert response2.status_code == 400
    data = response2.json()
    assert data.get("detail") == "Username already exists"