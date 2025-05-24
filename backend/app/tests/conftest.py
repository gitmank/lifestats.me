"""
Test configuration and fixtures.
"""
import os
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["TESTING"] = "true"

# Ensure the backend directory is on the import path for 'app' module
sys.path.insert(0, str(Path(__file__).parents[2]))

# Remove existing test database before any tests run
test_db_file = Path(__file__).parents[3] / "test.db"
if test_db_file.exists():
    test_db_file.unlink()

# Import app after setting environment variables
from app.main import app

# Disable rate limiting for tests
app.middleware_stack = None

@pytest.fixture(scope="session")
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture(autouse=True, scope="session")
def clean_db():
    """
    Clean up the test SQLite database after test session.
    """
    yield
    # Remove test database file after all tests
    test_db_file = Path(__file__).parents[3] / "test.db"
    if test_db_file.exists():
        test_db_file.unlink()