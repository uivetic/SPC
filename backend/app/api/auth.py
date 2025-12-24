"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import jwt
from datetime import datetime, timedelta
import traceback
import asyncio
from app.config import settings
from app.models.user import User, UserResponse
from app.services.auth_service import AuthService
from app.utils.google_workspace import is_user_in_group, check_user_access
from app.utils.auth import check_google_workspace_access

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
        
        user_email = user_info["email"]
        
        try:
            await check_google_workspace_access(user_email)
        except HTTPException as e:
            error_msg = e.detail or "Nemate pristup aplikaciji. Kontaktirajte secretary@best.rs"
            error_url = f"{settings.FRONTEND_URL}/auth/callback?error={error_msg}"
            return RedirectResponse(url=error_url)
        
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={
                "sub": user_info["id"],
                "email": user_info["email"],
                "name": user_info.get("name", ""),
            },
            expires_delta=access_token_expires
        )
        
        frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
    except HTTPException as e:
        error_msg = e.detail or "Greška pri autentifikaciji"
        error_url = f"{settings.FRONTEND_URL}/auth/callback?error={error_msg}"
        return RedirectResponse(url=error_url)
    except Exception as e:
        error_url = f"{settings.FRONTEND_URL}/auth/callback?error={str(e)}"
        return RedirectResponse(url=error_url)


@router.post("/auth/google/callback")
async def google_callback_post(code: str):
    """Handle Google OAuth callback (POST - for frontend code exchange)"""
    try:
        redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.FRONTEND_URL}/auth/callback"
        user_info = await auth_service.handle_google_callback(code, redirect_uri)
        
        user_email = user_info["email"]
        
        try:
            await check_google_workspace_access(user_email)
        except HTTPException:
            raise
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Greška pri autentifikaciji: {str(e)}"
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user.dict())


@router.get("/auth/permissions")
async def get_user_permissions(
    current_user: User = Depends(auth_service.get_current_user)
):
    from app.dependencies import check_write_permission, check_view_permission
    
    can_write = check_write_permission(current_user)
    can_view = await check_view_permission(current_user)
    
    return {
        "email": current_user.email,
        "can_write_points": can_write,
        "can_view_points": can_view,
    }


@router.post("/auth/logout")
async def logout():
    """Logout endpoint (client should remove token)"""
    return {"message": "Logged out successfully"}


@router.get("/auth/test/google-workspace/{user_email}")
async def test_google_workspace_access(user_email: str):
    try:
        # Proveri da li je @best.rs (automatski pristup)
        auto_access = user_email.endswith("@best.rs")
        
        # Proveri članstvo u grupi (samo ako nije @best.rs)
        is_member = False
        error_details = None
        
        if not auto_access:
            try:
                # Pozovi sync funkciju u async kontekstu
                loop = asyncio.get_event_loop()
                is_member = await loop.run_in_executor(None, is_user_in_group, user_email)
            except Exception as e:
                error_details = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
        
        has_access = auto_access or is_member
        
        result = {
            "user_email": user_email,
            "has_access": has_access,
            "is_member_of_group": is_member,
            "group": "opsta@best.rs",
            "auto_access": auto_access
        }
        
        if error_details:
            result["error"] = error_details
        
        return result
    except Exception as e:
        return {
            "user_email": user_email,
            "error": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            },
            "has_access": False
        }

