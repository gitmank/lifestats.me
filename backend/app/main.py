import app.logging_config  # initialize logging to SQLite
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://lifestats-me.vercel.app",  # Your specific Vercel domain
        "https://lifestats.vercel.app",     # Alternative domain
        "https://lifestats.me",             # Your custom domain
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow any Vercel subdomain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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