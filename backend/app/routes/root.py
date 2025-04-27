"""
Root endpoint handler that provides basic API information.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "hint": "POST to /api/signup with {username} to create an account.",
        "docs": "Visit /docs for complete API spec."
    }
