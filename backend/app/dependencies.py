"""
Rate limiting dependencies for FastAPI endpoints.
"""
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Response, status

from app.auth import get_current_user
from app.models import User

# User-level rate limit: 10 requests per 1 second
USER_RATE_LIMIT = 10
USER_RATE_PERIOD = 1  # seconds
_user_requests = defaultdict(list)  # user_id -> list of request timestamps

async def rate_limit_user(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """
    Dependency to rate limit authenticated users: max USER_RATE_LIMIT requests per USER_RATE_PERIOD.
    Sets rate limit headers on the response.
    """
    user_id = current_user.id
    now = time.time()
    history = _user_requests[user_id]
    # Remove timestamps outside the current period window
    while history and history[0] <= now - USER_RATE_PERIOD:
        history.pop(0)
    # Check if limit exceeded
    if len(history) >= USER_RATE_LIMIT:
        reset = history[0] + USER_RATE_PERIOD
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(USER_RATE_LIMIT),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset)),
            },
        )
    # Record this request
    history.append(now)
    remaining = USER_RATE_LIMIT - len(history)
    reset = history[0] + USER_RATE_PERIOD
    # Attach rate limit headers
    response.headers["X-RateLimit-Limit"] = str(USER_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset))