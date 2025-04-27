from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel

class UserBase(SQLModel):
    username: str

class UserCreate(UserBase):
    pass

class UserSignup(UserBase):
    # Token (plaintext UUID4) returned on signup
    token: str

class UserRead(UserBase):
    id: int

class MetricConfig(SQLModel):
    key: str
    name: str
    unit: str

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
    
class APIKeyOut(SQLModel):
    """
    Response model for API key creation.
    """
    token: str

class APIKeyDelete(SQLModel):
    """
    Request model for deleting an API key.
    """
    token: str


class AggregatedMetrics(SQLModel):
    """
    Aggregated metric averages over predefined periods, returning null
    for metrics without entries.
    """
    daily: Dict[str, Optional[float]]
    weekly: Dict[str, Optional[float]]
    monthly: Dict[str, Optional[float]]
    quarterly: Dict[str, Optional[float]]
    yearly: Dict[str, Optional[float]]