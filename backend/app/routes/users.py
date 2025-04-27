from fastapi import APIRouter, HTTPException, Depends, Response
from sqlmodel import Session
import uuid, hashlib
import logging

from app.schemas import UserCreate, UserSignup, APIKeyOut, APIKeyDelete
from app.crud import get_user_by_username, create_user, create_api_key, revoke_api_key, create_default_goals
from app.db import get_session
from app.auth import get_current_user
from app.dependencies import rate_limit_user
import time

# Global signup rate limit: 5 requests per minute
SIGNUP_RATE_LIMIT = 5
SIGNUP_RATE_PERIOD = 60  # seconds
_signup_requests: list[float] = []

router = APIRouter(prefix="/api", tags=["users"])

@router.post("/signup", response_model=UserSignup)
def signup(
    user_in: UserCreate,
    response: Response,
    session: Session = Depends(get_session),
):
    """
    Register a new user. Generates a UUID4 token, stores its SHA-256 hash, and returns the plaintext token.
    """
    logging.info(f"signup called with username={user_in.username}")
    existing = get_user_by_username(session, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    # Global rate limiting: allow only SIGNUP_RATE_LIMIT new signups per SIGNUP_RATE_PERIOD
    now = time.time()
    # Prune timestamps older than period
    while _signup_requests and _signup_requests[0] <= now - SIGNUP_RATE_PERIOD:
        _signup_requests.pop(0)
    if len(_signup_requests) >= SIGNUP_RATE_LIMIT:
        reset = _signup_requests[0] + SIGNUP_RATE_PERIOD
        headers = {
            "X-RateLimit-Limit": str(SIGNUP_RATE_LIMIT),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(reset)),
        }
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers=headers)
    # Record this signup attempt
    _signup_requests.append(now)
    remaining = SIGNUP_RATE_LIMIT - len(_signup_requests)
    reset = _signup_requests[0] + SIGNUP_RATE_PERIOD
    response.headers["X-RateLimit-Limit"] = str(SIGNUP_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset))
    # Generate token and its hash
    token = str(uuid.uuid4())
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    # Create user record
    user = create_user(session, user_in.username)
    # Store first API key
    create_api_key(session, user.id, token_hash)
    # Initialize default goals for the new user
    create_default_goals(session, user.id)
    return UserSignup(username=user.username, token=token)
    
@router.post("/keys/{username}", response_model=APIKeyOut)
def generate_api_key(
    username: str,
    response: Response,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Generate and return a new API key for the authenticated user.
    """
    logging.info(f"generate_api_key called for username={username}")
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to generate key for this user")
    # Generate new token
    token = str(uuid.uuid4())
    key_hash = hashlib.sha256(token.encode()).hexdigest()
    create_api_key(session, current_user.id, key_hash)
    return APIKeyOut(token=token)

@router.delete("/keys/{username}", status_code=204)
def invalidate_api_key(
    username: str,
    response: Response,
    key_in: APIKeyDelete,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session),
    _rl: None = Depends(rate_limit_user),
):
    """
    Invalidate (revoke) the given API key for the authenticated user.
    """
    logging.info(f"invalidate_api_key called for username={username}")
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to revoke key for this user")
    key_hash = hashlib.sha256(key_in.token.encode()).hexdigest()
    revoke_api_key(session, current_user.id, key_hash)