import asyncio
from fastapi import HTTPException, status
from .google_workspace import check_user_access


async def check_google_workspace_access(user_email: str):
    try:
        loop = asyncio.get_event_loop()
        has_access = await loop.run_in_executor(None, check_user_access, user_email)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nemate pristup aplikaciji. Kontaktirajte secretary@best.rs"
            )
        
        return True
    except HTTPException:
        raise
    except Exception as e:
        if user_email.lower().endswith("@best.rs"):
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Greška pri proveri pristupa: {str(e)}"
        )

