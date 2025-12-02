"""Google Groups service for checking group membership"""
import httpx
from typing import Optional
from app.config import settings
from google.oauth2.service_account import Credentials
import json
import os
import asyncio
from app.services.cache_service import cache_service


class GoogleGroupsService:
    """Service for checking Google Groups membership"""
    
    def __init__(self):
        self._credentials: Optional[Credentials] = None
    
    async def _get_credentials(self) -> Credentials:
        """Get or initialize Google credentials"""
        if self._credentials is None:
            await self._initialize_credentials()
        return self._credentials
    
    async def _initialize_credentials(self):
        """Initialize Google credentials"""
        loop = asyncio.get_event_loop()
        
        def load_credentials():
            # Try to load from environment variable first
            credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
            if credentials_json:
                try:
                    creds_dict = json.loads(credentials_json)
                    return Credentials.from_service_account_info(
                        creds_dict,
                        scopes=settings.GOOGLE_SHEETS_SCOPES
                    )
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f"Invalid GOOGLE_SHEETS_CREDENTIALS JSON: {e}")
            
            # Fallback to file path
            if not os.path.exists(settings.GOOGLE_SHEETS_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Credentials file not found: {settings.GOOGLE_SHEETS_CREDENTIALS_PATH}"
                )
            return Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_PATH,
                scopes=settings.GOOGLE_SHEETS_SCOPES
            )
        
        self._credentials = await loop.run_in_executor(None, load_credentials)
    
    async def is_member_of_group(self, email: str, group_email: Optional[str] = None) -> bool:
        """
        Check if email is a member of Google Group using Admin Directory API
        
        Note: This requires:
        1. Domain-Wide Delegation enabled in Google Cloud Console
        2. Service account email added to Google Workspace Admin Console with scope:
           https://www.googleapis.com/auth/admin.directory.group.readonly
        3. Admin API enabled in Google Cloud Console
        4. GOOGLE_ADMIN_EMAIL set in environment variables (super admin email)
        """
        group_email = group_email or settings.GOOGLE_GROUP_EMAIL
        
        # Check cache first
        cache_key = f"group_member:{group_email}:{email.lower()}"
        cached_result = await cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            base_creds = await self._get_credentials()
            
            # For domain-wide delegation, we need to use with_subject
            # This allows the service account to act on behalf of the admin user
            if not settings.GOOGLE_ADMIN_EMAIL:
                print("GOOGLE_ADMIN_EMAIL not set, cannot use domain-wide delegation")
                # Fallback: allow @best.rs emails
                return email.lower().endswith("@best.rs")
            
            # Create delegated credentials with admin email using with_subject
            from google.auth.transport.requests import Request
            
            # Use with_subject to impersonate the admin user
            delegated_creds = base_creds.with_subject(settings.GOOGLE_ADMIN_EMAIL)
            
            # Refresh to get access token
            request = Request()
            delegated_creds.refresh(request)
            access_token = delegated_creds.token
            
            if not access_token:
                raise ValueError("Failed to get access token with domain-wide delegation")
            
            # Use Google Admin Directory API to check group membership
            # Format: GET /admin/directory/v1/groups/{groupKey}/members/{memberKey}
            api_url = f"https://admin.googleapis.com/admin/directory/v1/groups/{group_email}/members/{email}"
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                response = await client.get(api_url, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    # User is a member
                    await cache_service.set(cache_key, True, ttl=3600)  # Cache for 1 hour
                    return True
                elif response.status_code == 404:
                    # User is not a member
                    await cache_service.set(cache_key, False, ttl=3600)
                    return False
                else:
                    # API error - log and fall back
                    print(f"Google Groups API error: {response.status_code} - {response.text}")
                    # Fallback: allow @best.rs emails
                    return email.lower().endswith("@best.rs")
                    
        except Exception as e:
            # If API fails, fall back to checking if email ends with @best.rs
            print(f"Error checking Google Groups membership for {email}: {e}")
            # Fallback: allow @best.rs emails
            return email.lower().endswith("@best.rs")


# Global service instance
google_groups_service = GoogleGroupsService()

