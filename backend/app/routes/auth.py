from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from ..security import authenticate_user, create_access_token, get_current_user, get_password_hash


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        name=payload.name,
        role="user",
        phone=payload.phone,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.uid))
    user.session_token = access_token
    db.commit()
    return TokenResponse(access_token=access_token)


@router.post("/logout")
def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    current_user.session_token = None
    db.commit()
    return {"message": "Logged out"}



