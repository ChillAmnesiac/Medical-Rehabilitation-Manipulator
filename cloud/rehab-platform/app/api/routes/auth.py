from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_settings
from app.core.config import Settings
from app.schemas import SessionRequest
from app.services.auth import authenticate_user, build_session_payload

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/session")
def create_session(
    request: SessionRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user = authenticate_user(db, request.email, request.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_INVALID", "message": "账号或密码不正确"},
        )
    return {"data": build_session_payload(user, settings)}
