"""
Authentication dependency for FastAPI.
"""
import hashlib
import logging
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.db import get_session
from app.models import User, APIKey

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """
    Validate the bearer token and return the corresponding User.
    """
    token = credentials.credentials
    # Hash the provided token and look up in APIKey table
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    logging.info(f"get_current_user called with token_hash={token_hash}")
    statement = select(APIKey).where(APIKey.key_hash == token_hash)
    api_key = session.exec(statement).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Return the associated User
    return api_key.user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user