from typing import List
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.config import config
from app.schemas import MetricConfig, MetricEntryCreate, MetricEntryRead, AggregatedMetrics
from app.crud import create_metric_entry, get_user_metrics, get_user_goals, get_last_entries, delete_metric_entry
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
    logging.info(f"get_metrics_config endpoint called for user_id={current_user.id}")
    
    # Get base configuration
    base_config = config.get_metrics()
    
    # Get user's custom goals
    user_goals = get_user_goals(session, current_user.id)
    goal_map = {goal.metric_key: goal.target_value for goal in user_goals}
    
    # Merge user goals with base config
    result = []
    for metric in base_config:
        metric_dict = metric.copy()
        # Use user's custom goal if available, otherwise use default_goal
        metric_dict["goal"] = goal_map.get(metric["key"], metric.get("default_goal", 0))
        result.append(metric_dict)
    
    return result

@router.get("", response_model=AggregatedMetrics)
def read_metrics(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Return aggregated metric sums for the authenticated user over fixed periods.
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
    
    # Determine all available metric keys from config
    metric_keys = [m["key"] for m in config.get_metrics()]
    # Build baseline goals from config defaults, then override with user-set goals
    default_goal_map = {m["key"]: m.get("default_goal") for m in config.get_metrics() if m.get("default_goal") is not None}
    # Build type map for goal comparison logic
    type_map = {m["key"]: m.get("type", "min") for m in config.get_metrics()}
    goals = get_user_goals(session, current_user.id)
    goal_map = default_goal_map.copy()
    for g in sorted(goals, key=lambda x: x.created_at):
        goal_map[g.metric_key] = g.target_value
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
        # Compute average per day by dividing sum by number of days in period
        days = period_days.get(name, 1)
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
        for key, target in goal_map.items():
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
    """
    logging.info(f"add_metric_entry called for user_id={current_user.id}, payload={entry_in.model_dump()}")
    # Validate metric_key against configured metrics
    valid_keys = [m["key"] for m in config.get_metrics()]
    if entry_in.metric_key not in valid_keys:
        # Return 400 Bad Request with hint of valid metric keys
        content = {
            "detail": f"Invalid metric_key '{entry_in.metric_key}'",
            "hint": valid_keys,
        }
        return JSONResponse(status_code=400, content=content)
    # Determine timestamp: use provided or default to current UTC time
    from datetime import datetime
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