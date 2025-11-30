"""Points endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.points import PointsWriteRequest, PointsResponse, PointsWriteResponse
from app.models.user import User
from app.services.google_sheets import GoogleSheetsService
from app.services.auth_service import AuthService

router = APIRouter()
sheets_service = GoogleSheetsService()
auth_service = AuthService()


@router.post("/points/write", response_model=PointsWriteResponse)
async def write_points(
    request: PointsWriteRequest,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Write points to Google Sheets"""
    try:
        result = await sheets_service.write_points(
            batch=request.batch,
            pairs=request.pairs
        )
        return PointsWriteResponse(
            success=True,
            message=f"Uspešno upisano {result['count']} osoba",
            count=result['count']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Greška pri upisu bodova: {str(e)}"
        )


@router.get("/points/{name}", response_model=PointsResponse)
async def get_points(
    name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get points for a specific person"""
    try:
        points_data = await sheets_service.get_points_for_person(name)
        return PointsResponse(**points_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Greška pri čitanju bodova: {str(e)}"
        )


@router.get("/points/all")
async def get_all_points(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get list of all people with their points summary"""
    try:
        people = await sheets_service.get_all_people()
        return {"people": people}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Greška pri učitavanju podataka: {str(e)}"
        )

