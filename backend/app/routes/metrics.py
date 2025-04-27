from typing import List
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, Response
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
    for name, start in periods.items():
        entries = get_user_metrics(session, current_user.id, start, now)
        # Initialize averages with None for each metric
        avg_values = {key: None for key in metric_keys}
        # Collect values by metric key
        values_by_key: dict = {key: [] for key in metric_keys}
        for entry in entries:
            if entry.metric_key in values_by_key:
                values_by_key[entry.metric_key].append(entry.value)
        # Compute averages where data exists
        for key, vals in values_by_key.items():
            if vals:
                avg_values[key] = sum(vals) / len(vals)
        aggregated[name] = avg_values
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