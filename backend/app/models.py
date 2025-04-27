from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DateTime, Index, String

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    metrics: List["MetricEntry"] = Relationship(back_populates="user")
    api_keys: List["APIKey"] = Relationship(back_populates="user")
    # User-defined goals for tracked metrics
    goals: List["Goal"] = Relationship(back_populates="user")

class MetricEntry(SQLModel, table=True):
    __table_args__ = (
        Index("ix_metric_user_timestamp", "user_id", "timestamp"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    metric_key: str = Field(index=True)
    value: float
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True),
        default_factory=datetime.utcnow,
    )
    user: Optional[User] = Relationship(back_populates="metrics")

class APIKey(SQLModel, table=True):
    """
    User API keys for authentication.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    key_hash: str = Field(
        sa_column=Column(String, index=True, nullable=False)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[User] = Relationship(back_populates="api_keys")

class Goal(SQLModel, table=True):
    """
    User-defined goals for specific metrics.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    metric_key: str = Field(index=True)
    target_value: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationship back to the user
    user: Optional[User] = Relationship(back_populates="goals")