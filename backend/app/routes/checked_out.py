from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CheckedOut, Item, User
from ..schemas import CheckedOutCreate, CheckedOutResponse, CheckedOutUpdate
from ..security import get_current_user, require_roles


router = APIRouter(prefix="/checked-out", tags=["checked-out"])


def get_or_404(db: Session, iid: int) -> CheckedOut:
    checkout = db.get(CheckedOut, iid)
    if not checkout:
        raise HTTPException(status_code=404, detail=f"Checkout for item {iid} not found")
    return checkout


@router.post("", response_model=CheckedOutResponse, status_code=status.HTTP_201_CREATED)
def create_checkout(
    payload: CheckedOutCreate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin", "librarian"))] = None,
):
    if payload.start_date > payload.due_date:
        raise HTTPException(status_code=400, detail="start_date must be <= due_date")

    if not db.get(Item, payload.iid):
        raise HTTPException(status_code=404, detail=f"Item with id {payload.iid} not found")
    if not db.get(User, payload.uid):
        raise HTTPException(status_code=404, detail=f"User with id {payload.uid} not found")
    if db.get(CheckedOut, payload.iid):
        raise HTTPException(status_code=409, detail="Item is already checked out")

    checkout = CheckedOut(**payload.model_dump())
    db.add(checkout)
    db.commit()
    db.refresh(checkout)
    return checkout


@router.get("", response_model=list[CheckedOutResponse])
def list_checkouts(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin", "librarian"))] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return db.query(CheckedOut).offset(skip).limit(limit).all()


@router.get("/me", response_model=list[CheckedOutResponse])
def list_my_checkouts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return (
        db.query(CheckedOut)
        .filter(CheckedOut.uid == current_user.uid)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{iid}", response_model=CheckedOutResponse)
def get_checkout(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    return get_or_404(db, iid)


@router.put("/{iid}", response_model=CheckedOutResponse)
def update_checkout(
    iid: int,
    payload: CheckedOutUpdate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    checkout = get_or_404(db, iid)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(checkout, field, value)

    if checkout.start_date > checkout.due_date:
        raise HTTPException(status_code=400, detail="start_date must be <= due_date")

    if payload.uid is not None and not db.get(User, payload.uid):
        raise HTTPException(status_code=404, detail=f"User with id {payload.uid} not found")

    db.commit()
    db.refresh(checkout)
    return checkout


@router.delete("/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkout(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    checkout = get_or_404(db, iid)
    db.delete(checkout)
    db.commit()
    return None