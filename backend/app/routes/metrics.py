from typing import List
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.config import config
from app.schemas import (
    MetricConfig, MetricEntryCreate, MetricEntryRead, AggregatedMetrics,
    UserMetricsConfigCreate, UserMetricsConfigUpdate, UserMetricsConfigRead
)
from app.crud import (
    create_metric_entry, get_user_metrics, get_user_goals, get_last_entries, 
    delete_metric_entry, get_user_metrics_config_active, get_user_metrics_config,
    get_user_metrics_config_inactive, create_user_metrics_config, update_user_metrics_config, 
    delete_user_metrics_config
)
from app.db import get_session
from app.auth import get_current_user
from app.models import User
from app.dependencies import rate_limit_user

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/config", response_model=List[MetricConfig])
def get_metrics_config(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """Get user-specific metrics configuration."""
    logging.info(f"get_metrics_config endpoint called for user_id={current_user.id}")
    
    # Get user's specific configuration
    user_configs = get_user_metrics_config_active(session, current_user.id)
    
    # Convert to MetricConfig format for compatibility
    result = []
    for config in user_configs:
        metric_dict = {
            "key": config.metric_key,
            "name": config.metric_name,
            "unit": config.unit,
            "type": config.type,
            "default_goal": config.default_goal,
            "goal": config.goal,
            "is_active": config.is_active
        }
        result.append(metric_dict)
    
    return result

@router.get("/config/inactive", response_model=List[MetricConfig])
def get_inactive_metrics_config(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """Get user-specific inactive metrics configuration."""
    logging.info(f"get_inactive_metrics_config endpoint called for user_id={current_user.id}")
    
    # Get user's inactive configuration
    user_configs = get_user_metrics_config_inactive(session, current_user.id)
    
    # Convert to MetricConfig format for compatibility
    result = []
    for config in user_configs:
        metric_dict = {
            "key": config.metric_key,
            "name": config.metric_name,
            "unit": config.unit,
            "type": config.type,
            "default_goal": config.default_goal,
            "goal": config.goal,
            "is_active": config.is_active
        }
        result.append(metric_dict)
    
    return result

@router.post("/config", response_model=UserMetricsConfigRead)
def create_metrics_config(
    config_in: UserMetricsConfigCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """Create a new metrics configuration for the user."""
    logging.info(f"create_metrics_config called for user_id={current_user.id}, payload={config_in.model_dump()}")
    
    # Check if metric already exists for this user
    existing_configs = get_user_metrics_config(session, current_user.id)
    for config in existing_configs:
        if config.metric_key == config_in.metric_key:
            raise HTTPException(status_code=400, detail=f"Metric '{config_in.metric_key}' already exists for user")
    
    new_config = create_user_metrics_config(
        session=session,
        user_id=current_user.id,
        metric_key=config_in.metric_key,
        metric_name=config_in.metric_name,
        unit=config_in.unit,
        type=config_in.type,
        goal=config_in.goal,
        default_goal=config_in.default_goal,
        is_active=config_in.is_active
    )
    
    return new_config

@router.put("/config/{metric_key}", response_model=UserMetricsConfigRead)
def update_metrics_config(
    metric_key: str,
    config_in: UserMetricsConfigUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """Update a metrics configuration for the user."""
    logging.info(f"update_metrics_config called for user_id={current_user.id}, metric_key={metric_key}")
    
    updated_config = update_user_metrics_config(
        session=session,
        user_id=current_user.id,
        metric_key=metric_key,
        **config_in.model_dump(exclude_unset=True)
    )
    
    if not updated_config:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_key}' not found for user")
    
    return updated_config

@router.delete("/config/{metric_key}")
def delete_metrics_config(
    metric_key: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """Delete (deactivate) a metrics configuration for the user."""
    logging.info(f"delete_metrics_config called for user_id={current_user.id}, metric_key={metric_key}")
    
    success = delete_user_metrics_config(session, current_user.id, metric_key)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_key}' not found for user")
    
    return {"status": "success", "message": f"Metric '{metric_key}' deactivated"}

@router.get("", response_model=AggregatedMetrics)
def read_metrics(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Return aggregated metric sums for the authenticated user over fixed periods.
    Uses user-specific metrics configuration.
    """
    logging.info(f"read_metrics called for user_id={current_user.id}")
    now = datetime.utcnow()
    
    # Calculate period start dates
    today = now.date()
    
    # For weekly: find the start of current week (Monday)
    days_since_monday = today.weekday()  # Monday=0, Sunday=6
    current_week_start = today - timedelta(days=days_since_monday)
    weekly_start = datetime.combine(current_week_start, datetime.min.time())
    
    # For daily: start from beginning of today to end of today
    daily_start = datetime.combine(today, datetime.min.time())
    daily_end = datetime.combine(today + timedelta(days=1), datetime.min.time())
    
    periods = {
        "daily": daily_start,
        "weekly": weekly_start,
        "monthly": now - timedelta(days=30),
        "quarterly": now - timedelta(days=90),
        "yearly": now - timedelta(days=365),
    }
    
    # Get user's active metrics configuration
    user_configs = get_user_metrics_config_active(session, current_user.id)
    metric_keys = [config.metric_key for config in user_configs]
    goal_map = {config.metric_key: config.goal for config in user_configs if config.goal is not None}
    type_map = {config.metric_key: config.type for config in user_configs}
    
    # Prepare containers for aggregated metrics
    aggregated: dict = {}
    
    # Define period lengths in days for averaging per day
    period_days = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365,
    }
    
    # Compute aggregated metrics per period
    for name, start in periods.items():
        # Fetch entries in the period
        if name == "daily":
            # For daily: use the entire day (start to end of day)
            entries = get_user_metrics(session, current_user.id, start, daily_end)
        else:
            # For other periods: use start to now
            entries = get_user_metrics(session, current_user.id, start, now)
        
        # Sum values for each metric key
        sums: dict = {key: 0.0 for key in metric_keys}
        for entry in entries:
            key = entry.metric_key
            if key in sums:
                sums[key] += entry.value
        
        # --- MODIFIED: Only count days that have passed (including today) for average calculation ---
        if name == "weekly":
            # Days passed in current week (Monday=0, ..., today)
            days_passed = today.weekday() + 1  # e.g. if today is Wednesday (2), days_passed = 3
        elif name == "monthly":
            days_passed = today.day  # 1-based (e.g. 7th = 7 days passed)
        elif name == "quarterly":
            # Approximate: 90 days, so use days since (now - 90 days) to today
            days_passed = (now.date() - (now - timedelta(days=90)).date()).days + 1
        elif name == "yearly":
            days_passed = (now.date() - (now - timedelta(days=365)).date()).days + 1
        else:
            days_passed = 1
        # Cap days_passed to max period length
        days = min(period_days.get(name, 1), days_passed)
        
        # Compute average per day by dividing sum by number of days in period
        avg_per_day: dict = {}
        for key in metric_keys:
            total = sums.get(key, 0.0)
            avg_per_day[key] = (total / days) if total != 0 else (None if not entries else 0.0 / days)
        
        # Calculate dates for this period consistently
        if name == "weekly":
            # For weekly: use Monday to Sunday dates in order
            dates = [current_week_start + timedelta(days=i) for i in range(7)]
        elif name == "daily":
            # For daily: only include today
            dates = [today]
        else:
            # For other periods: go back from today
            dates = [(today - timedelta(days=i)) for i in reversed(range(period_days[name]))]
        
        # Prepare the base aggregation for this period: wrap averages under 'average_values'
        if name == "weekly":
            daily_totals: dict = {key: [] for key in metric_keys}
            for key in metric_keys:
                for day in dates:
                    total = sum(
                        e.value for e in entries
                        if e.metric_key == key and e.timestamp.date() == day
                    )
                    daily_totals[key].append(total)
            base = {"average_values": avg_per_day, "daily_totals": daily_totals}
        else:
            base = {"average_values": avg_per_day}
        
        # Count goal-reached days for this period using the same dates
        goal_counts = {}
        for key in metric_keys:
            target = goal_map.get(key)
            if target is None:
                goal_counts[key] = 0
                continue
                
            count = 0
            metric_type = type_map.get(key, "min")
            for day in dates:
                total = sum(
                    e.value for e in entries
                    if e.metric_key == key and e.timestamp.date() == day
                )
                # Check goal completion based on metric type
                if metric_type == "max":
                    # For max goals (limits), goal is met when total <= target
                    if total <= target:
                        count += 1
                else:
                    # For min goals, goal is met when total >= target
                    if total >= target:
                        count += 1
            goal_counts[key] = count
        base["goalReached"] = goal_counts
        aggregated[name] = base
    
    # Return aggregated metrics with nested goalReached per period
    return aggregated

@router.post("", response_model=MetricEntryRead)
def add_metric_entry(
    entry_in: MetricEntryCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Create a new metric entry for the authenticated user.
    Validates against user's active metrics configuration.
    """
    logging.info(f"add_metric_entry called for user_id={current_user.id}, payload={entry_in.model_dump()}")
    
    # Validate metric_key against user's active metrics configuration
    user_configs = get_user_metrics_config_active(session, current_user.id)
    valid_keys = [config.metric_key for config in user_configs]
    
    if entry_in.metric_key not in valid_keys:
        # Return 400 Bad Request with hint of valid metric keys
        content = {
            "detail": f"Invalid metric_key '{entry_in.metric_key}' or metric is not active for user",
            "hint": valid_keys,
        }
        return JSONResponse(status_code=400, content=content)
    
    # Determine timestamp: use provided or default to current UTC time
    ts = entry_in.timestamp or datetime.utcnow()
    entry = create_metric_entry(
        session,
        current_user.id,
        entry_in.metric_key,
        entry_in.value,
        ts,
    )
    return entry

@router.get("/recent", response_model=List[MetricEntryRead])
def get_recent_entries(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Get the last 5 metric entries for the authenticated user.
    """
    logging.info(f"get_recent_entries called for user_id={current_user.id}")
    entries = get_last_entries(session, current_user.id)
    return entries

@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Delete a specific metric entry for the authenticated user.
    """
    logging.info(f"delete_entry called for user_id={current_user.id}, entry_id={entry_id}")
    delete_metric_entry(session, current_user.id, entry_id)
    return {"status": "success"}