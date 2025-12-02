"""Users endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.models.user import User
from app.services.google_sheets import GoogleSheetsService
from app.services.auth_service import AuthService
from app.dependencies import require_view_permission

router = APIRouter()
sheets_service = GoogleSheetsService()
auth_service = AuthService()


@router.get("/users")
async def get_users(
    current_user: User = Depends(require_view_permission)
):
    """Get list of all users/members"""
    try:
        users = await sheets_service.get_all_names()
        return {"users": users}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri učitavanju korisnika: {str(e)}"
        )


@router.get("/users/search")
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: User = Depends(require_view_permission)
):
    """Search users with fuzzy matching"""
    try:
        results = await sheets_service.search_names(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri pretrazi: {str(e)}"
        )

