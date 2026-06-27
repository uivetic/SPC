"""Google Workspace integration utilities"""
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional
from app.config import settings

# Putanja do service account JSON fajla
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', settings.GOOGLE_SHEETS_CREDENTIALS_PATH)

# Admin email koji delegira pristup
ADMIN_EMAIL = settings.GOOGLE_ADMIN_EMAIL or 'secretary@best.rs'

# Grupa za proveru članstva
GROUP_EMAIL = settings.GOOGLE_GROUP_EMAIL or 'opsta@best.rs'

# Scopes koje aplikacija zahteva
SCOPES = ['https://www.googleapis.com/auth/admin.directory.group.readonly']


def get_google_admin_service():
    """
    Učitava service account JSON
    Kreira credentials sa domain-wide delegation
    Delegira pristup kao secretary@best.rs
    Vraća Google Admin SDK servis
    """
    # Try to load from environment variable first (for Render/cloud deployment)
    credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    if credentials_json:
        try:
            service_account_info = json.loads(credentials_json)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid GOOGLE_SHEETS_CREDENTIALS JSON: {e}")
    else:
        # Fallback to file path (for local development)
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(
                f"Service account file not found: {SERVICE_ACCOUNT_FILE}. "
                "Either set GOOGLE_SHEETS_CREDENTIALS environment variable or provide a valid file path."
            )
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            service_account_info = json.load(f)
    
    # Kreiraj credentials sa domain-wide delegation
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )
    
    # Delegiraj pristup kao secretary@best.rs
    delegated_credentials = credentials.with_subject(ADMIN_EMAIL)
    
    # Kreiraj i vrati Admin SDK servis
    service = build('admin', 'directory_v1', credentials=delegated_credentials, cache_discovery=False)
    return service


def is_user_in_group(user_email: str) -> bool:
    """
    Proverava da li je korisnik član Google grupe.
    
    - Ako email završava sa @best.rs, vraća True
    - Za vanjske email-ove koristi list() metodu da dobije sve članove grupe
    - Prolazi kroz listu i proverava da li je email u grupi
    - Za @best.rs email-ove koristi hasMember() API
    
    Args:
        user_email: Email adresa korisnika za proveru
        
    Returns:
        True ako je korisnik član grupe, False inače
    """
    # Ako email završava sa @best.rs, automatski ima pristup
    if user_email.lower().endswith("@best.rs"):
        return True
    
    try:
        service = get_google_admin_service()
        print(f"[GROUP CHECK] Checking if {user_email} is in {GROUP_EMAIL}")

        # Direct single-member lookup — avoids pagination issues with list()
        # Returns member info if found, raises 404 HttpError if not a member.
        service.members().get(
            groupKey=GROUP_EMAIL,
            memberKey=user_email
        ).execute()

        print(f"[GROUP CHECK] {user_email} IS a member")
        return True

    except HttpError as e:
        if e.resp.status == 404:
            print(f"[GROUP CHECK] {user_email} is NOT a member (404)")
            return False
        elif e.resp.status == 403:
            print(f"[GROUP CHECK] 403 from Google Admin API — Domain-Wide Delegation may not be configured. Admin: {ADMIN_EMAIL}, Scope: {SCOPES[0]}, Error: {e}")
            raise Exception(f"Domain-Wide Delegation error: {e}")
        else:
            print(f"[GROUP CHECK] HttpError {e.resp.status} for {user_email}: {e}")
            raise Exception(f"HttpError {e.resp.status}: {e}")
    except Exception as e:
        import traceback
        print(f"[GROUP CHECK] Unexpected error for {user_email}: {traceback.format_exc()}")
        raise Exception(f"Unexpected error: {e}")


def check_user_access(user_email: str) -> bool:
    if user_email.lower().endswith("@best.rs"):
        return True
    
    try:
        return is_user_in_group(user_email)
    except Exception:
        return False

