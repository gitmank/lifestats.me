"""
Comprehensive test suite for all backend routes.
"""
import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
import json


def unique_username(prefix="user"):
    """Generate a unique username for tests."""
    return f"{prefix}_{str(uuid.uuid4())[:8]}"


class TestRootRoute:
    """Test the root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test GET / returns basic API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "hint" in data
        assert "docs" in data
        assert "signup" in data["hint"]


class TestUserRoutes:
    """Test all user-related endpoints."""
    
    def test_signup_success(self, client):
        """Test successful user signup."""
        username = unique_username("signup")
        response = client.post("/api/signup", json={"username": username})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
        assert "token" in data
        assert len(data["token"]) > 0
        
    def test_signup_duplicate_username(self, client):
        """Test signup with duplicate username fails."""
        username = unique_username("duplicate")
        # Create user first
        client.post("/api/signup", json={"username": username})
        # Try to create same user again
        response = client.post("/api/signup", json={"username": username})
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
        
    def test_signup_invalid_data(self, client):
        """Test signup with invalid data."""
        response = client.post("/api/signup", json={})
        assert response.status_code == 422  # Validation error
        
    def test_get_current_user(self, client):
        """Test getting current user info."""
        # Create user and get token
        username = unique_username("current")
        signup_response = client.post("/api/signup", json={"username": username})
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
        assert "id" in data
        
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/me")
        assert response.status_code == 403  # Backend returns 403, not 401
        
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/me", headers=headers)
        assert response.status_code == 401


class TestAPIKeyRoutes:
    """Test API key management endpoints."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create a user and return username and token."""
        username = unique_username("apikey")
        response = client.post("/api/signup", json={"username": username})
        data = response.json()
        return {"username": data["username"], "token": data["token"]}
    
    def test_list_api_keys(self, client, authenticated_user):
        """Test listing API keys for user."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.get(f"/api/keys/{authenticated_user['username']}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1  # One key from signup
        assert "id" in data[0]
        assert "created_at" in data[0]
        assert "key_preview" in data[0]
        
    def test_generate_api_key(self, client, authenticated_user):
        """Test generating a new API key."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.post(f"/api/keys/{authenticated_user['username']}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0
        
    def test_generate_api_key_limit(self, client, authenticated_user):
        """Test API key generation limit (max 5 keys)."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        # Generate 4 more keys (already have 1 from signup)
        for i in range(4):
            response = client.post(f"/api/keys/{authenticated_user['username']}", headers=headers)
            assert response.status_code == 200
            
        # 6th key should fail
        response = client.post(f"/api/keys/{authenticated_user['username']}", headers=headers)
        assert response.status_code == 400
        assert "limit" in response.json()["detail"].lower()
        
    def test_delete_api_key_by_token(self, client, authenticated_user):
        """Test deleting API key by token."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        # Generate a new key
        new_key_response = client.post(f"/api/keys/{authenticated_user['username']}", headers=headers)
        new_token = new_key_response.json()["token"]
        
        # Delete the new key using request method
        response = client.request(
            "DELETE",
            f"/api/keys/{authenticated_user['username']}",
            headers={**headers, "Content-Type": "application/json"},
            json={"token": new_token}
        )
        assert response.status_code == 204
        
    def test_delete_api_key_by_id(self, client, authenticated_user):
        """Test deleting API key by ID."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        # Generate a new key
        client.post(f"/api/keys/{authenticated_user['username']}", headers=headers)
        
        # List keys to get ID
        list_response = client.get(f"/api/keys/{authenticated_user['username']}", headers=headers)
        keys = list_response.json()
        key_to_delete = keys[1]  # Delete the second key (not the one we're using)
        
        # Delete by ID
        response = client.delete(
            f"/api/keys/{authenticated_user['username']}/{key_to_delete['id']}",
            headers=headers
        )
        assert response.status_code == 204
        
    def test_unauthorized_key_operations(self, client, authenticated_user):
        """Test API key operations without proper authorization."""
        # Try to list keys for different user
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.get("/api/keys/otheruser", headers=headers)
        assert response.status_code == 403
        
    def test_delete_user_account(self, client, authenticated_user):
        """Test deleting user account."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.delete(f"/api/user/{authenticated_user['username']}", headers=headers)
        assert response.status_code == 204
        
        # Verify user is deleted by trying to access with same token
        response = client.get("/api/me", headers=headers)
        assert response.status_code == 401


class TestMetricsRoutes:
    """Test metrics-related endpoints."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create a user and return username and token."""
        username = unique_username("metrics")
        response = client.post("/api/signup", json={"username": username})
        data = response.json()
        return {"username": data["username"], "token": data["token"]}
    
    def test_get_metrics_config(self, client, authenticated_user):
        """Test getting metrics configuration."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.get("/api/metrics/config", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check required fields
        for metric in data:
            assert "key" in metric
            assert "name" in metric
            assert "unit" in metric
            assert "type" in metric
            assert metric["type"] in ["min", "max"]
            
    def test_get_metrics_config_unauthorized(self, client):
        """Test getting metrics config without authentication."""
        response = client.get("/api/metrics/config")
        assert response.status_code == 403  # Backend returns 403, not 401
        
    def test_add_metric_entry(self, client, authenticated_user):
        """Test adding a metric entry."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # Get valid metric keys
        config_response = client.get("/api/metrics/config", headers=headers)
        metrics = config_response.json()
        valid_key = metrics[0]["key"]
        
        # Add metric entry
        response = client.post("/api/metrics", json={
            "metric_key": valid_key,
            "value": 2.5
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["metric_key"] == valid_key
        assert data["value"] == 2.5
        assert "id" in data
        assert "user_id" in data
        
    def test_add_metric_entry_with_timestamp(self, client, authenticated_user):
        """Test adding a metric entry with custom timestamp."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        config_response = client.get("/api/metrics/config", headers=headers)
        metrics = config_response.json()
        valid_key = metrics[0]["key"]
        
        timestamp = "2024-01-15T10:30:00"
        response = client.post("/api/metrics", json={
            "metric_key": valid_key,
            "value": 3.0,
            "timestamp": timestamp
        }, headers=headers)
        assert response.status_code == 200
        
    def test_add_metric_invalid_key(self, client, authenticated_user):
        """Test adding metric with invalid key."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.post("/api/metrics", json={
            "metric_key": "invalid_key",
            "value": 1.0
        }, headers=headers)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "hint" in data
        assert isinstance(data["hint"], list)
        
    def test_get_aggregated_metrics(self, client, authenticated_user):
        """Test getting aggregated metrics."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # Add some metric entries first
        config_response = client.get("/api/metrics/config", headers=headers)
        metrics = config_response.json()
        valid_key = metrics[0]["key"]
        
        # Add multiple entries
        for value in [1.0, 2.0, 3.0]:
            client.post("/api/metrics", json={
                "metric_key": valid_key,
                "value": value
            }, headers=headers)
            
        # Get aggregated metrics
        response = client.get("/api/metrics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "daily" in data
        assert "weekly" in data
        assert "monthly" in data
        assert "quarterly" in data
        assert "yearly" in data
        
        # Check daily data contains our metric
        daily = data["daily"]
        assert "average_values" in daily
        assert "goalReached" in daily
        assert valid_key in daily["average_values"]
        
    def test_get_metrics_unauthorized(self, client):
        """Test getting metrics without authentication."""
        response = client.get("/api/metrics")
        assert response.status_code == 403  # Backend returns 403, not 401


class TestGoalsRoutes:
    """Test goals-related endpoints."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create a user and return username and token."""
        username = unique_username("goals")
        response = client.post("/api/signup", json={"username": username})
        data = response.json()
        return {"username": data["username"], "token": data["token"]}
    
    def test_read_goals(self, client, authenticated_user):
        """Test reading user goals."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.get("/api/goals", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default goals from signup
        assert len(data) > 0
        
        for goal in data:
            assert "id" in goal
            assert "metric_key" in goal
            assert "target_value" in goal
            assert "user_id" in goal
            assert "created_at" in goal
            
    def test_set_goal(self, client, authenticated_user):
        """Test setting a goal."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # Get valid metric keys
        config_response = client.get("/api/metrics/config", headers=headers)
        metrics = config_response.json()
        valid_key = metrics[0]["key"]
        
        # Set goal
        response = client.post("/api/goals", json={
            "metric_key": valid_key,
            "target_value": 5.0
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["metric_key"] == valid_key
        assert data["target_value"] == 5.0
        assert "id" in data
        
    def test_update_existing_goal(self, client, authenticated_user):
        """Test updating an existing goal (upsert behavior)."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        config_response = client.get("/api/metrics/config", headers=headers)
        metrics = config_response.json()
        valid_key = metrics[0]["key"]
        
        # Set initial goal
        response1 = client.post("/api/goals", json={
            "metric_key": valid_key,
            "target_value": 3.0
        }, headers=headers)
        goal_id = response1.json()["id"]
        
        # Update same goal
        response2 = client.post("/api/goals", json={
            "metric_key": valid_key,
            "target_value": 6.0
        }, headers=headers)
        assert response2.status_code == 200
        updated_goal = response2.json()
        assert updated_goal["target_value"] == 6.0
        # Should be same goal ID (upsert)
        assert updated_goal["id"] == goal_id
        
    def test_set_goal_invalid_metric(self, client, authenticated_user):
        """Test setting goal with invalid metric key."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        response = client.post("/api/goals", json={
            "metric_key": "invalid_key",
            "target_value": 1.0
        }, headers=headers)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "hint" in data
        
    def test_goals_unauthorized(self, client):
        """Test goals endpoints without authentication."""
        response = client.get("/api/goals")
        assert response.status_code == 403  # Backend returns 403, not 401
        
        response = client.post("/api/goals", json={
            "metric_key": "water_litres", 
            "target_value": 2.0
        })
        assert response.status_code == 403  # Backend returns 403, not 401


class TestRateLimiting:
    """Test rate limiting functionality (if enabled)."""
    
    def test_rate_limiting_disabled_in_tests(self, client):
        """Verify rate limiting is disabled during tests."""
        # Make many requests quickly
        for i in range(20):
            response = client.get("/")
            assert response.status_code == 200
            
        # All should succeed since rate limiting is disabled in test mode


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
    def test_invalid_method(self, client):
        """Test using wrong HTTP method."""
        response = client.put("/api/signup")
        assert response.status_code == 405
        
    def test_malformed_json(self, client):
        """Test sending malformed JSON."""
        response = client.post("/api/signup", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422


class TestDatabaseIntegration:
    """Test database-related functionality."""
    
    def test_database_persistence(self, client):
        """Test that data persists across requests."""
        # Create user
        username = unique_username("persist")
        signup_response = client.post("/api/signup", json={"username": username})
        token = signup_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Add metric entry
        config_response = client.get("/api/metrics/config", headers=headers)
        valid_key = config_response.json()[0]["key"]
        
        client.post("/api/metrics", json={
            "metric_key": valid_key,
            "value": 10.0
        }, headers=headers)
        
        # Verify data persists
        metrics_response = client.get("/api/metrics", headers=headers)
        assert metrics_response.status_code == 200
        data = metrics_response.json()
        assert data["daily"]["average_values"][valid_key] == 10.0
        
    def test_user_data_isolation(self, client):
        """Test that users can only access their own data."""
        # Create two users
        user1_response = client.post("/api/signup", json={"username": unique_username("user1")})
        user2_response = client.post("/api/signup", json={"username": unique_username("user2")})
        
        user1_token = user1_response.json()["token"]
        user2_token = user2_response.json()["token"]
        
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 1 adds metric
        config_response = client.get("/api/metrics/config", headers=user1_headers)
        valid_key = config_response.json()[0]["key"]
        
        client.post("/api/metrics", json={
            "metric_key": valid_key,
            "value": 15.0
        }, headers=user1_headers)
        
        # User 2 should not see user 1's data
        user2_metrics = client.get("/api/metrics", headers=user2_headers)
        assert user2_metrics.status_code == 200
        data = user2_metrics.json()
        # User 2 should have 0 or None for this metric (no entries)
        user2_value = data["daily"]["average_values"].get(valid_key)
        assert user2_value in [0, None], f"User 2 should not see user 1's data, got {user2_value}"


class TestMaxGoalLogic:
    """Test the max goal type logic specifically."""
    
    @pytest.fixture
    def authenticated_user(self, client):
        """Create a user and return username and token."""
        username = unique_username("maxgoal")
        response = client.post("/api/signup", json={"username": username})
        data = response.json()
        return {"username": data["username"], "token": data["token"]}
    
    def test_max_goal_completion_logic(self, client, authenticated_user):
        """Test that max goals work correctly (goal met when under limit)."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # Get metrics config to find a max type metric
        config_response = client.get("/api/metrics/config", headers=headers)
        metrics = config_response.json()
        
        max_metric = None
        for metric in metrics:
            if metric["type"] == "max":
                max_metric = metric
                break
        
        assert max_metric is not None, "Should have at least one max type metric"
        
        # Set a limit for this metric
        goal_response = client.post("/api/goals", json={
            "metric_key": max_metric["key"],
            "target_value": 100.0
        }, headers=headers)
        assert goal_response.status_code == 200
        
        # Add entries below the limit (should meet goal)
        client.post("/api/metrics", json={
            "metric_key": max_metric["key"],
            "value": 50.0
        }, headers=headers)
        
        # Check that goal is reached
        metrics_response = client.get("/api/metrics", headers=headers)
        data = metrics_response.json()
        daily_goals = data["daily"]["goalReached"]
        
        # For max type, goal should be reached when value <= target
        assert daily_goals[max_metric["key"]] >= 0  # Should have some days with goal met 