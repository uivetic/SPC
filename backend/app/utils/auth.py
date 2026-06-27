import asyncio
from fastapi import HTTPException, status
from .google_workspace import check_user_access


async def check_google_workspace_access(user_email: str):
    from .google_workspace import is_user_in_group
    try:
        loop = asyncio.get_event_loop()
        has_access = await loop.run_in_executor(None, is_user_in_group, user_email)

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nemate pristup aplikaciji. Kontaktirajte secretary@best.rs"
            )

        return True
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[AUTH] check_google_workspace_access failed for {user_email}: {traceback.format_exc()}")
        if user_email.lower().endswith("@best.rs"):
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Greška pri proveri pristupa: {str(e)}"
        )

