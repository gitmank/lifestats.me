"""
Routes for user-defined goals on metrics.
"""
from typing import List
import logging

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.config import config
from app.schemas import GoalCreate, GoalRead
from app.crud import upsert_goal, get_user_goals
from app.db import get_session
from app.auth import get_current_user
from app.models import User
from app.dependencies import rate_limit_user

router = APIRouter(prefix="/api/goals", tags=["goals"])

@router.get("", response_model=List[GoalRead])
def read_goals(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Retrieve all goals set by the authenticated user.
    """
    logging.info(f"read_goals called for user_id={current_user.id}")
    goals = get_user_goals(session, current_user.id)
    return goals

@router.post("", response_model=GoalRead)
def set_goal(
    goal_in: GoalCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Set a new goal for a specific metric for the authenticated user.
    """
    logging.info(f"set_goal called for user_id={current_user.id}, payload={goal_in.model_dump()}")
    # Validate metric_key against configured metrics
    valid_keys = [m["key"] for m in config.get_metrics()]
    if goal_in.metric_key not in valid_keys:
        content = {
            "detail": f"Invalid metric_key '{goal_in.metric_key}'",
            "hint": valid_keys,
        }
        return JSONResponse(status_code=400, content=content)

    goal = upsert_goal(
        session,
        current_user.id,
        goal_in.metric_key,
        goal_in.target_value,
    )
    return goal