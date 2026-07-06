from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import User
from app.security import create_access_token, hash_password, verify_password


DEFAULT_EMAIL = "3245056131@qq.com"
DEFAULT_PASSWORD = "1234"


def seed_default_user(session: Session) -> None:
    existing = session.scalar(select(User).where(User.email == DEFAULT_EMAIL))
    if existing:
        return
    session.add(
        User(
            email=DEFAULT_EMAIL,
            password_hash=hash_password(DEFAULT_PASSWORD),
            name="康复用户",
            rehab_stage="亚急性期",
            affected_side="左侧",
            medical_constraints="",
        )
    )
    session.commit()


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = session.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def build_session_payload(user: User, settings: Settings) -> dict[str, object]:
    return {
        "access_token": create_access_token(
            subject=str(user.id),
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            ttl_minutes=settings.access_token_ttl_minutes,
        ),
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_minutes * 60,
    }
