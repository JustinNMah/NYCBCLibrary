from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from .database import get_db
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
    logger.debug("Authenticating user identifier=%s", identifier)
    user = db.query(User).filter((User.name == identifier) | (User.email == identifier)).first()
    if not user or not user.hashed_password:
        logger.debug("Authentication failed: no user or password hash")
        return None
    if not verify_password(password, user.hashed_password):
        logger.debug("Authentication failed: password mismatch for user id=%s", user.uid if user else None)
        return None
    logger.debug("Authentication successful for user id=%s", user.uid)
    return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    logger.debug("Resolving current user from bearer token")
    payload = _decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = db.get(User, int(user_id))
    except (TypeError, ValueError):
        logger.debug("Current user lookup failed for sub=%r", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user or user.session_token != token:
        logger.debug(
            "Token mismatch or missing user. user_exists=%s token_matches=%s",
            bool(user),
            bool(user and user.session_token == token),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: str):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role != "admin" and current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user

    return dependency