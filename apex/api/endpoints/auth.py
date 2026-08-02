"""Authentication Endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from apex.config import settings
import structlog

log = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    api_key: str


def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/token")
async def login(req: LoginRequest):
    # In production: validate against database
    if req.api_key == settings.APP_SECRET_KEY:
        token = create_access_token({"sub": "admin", "tenant": "garcar"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(401, "Invalid API key")


@router.get("/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return {"user": payload.get("sub"), "tenant": payload.get("tenant")}
    except JWTError:
        raise HTTPException(401, "Invalid token")
