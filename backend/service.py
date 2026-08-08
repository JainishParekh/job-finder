from backend.settings import settings
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

ADMIN_API_KEY = settings.admin_api_key

security = HTTPBearer()


def verify_admin_access(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates the Bearer token. Only you know this token.
    """
    if credentials.credentials != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
