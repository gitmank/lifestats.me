import app.logging_config  # initialize logging to SQLite
import time
from collections import defaultdict, deque
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from app.db import engine
from app.routes.users import router as users_router
from app.routes.metrics import router as metrics_router
from app.routes.root import router as root_router
from app.routes.goals import router as goals_router

app = FastAPI()

# Rate limiting storage
request_times = defaultdict(lambda: deque())
global_request_times = deque()

# Add CORS middleware with wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware: 10 req/sec per API key for authenticated, 10 req/sec global for unauthenticated"""
    current_time = time.time()
    
    # Extract API key from Authorization header
    auth_header = request.headers.get("Authorization")
    api_key = None
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header.split(" ", 1)[1]
    
    if api_key:
        # Authenticated request - rate limit per API key
        user_times = request_times[api_key]
        
        # Remove requests older than 1 second
        while user_times and current_time - user_times[0] > 1.0:
            user_times.popleft()
        
        # Check if rate limit exceeded
        if len(user_times) >= 10:
            raise HTTPException(
                status_code=429,
                detail="Too many requests! You're sending requests too quickly. Please wait a few seconds and try again. (Limit: 10 requests per second)"
            )
        
        # Add current request
        user_times.append(current_time)
    else:
        # Unauthenticated request - global rate limit
        # Remove requests older than 1 second
        while global_request_times and current_time - global_request_times[0] > 1.0:
            global_request_times.popleft()
        
        # Check if rate limit exceeded
        if len(global_request_times) >= 10:
            raise HTTPException(
                status_code=429,
                detail="Server is receiving too many requests right now. Please wait a few seconds and try again. Consider signing up for higher limits!"
            )
        
        # Add current request
        global_request_times.append(current_time)
    
    response = await call_next(request)
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler that adds relevant hints to error responses."""
    error_hint = "Check API documentation at /docs for details"
    
    # Customize hints based on status code
    if exc.status_code == 401:
        error_hint = "Send a valid token in the Authorization header as 'Bearer {token}'"
    elif exc.status_code == 403:
        error_hint = "You don't have permission to access this resource"
    elif exc.status_code == 404:
        error_hint = "Check that the endpoint URL and path parameters are correct"
    elif exc.status_code == 422:
        error_hint = "Validation error - check your request data format"
    elif exc.status_code == 429:
        error_hint = "Rate limit exceeded - please wait and try again later"
    elif "Username already exists" in str(exc.detail):
        error_hint = "Choose a different username!"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "hint": error_hint},
    )

app.include_router(root_router)
app.include_router(users_router)
app.include_router(metrics_router)
app.include_router(goals_router)