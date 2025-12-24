from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.models.user import User
from app.services.google_groups import google_groups_service

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        name: str = payload.get("name", "")
        
        if user_id is None or email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    return User(id=user_id, email=email, name=name)


def check_write_permission(user: User) -> bool:
    user_email_lower = user.email.lower()
    
    # Check if user is in allowed write emails list
    return user_email_lower in [email.lower() for email in settings.ALLOWED_WRITE_EMAILS]


async def check_view_permission(user: User) -> bool:
    user_email_lower = user.email.lower()
    
    if user_email_lower.endswith("@best.rs"):
        return True
    
    if settings.ALLOWED_VIEW_EMAILS:
        if user_email_lower in [email.lower() for email in settings.ALLOWED_VIEW_EMAILS]:
            return True
    
    try:
        from app.utils.google_workspace import is_user_in_group
        import asyncio
        
        loop = asyncio.get_event_loop()
        is_member = await loop.run_in_executor(None, is_user_in_group, user.email)
        return is_member
    except Exception as e:
        error_str = str(e)
        is_delegation_error = 'unauthorized_client' in error_str.lower() or 'domain-wide delegation' in error_str.lower()
        if is_delegation_error:
            print(f"ERROR: Domain-Wide Delegation may not be properly configured.")
        return False


async def require_write_permission(
    current_user: User = Depends(get_current_user)
) -> User:
    if not check_write_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemate dozvolu za unos bodova. Samo određeni korisnici mogu unositi bodove."
        )
    return current_user


async def require_view_permission(
    current_user: User = Depends(get_current_user)
) -> User:
    if not await check_view_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemate dozvolu za pregled bodova."
        )
    return current_user
