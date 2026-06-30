from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..database import Session, get_db
from ..db_helpers import db_delete_user, db_get_user_by_uid, db_list_users, db_update_user
from ..models import User
from ..schemas import UserResponse, UserUpdate
from ..security import get_current_user, get_password_hash, require_roles


router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


def get_or_404(db: Session, uid: int) -> User:
    user = db_get_user_by_uid(db, uid)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {uid} not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    logger.debug("List users skip=%s limit=%s", skip, limit)
    return db_list_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    logger.debug("Read current user id=%s", current_user.uid)
    return current_user


@router.get("/{uid}", response_model=UserResponse)
def get_user(
    uid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Get user id=%s", uid)
    return get_or_404(db, uid)


@router.put("/{uid}", response_model=UserResponse)
def update_user(
    uid: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Update user id=%s", uid)
    get_or_404(db, uid)
    updates = payload.model_dump(exclude_unset=True)

    if "password" in updates:
        updates["hashed_password"] = get_password_hash(updates.pop("password"))

    return db_update_user(db, uid, updates)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    uid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Delete user id=%s", uid)
    get_or_404(db, uid)
    db_delete_user(db, uid)
    return None