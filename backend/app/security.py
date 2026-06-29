from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from .database import Session, get_db
from .models import User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    logger.debug("Password verification result=%s", result)
    return result


def get_password_hash(password: str) -> str:
    logger.debug("Hashing password")
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire}
    logger.debug("Creating access token for subject=%s expires_at=%s", subject, expire.isoformat())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict[str, Any]:
    token = token.strip()
    if token.startswith("Bearer "):
        token = token.removeprefix("Bearer ").strip()

    try:
        logger.debug("Decoding access token prefix=%s", token[:12])
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError as exc:
        logger.debug("Token decode failed: %s: %s", type(exc).__name__, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    """Authenticate user by name or email. NotImplemented - use custom SQL."""
    raise NotImplementedError("Use custom SQL helper for user authentication")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """Get current user from bearer token. NotImplemented - use custom SQL."""
    raise NotImplementedError("Use custom SQL helper to get user by token")


def require_roles(*roles: str):
    """Require specific roles. NotImplemented - use custom SQL."""
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        raise NotImplementedError("Use custom SQL helper to check user role")
    return dependency