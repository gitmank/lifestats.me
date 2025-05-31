from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from .models import User, MetricEntry, APIKey, Goal, UserMetricsConfig
from .config import config
import logging

def create_user(session: Session, username: str) -> User:
    """
    Create a new user with the given username.
    """
    logging.info(f"create_user called with username={username}")
    user = User(username=username)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Initialize user with default metrics configuration
    initialize_user_metrics_config(session, user.id)
    
    return user
    
def initialize_user_metrics_config(session: Session, user_id: int) -> None:
    """
    Initialize a user's metrics configuration with default values from the global config.
    """
    logging.info(f"initialize_user_metrics_config called for user_id={user_id}")
    
    default_metrics = config.get_metrics()
    for metric in default_metrics:
        user_config = UserMetricsConfig(
            user_id=user_id,
            metric_key=metric["key"],
            metric_name=metric["name"],
            unit=metric["unit"],
            type=metric["type"],
            goal=metric.get("goal"),
            default_goal=metric.get("default_goal"),
            is_active=True
        )
        session.add(user_config)
    
    session.commit()

def create_api_key(session: Session, user_id: int, key_hash: str) -> APIKey:
    """
    Create a new API key for the given user.
    """
    logging.info(f"create_api_key called for user_id={user_id}")
    api_key = APIKey(user_id=user_id, key_hash=key_hash)
    session.add(api_key)
    session.commit()
    session.refresh(api_key)
    return api_key

def revoke_api_key(session: Session, user_id: int, key_hash: str) -> None:
    """
    Revoke (delete) the API key matching the given hash for the user.
    """
    logging.info(f"revoke_api_key called for user_id={user_id}, key_hash={key_hash}")
    statement = select(APIKey).where(
        APIKey.user_id == user_id,
        APIKey.key_hash == key_hash,
    )
    api_key = session.exec(statement).first()
    if api_key:
        session.delete(api_key)
        session.commit()

def get_user_by_token_hash(session: Session, token_hash: str) -> Optional[User]:
    """
    Retrieve the User associated with the given API key hash.
    """
    logging.info(f"get_user_by_token_hash called with token_hash={token_hash}")
    statement = select(User).join(APIKey).where(APIKey.key_hash == token_hash)
    return session.exec(statement).first()

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    logging.info(f"get_user_by_username called with username={username}")
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def get_user_api_keys(session: Session, user_id: int) -> List[APIKey]:
    """
    Retrieve all API keys for the given user.
    """
    logging.info(f"get_user_api_keys called for user_id={user_id}")
    statement = select(APIKey).where(APIKey.user_id == user_id).order_by(APIKey.created_at.desc())
    return session.exec(statement).all()

def delete_user(session: Session, user_id: int) -> None:
    """
    Delete a user and all associated data (API keys, metrics, goals, metrics config).
    """
    logging.info(f"delete_user called for user_id={user_id}")
    
    # Delete all API keys
    statement = select(APIKey).where(APIKey.user_id == user_id)
    api_keys = session.exec(statement).all()
    for key in api_keys:
        session.delete(key)
    
    # Delete all metric entries
    statement = select(MetricEntry).where(MetricEntry.user_id == user_id)
    metrics = session.exec(statement).all()
    for metric in metrics:
        session.delete(metric)
    
    # Delete all goals
    statement = select(Goal).where(Goal.user_id == user_id)
    goals = session.exec(statement).all()
    for goal in goals:
        session.delete(goal)
    
    # Delete all user metrics config
    statement = select(UserMetricsConfig).where(UserMetricsConfig.user_id == user_id)
    metrics_configs = session.exec(statement).all()
    for config in metrics_configs:
        session.delete(config)
    
    # Delete the user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if user:
        session.delete(user)
    
    session.commit()

def create_metric_entry(
    session: Session,
    user_id: int,
    metric_key: str,
    value: float,
    timestamp: datetime,
) -> MetricEntry:
    logging.info(f"create_metric_entry called for user_id={user_id}, metric_key={metric_key}, value={value}, timestamp={timestamp}")
    entry = MetricEntry(
        user_id=user_id,
        metric_key=metric_key,
        value=value,
        timestamp=timestamp,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

def get_user_metrics(
    session: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[MetricEntry]:
    logging.info(f"get_user_metrics called for user_id={user_id}, start_date={start_date}, end_date={end_date}")
    statement = select(MetricEntry).where(MetricEntry.user_id == user_id)
    if start_date:
        statement = statement.where(MetricEntry.timestamp >= start_date)
    if end_date:
        statement = statement.where(MetricEntry.timestamp <= end_date)
    statement = statement.order_by(MetricEntry.timestamp)
    return session.exec(statement).all()
 
def create_goal(
    session: Session,
    user_id: int,
    metric_key: str,
    target_value: float,
) -> Goal:
    """
    Create a new goal for the given user and metric.
    """
    logging.info(f"create_goal called for user_id={user_id}, metric_key={metric_key}, target_value={target_value}")
    goal = Goal(
        user_id=user_id,
        metric_key=metric_key,
        target_value=target_value,
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

def get_user_goals(
    session: Session,
    user_id: int,
) -> List[Goal]:
    """
    Retrieve all goals set by the user.
    """
    logging.info(f"get_user_goals called for user_id={user_id}")
    statement = select(Goal).where(Goal.user_id == user_id)
    return session.exec(statement).all()
 
def create_default_goals(
    session: Session,
    user_id: int,
) -> List[Goal]:
    """
    Create default goals for the given user based on metrics config.
    """
    logging.info(f"create_default_goals called for user_id={user_id}")
    created_goals: List[Goal] = []
    metrics = config.get_metrics()
    for m in metrics:
        default_goal = m.get("default_goal")
        if default_goal is not None:
            goal = create_goal(session, user_id, m["key"], default_goal)
            created_goals.append(goal)
    return created_goals

def upsert_goal(
    session: Session,
    user_id: int,
    metric_key: str,
    target_value: float,
) -> Goal:
    """
    Insert or update a goal for the given user and metric.
    If a goal exists, update its target_value and timestamp; otherwise create a new goal.
    """
    logging.info(f"upsert_goal called for user_id={user_id}, metric_key={metric_key}, target_value={target_value}")
    # Check for existing goal
    statement = select(Goal).where(
        Goal.user_id == user_id,
        Goal.metric_key == metric_key,
    )
    existing = session.exec(statement).first()
    if existing:
        existing.target_value = target_value
        existing.created_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    # No existing goal; create a new one
    return create_goal(session, user_id, metric_key, target_value)

def get_last_entries(session: Session, user_id: int, limit: int = 5) -> List[MetricEntry]:
    """
    Get the last N entries for the given user, ordered by timestamp descending.
    """
    logging.info(f"get_last_entries called for user_id={user_id}, limit={limit}")
    statement = select(MetricEntry).where(MetricEntry.user_id == user_id).order_by(MetricEntry.timestamp.desc()).limit(limit)
    return session.exec(statement).all()

def delete_metric_entry(session: Session, user_id: int, entry_id: int) -> None:
    """
    Delete a specific metric entry for the given user.
    """
    logging.info(f"delete_metric_entry called for user_id={user_id}, entry_id={entry_id}")
    statement = select(MetricEntry).where(
        MetricEntry.id == entry_id,
        MetricEntry.user_id == user_id
    )
    entry = session.exec(statement).first()
    if entry:
        session.delete(entry)
        session.commit()

def get_user_metrics_config(session: Session, user_id: int) -> List[UserMetricsConfig]:
    """
    Get all metrics configurations for a user.
    """
    logging.info(f"get_user_metrics_config called for user_id={user_id}")
    statement = select(UserMetricsConfig).where(UserMetricsConfig.user_id == user_id)
    return session.exec(statement).all()

def get_user_metrics_config_active(session: Session, user_id: int) -> List[UserMetricsConfig]:
    """
    Get only active metrics configurations for a user.
    """
    logging.info(f"get_user_metrics_config_active called for user_id={user_id}")
    statement = select(UserMetricsConfig).where(
        UserMetricsConfig.user_id == user_id,
        UserMetricsConfig.is_active == True
    )
    return session.exec(statement).all()

def get_user_metrics_config_inactive(session: Session, user_id: int) -> List[UserMetricsConfig]:
    """
    Get only inactive metrics configurations for a user.
    """
    logging.info(f"get_user_metrics_config_inactive called for user_id={user_id}")
    statement = select(UserMetricsConfig).where(
        UserMetricsConfig.user_id == user_id,
        UserMetricsConfig.is_active == False
    )
    return session.exec(statement).all()

def create_user_metrics_config(
    session: Session, 
    user_id: int, 
    metric_key: str,
    metric_name: str,
    unit: str,
    type: str,
    goal: Optional[float] = None,
    default_goal: Optional[float] = None,
    is_active: bool = True
) -> UserMetricsConfig:
    """
    Create a new metrics configuration for a user.
    """
    logging.info(f"create_user_metrics_config called for user_id={user_id}, metric_key={metric_key}")
    
    config = UserMetricsConfig(
        user_id=user_id,
        metric_key=metric_key,
        metric_name=metric_name,
        unit=unit,
        type=type,
        goal=goal,
        default_goal=default_goal,
        is_active=is_active,
        updated_at=datetime.utcnow()
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

def update_user_metrics_config(
    session: Session,
    user_id: int,
    metric_key: str,
    **kwargs
) -> Optional[UserMetricsConfig]:
    """
    Update a user's metrics configuration.
    """
    logging.info(f"update_user_metrics_config called for user_id={user_id}, metric_key={metric_key}")
    
    statement = select(UserMetricsConfig).where(
        UserMetricsConfig.user_id == user_id,
        UserMetricsConfig.metric_key == metric_key
    )
    config = session.exec(statement).first()
    
    if config:
        for key, value in kwargs.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
        
        config.updated_at = datetime.utcnow()
        session.add(config)
        session.commit()
        session.refresh(config)
    
    return config

def delete_user_metrics_config(session: Session, user_id: int, metric_key: str) -> bool:
    """
    Delete (or deactivate) a user's metrics configuration.
    """
    logging.info(f"delete_user_metrics_config called for user_id={user_id}, metric_key={metric_key}")
    
    statement = select(UserMetricsConfig).where(
        UserMetricsConfig.user_id == user_id,
        UserMetricsConfig.metric_key == metric_key
    )
    config = session.exec(statement).first()
    
    if config:
        # Instead of deleting, we deactivate to preserve history
        config.is_active = False
        config.updated_at = datetime.utcnow()
        session.add(config)
        session.commit()
        return True
    
    return False