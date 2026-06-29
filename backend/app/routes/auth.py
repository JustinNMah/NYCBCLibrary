from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import Session, get_db
from ..db_helpers import db_create_user, db_set_user_session_token
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from ..security import authenticate_user, create_access_token, get_current_user, get_password_hash


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    logger.debug("Register request for user=%s email=%s", payload.name, payload.email)
    user = db_create_user(
        db,
        name=payload.name,
        role="user",
        phone=payload.phone,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
    )
    logger.debug("Registered user id=%s", user.uid)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    logger.debug("Login request for username=%s", payload.username)
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        logger.debug("Login failed for username=%s", payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.uid))
    db_set_user_session_token(db, user.uid, access_token)
    logger.debug("Login successful for user id=%s", user.uid)
    return TokenResponse(access_token=access_token)


@router.post("/logout")
def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    logger.debug("Logout request for user id=%s", current_user.uid)
    db_set_user_session_token(db, current_user.uid, None)
    return {"message": "Logged out"}



