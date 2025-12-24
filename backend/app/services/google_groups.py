"""Google Groups service for checking group membership"""
from typing import Optional
from app.config import settings
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
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
    
    async def _get_admin_service(self):
        """
        Get Google Admin SDK service instance with domain-wide delegation
        
        Note: This requires:
        1. Domain-Wide Delegation enabled in Google Cloud Console
        2. Service account email added to Google Workspace Admin Console with scope:
           https://www.googleapis.com/auth/admin.directory.group.readonly
        3. Admin API enabled in Google Cloud Console
        4. GOOGLE_ADMIN_EMAIL set in environment variables (super admin email)
        """
        if not settings.GOOGLE_ADMIN_EMAIL:
            raise ValueError("GOOGLE_ADMIN_EMAIL not set, cannot use domain-wide delegation")
        
        base_creds = await self._get_credentials()
        
        # Use with_subject to impersonate the admin user (domain-wide delegation)
        delegated_creds = base_creds.with_subject(settings.GOOGLE_ADMIN_EMAIL)
        
        # Build Admin SDK service
        loop = asyncio.get_event_loop()
        def build_service():
            try:
                # Try to refresh credentials to get access token
                from google.auth.transport.requests import Request
                request = Request()
                delegated_creds.refresh(request)
                return build('admin', 'directory_v1', credentials=delegated_creds, cache_discovery=False)
            except Exception as e:
                error_msg = str(e)
                if 'unauthorized_client' in error_msg.lower():
                    # Get Client ID from credentials
                    client_id = "N/A"
                    try:
                        creds_info = base_creds._service_account_email
                        # Try to get client_id from service account info
                        if hasattr(base_creds, '_service_account_email'):
                            # Read from file if available
                            import json
                            if os.path.exists(settings.GOOGLE_SHEETS_CREDENTIALS_PATH):
                                with open(settings.GOOGLE_SHEETS_CREDENTIALS_PATH, 'r') as f:
                                    sa_info = json.load(f)
                                    client_id = sa_info.get('client_id', 'N/A')
                    except:
                        pass
                    
                    print("\n" + "="*80)
                    print("ERROR: Domain-Wide Delegation not properly configured!")
                    print("="*80)
                    print("\nService Account Info:")
                    print(f"  Email: spc-python@sistem-pracenja-clanstva.iam.gserviceaccount.com")
                    print(f"  Client ID: {client_id}")
                    print(f"  Admin Email: {settings.GOOGLE_ADMIN_EMAIL}")
                    print("\nTo fix this, you need to:")
                    print("\n1. Enable Domain-Wide Delegation in Google Cloud Console:")
                    print("   Direct link: https://console.cloud.google.com/iam-admin/serviceaccounts")
                    print("   - Select project: sistem-pracenja-clanstva")
                    print("   - Find service account: spc-python@sistem-pracenja-clanstva.iam.gserviceaccount.com")
                    print("   - Click on the service account email")
                    print("   - Go to 'Advanced settings' > 'Domain-wide delegation'")
                    print("   - Enable 'Enable Google Workspace Domain-wide Delegation'")
                    print(f"   - Note the Client ID: {client_id}")
                    print("\n2. Add Service Account to Google Workspace Admin Console:")
                    print("   Direct link: https://admin.google.com/ac/owl/domainwidedelegation")
                    print("   - Login with super admin account (e.g., secretary@best.rs)")
                    print("   - Click 'Add new'")
                    print(f"   - Enter Client ID: {client_id}")
                    print("   - Add OAuth scope (EXACTLY as shown, copy-paste this):")
                    print("     https://www.googleapis.com/auth/admin.directory.group.readonly")
                    print("   - Click 'Authorize'")
                    print("\n3. Enable Admin SDK API:")
                    print("   Direct link: https://console.cloud.google.com/apis/library/admin.googleapis.com")
                    print("   - Make sure project 'sistem-pracenja-clanstva' is selected")
                    print("   - Click 'Enable'")
                    print("\n4. Verify Configuration:")
                    print(f"   - GOOGLE_ADMIN_EMAIL: {settings.GOOGLE_ADMIN_EMAIL}")
                    print("   - This email MUST be a super admin in Google Workspace")
                    print("\n5. Wait a few minutes after making changes (propagation delay)")
                    print("\n6. Restart the backend server")
                    print("="*80 + "\n")
                raise
        
        return await loop.run_in_executor(None, build_service)
    
    async def is_member_of_group(self, email: str, group_email: Optional[str] = None) -> bool:
        """
        Check if email is a member of Google Group using Admin Directory API
        
        Uses the hasMember method which is more efficient than checking membership directly.
        """
        group_email = group_email or settings.GOOGLE_GROUP_EMAIL
        
        # Check cache first
        cache_key = f"group_member:{group_email}:{email.lower()}"
        cached_result = await cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # If no admin email, fallback to @best.rs check
            if not settings.GOOGLE_ADMIN_EMAIL:
                print("GOOGLE_ADMIN_EMAIL not set, cannot use domain-wide delegation")
                return email.lower().endswith("@best.rs")
            
            # Get Admin SDK service
            service = await self._get_admin_service()
            
            # Use hasMember method to check membership (more efficient)
            loop = asyncio.get_event_loop()
            def check_membership():
                try:
                    result = service.members().hasMember(
                        groupKey=group_email,
                        memberKey=email
                    ).execute()
                    return result.get('isMember', False)
                except HttpError as e:
                    if e.resp.status == 404:
                        # Group or member doesn't exist
                        return False
                    raise
            
            is_member = await loop.run_in_executor(None, check_membership)
            
            # Cache the result
            await cache_service.set(cache_key, is_member, ttl=3600)  # Cache for 1 hour
            
            return is_member
                    
        except Exception as e:
            # If API fails, fall back to checking if email ends with @best.rs
            print(f"Error checking Google Groups membership for {email}: {e}")
            # Fallback: allow @best.rs emails
            return email.lower().endswith("@best.rs")


# Global service instance
google_groups_service = GoogleGroupsService()

