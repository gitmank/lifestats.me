"""
Clean up the test SQLite database before and after test session.
"""
from pathlib import Path
# Remove existing test database before any tests run
test_db_file = Path(__file__).parents[3] / "test.db"
if test_db_file.exists():
    test_db_file.unlink()
import os
import sys
import pytest
from pathlib import Path

# Ensure the backend directory is on the import path for 'app' module
sys.path.insert(0, str(Path(__file__).parents[2]))

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