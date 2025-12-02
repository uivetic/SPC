"""Google Sheets endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.activity import ActivityResponse, ActivityCategory
from app.models.user import User
from app.services.google_sheets import GoogleSheetsService
from app.services.auth_service import AuthService
from app.dependencies import require_view_permission, require_write_permission

router = APIRouter()
sheets_service = GoogleSheetsService()
auth_service = AuthService()


@router.get("/sheets/activities", response_model=ActivityResponse)
async def get_activities(
    current_user: User = Depends(require_view_permission)
):
    """Get all activities organized by category"""
    try:
        activities = await sheets_service.get_activities()
        # Convert dict to list of ActivityCategory
        categories = [
            ActivityCategory(**cat) for cat in activities
        ]
        return ActivityResponse(categories=categories)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri učitavanju aktivnosti: {str(e)}"
        )


@router.get("/sheets/projects")
async def get_projects(
    current_user: User = Depends(require_view_permission)
):
    """Get list of projects"""
    try:
        projects = await sheets_service.get_projects()
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri učitavanju projekata: {str(e)}"
        )

