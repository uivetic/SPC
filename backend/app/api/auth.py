"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings
from app.models.user import User, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.FRONTEND_URL}/auth/callback"
    auth_url = auth_service.get_google_auth_url(redirect_uri)
    return {"auth_url": auth_url}


@router.get("/auth/google/callback")
async def google_callback_get(code: str):
    """Handle Google OAuth callback (GET - for redirects)"""
    try:
        redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.FRONTEND_URL}/auth/callback"
        user_info = await auth_service.handle_google_callback(code, redirect_uri)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={
                "sub": user_info["id"],
                "email": user_info["email"],
                "name": user_info.get("name", ""),
            },
            expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        error_url = f"{settings.FRONTEND_URL}/auth/callback?error={str(e)}"
        return RedirectResponse(url=error_url)


@router.post("/auth/google/callback")
async def google_callback_post(code: str):
    """Handle Google OAuth callback (POST - for frontend code exchange)"""
    try:
        redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.FRONTEND_URL}/auth/callback"
        user_info = await auth_service.handle_google_callback(code, redirect_uri)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={
                "sub": user_info["id"],
                "email": user_info["email"],
                "name": user_info.get("name", ""),
            },
            expires_delta=access_token_expires
        )
        
        return {"token": access_token, "user": user_info}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user.dict())


@router.post("/auth/logout")
async def logout():
    """Logout endpoint (client should remove token)"""
    return {"message": "Logged out successfully"}

