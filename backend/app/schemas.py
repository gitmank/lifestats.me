from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel

class UserBase(SQLModel):
    username: str

class UserCreate(UserBase):
    pass

class UserSignup(UserBase):
    # Token (plaintext UUID4) returned on signup
    token: str
    hint: str = "Use this token in the Authorization header as 'Bearer {token}'"

class UserRead(UserBase):
    id: int

class MetricConfig(SQLModel):
    key: str
    name: str
    unit: str
    # Optional default goal value for this metric (from config)
    default_goal: Optional[float] = None
    goal: Optional[float] = None

class MetricEntryBase(SQLModel):
    metric_key: str
    value: float
    # Optional timestamp; server will use current time if not provided
    timestamp: Optional[datetime] = None

class MetricEntryCreate(MetricEntryBase):
    pass

class MetricEntryRead(MetricEntryBase):
    id: int
    user_id: int
    hint: str = "Use GET /api/metrics to view your aggregated metrics"
    
class APIKeyOut(SQLModel):
    """
    Response model for API key creation.
    """
    token: str
    hint: str = "Use this token in the Authorization header as 'Bearer {token}'"

class APIKeyDelete(SQLModel):
    """
    Request model for deleting an API key.
    """
    token: str
    
class GoalBase(SQLModel):
    """
    Base schema for a user-defined goal.
    """
    metric_key: str
    target_value: float

class GoalCreate(GoalBase):
    """
    Schema for creating a new goal.
    """
    pass

class GoalRead(GoalBase):
    """
    Schema for reading a user-defined goal.
    """
    id: int
    user_id: int
    created_at: datetime
    hint: str = "Use GET/POST /api/goals to view or set goals"
 

class AggregatedMetrics(SQLModel):
    """
    Aggregated metric averages over predefined periods, returning null
    for metrics without entries.
    """
    # Aggregation for each period includes metric averages, weekly daily_totals, and nested goalReached counts
    daily: Dict[str, Any]
    # Weekly aggregation includes average per day, daily_totals, and goalReached
    weekly: Dict[str, Any]
    monthly: Dict[str, Any]
    quarterly: Dict[str, Any]
    yearly: Dict[str, Any]
    hint: str = "Use POST /api/metrics to add new measurement entries"