"""
Database engine and session management.
"""
import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
# File-based SQLite database stored at backend/life_metrics.db by default.
# Override via DATABASE_URL env var (full SQLAlchemy URL).
DB_FILE = Path(__file__).parent.parent / "life_metrics.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DB_FILE.resolve()}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create database and tables on import to ensure schema exists
# Import models to register them in metadata
import app.models  # noqa: F401
SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency for FastAPI to get a database session.
    Ensures that database schema is created before obtaining a session.
    """
    # Ensure tables exist (in case of missing or removed DB file)
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session