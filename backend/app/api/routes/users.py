"""User management routes."""

from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/")
async def list_users():
    """List all users."""
    return {"message": "List users - TODO: Implement"}


@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""
    return {"message": f"Get user {user_id} - TODO: Implement"}


@router.put("/{user_id}")
async def update_user(user_id: int):
    """Update user by ID."""
    return {"message": f"Update user {user_id} - TODO: Implement"}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """Delete user by ID."""
    return {"message": f"Delete user {user_id} - TODO: Implement"}