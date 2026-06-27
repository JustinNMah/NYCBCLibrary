from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserResponse, UserUpdate
from ..security import get_current_user, get_password_hash, require_roles


router = APIRouter(prefix="/users", tags=["users"])


def get_or_404(db: Session, uid: int) -> User:
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{uid}", response_model=UserResponse)
def get_user(
    uid: int,
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    if current_user.role != "admin" and current_user.uid != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return get_or_404(db, uid)


@router.get("/me", response_model=UserResponse)
def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.put("/{uid}", response_model=UserResponse)
def update_user(
    uid: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    if current_user.role != "admin" and current_user.uid != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user = get_or_404(db, uid)
    updates = payload.model_dump(exclude_unset=True)

    if current_user.role != "admin":
        updates.pop("role", None)

    if "password" in updates:
        updates["hashed_password"] = get_password_hash(updates.pop("password"))

    for field, value in updates.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    uid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    user = get_or_404(db, uid)
    db.delete(user)
    db.commit()
    return None