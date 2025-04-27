from typing import List
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.config import config
from app.schemas import MetricConfig, MetricEntryCreate, MetricEntryRead, AggregatedMetrics
from app.crud import create_metric_entry, get_user_metrics
from app.db import get_session
from app.auth import get_current_user
from app.models import User
from app.dependencies import rate_limit_user

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/config", response_model=List[MetricConfig])
def get_metrics_config():
    logging.info("get_metrics_config endpoint called")
    return config.get_metrics()

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
    periods = {
        "daily": now - timedelta(days=1),
        "weekly": now - timedelta(weeks=1),
        "monthly": now - timedelta(days=30),
        "quarterly": now - timedelta(days=90),
        "yearly": now - timedelta(days=365),
    }
    # Determine all available metric keys from config
    metric_keys = [m["key"] for m in config.get_metrics()]
    aggregated: dict = {}
    # Define period lengths in days for averaging per day
    period_days = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365,
    }
    for name, start in periods.items():
        # Fetch entries in the period
        entries = get_user_metrics(session, current_user.id, start, now)
        # Sum values for each metric key
        sums: dict = {key: None for key in metric_keys}
        for entry in entries:
            key = entry.metric_key
            if key in sums:
                if sums[key] is None:
                    sums[key] = entry.value
                else:
                    sums[key] += entry.value
        # Compute average per day by dividing sum by number of days in period
        days = period_days.get(name, 1)
        avg_per_day: dict = {}
        for key, total in sums.items():
            if total is None:
                avg_per_day[key] = None
            else:
                avg_per_day[key] = total / days
        # For weekly, also include an array of daily totals for the last 7 calendar days
        if name == "weekly":
            # Prepare list of the last 7 dates (oldest first)
            dates = [(now.date() - timedelta(days=i)) for i in reversed(range(period_days["weekly"]))]
            # Initialize daily totals per metric
            daily_totals: dict = {key: [] for key in metric_keys}
            # Compute totals for each day
            for key in metric_keys:
                for day in dates:
                    total = sum(
                        e.value for e in entries
                        if e.metric_key == key and e.timestamp.date() == day
                    )
                    daily_totals[key].append(total)
            # Include average per day values and daily totals for weekly aggregation
            aggregated[name] = {**avg_per_day, "daily_totals": daily_totals}
        else:
            aggregated[name] = avg_per_day
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