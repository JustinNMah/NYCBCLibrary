from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..database import Session, get_db
from ..db_helpers import (
    db_create_checkout,
    db_delete_checkout,
    db_get_checkout_by_iid,
    db_get_item_by_iid,
    db_get_user_by_uid,
    db_list_checkouts,
    db_list_my_checkouts,
    db_update_checkout,
)
from ..models import CheckedOut, User
from ..schemas import CheckedOutCreate, CheckedOutResponse, CheckedOutUpdate
from ..security import get_current_user, require_roles
from sqlite3 import IntegrityError

router = APIRouter(prefix="/checked-out", tags=["checked-out"])
logger = logging.getLogger(__name__)


def get_or_404(db: Session, iid: int) -> CheckedOut:
    checkout = db_get_checkout_by_iid(db, iid)
    if not checkout:
        raise HTTPException(status_code=404, detail=f"Checkout for item {iid} not found")
    return checkout


@router.post("", response_model=CheckedOutResponse, status_code=status.HTTP_201_CREATED)
def create_checkout(
    payload: CheckedOutCreate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin", "librarian"))] = None,
):
    logger.debug("Create checkout iid=%s uid=%s", payload.iid, payload.uid)
    
    # Don't need this part as SQL automatically throws error when constraints are violated
    # if payload.start_date > payload.due_date:
    #     raise HTTPException(status_code=400, detail="start_date must be <= due_date")
    # if not db_get_item_by_iid(db, payload.iid):
    #     raise HTTPException(status_code=404, detail=f"Item with id {payload.iid} not found")
    # if not db_get_user_by_uid(db, payload.uid):
    #     raise HTTPException(status_code=404, detail=f"User with id {payload.uid} not found")
    # if db_get_checkout_by_iid(db, payload.iid):
    #     raise HTTPException(status_code=409, detail="Item is already checked out")

    try:
        checkout = db_create_checkout(db, **payload.model_dump())
        logger.debug("Created checkout iid=%s uid=%s", checkout.iid, checkout.uid)
        return checkout
    except IntegrityError as e:
        # catch when table constraints are violated
        raise HTTPException(status_code=400, detail=f"Request body {{{payload}}} raised exception: {str(e)}")


@router.get("", response_model=list[CheckedOutResponse])
def list_checkouts(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin", "librarian"))] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    logger.debug("List checkouts skip=%s limit=%s", skip, limit)
    return db_list_checkouts(db, skip=skip, limit=limit)


@router.get("/me", response_model=list[CheckedOutResponse])
def list_my_checkouts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    logger.debug("List my checkouts user_id=%s skip=%s limit=%s", current_user.uid, skip, limit)
    return db_list_my_checkouts(db, uid=current_user.uid, skip=skip, limit=limit)


@router.get("/{iid}", response_model=CheckedOutResponse)
def get_checkout(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Get checkout iid=%s", iid)
    return get_or_404(db, iid)


@router.put("/{iid}", response_model=CheckedOutResponse)
def update_checkout(
    iid: int,
    payload: CheckedOutUpdate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Update checkout iid=%s", iid)
    updates = payload.model_dump(exclude_unset=True)
    get_or_404(db, iid)

    if updates.get("start_date") is not None and updates.get("due_date") is not None and updates["start_date"] > updates["due_date"]:
        raise HTTPException(status_code=400, detail="start_date must be <= due_date")

    if payload.uid is not None and not db_get_user_by_uid(db, payload.uid):
        raise HTTPException(status_code=404, detail=f"User with id {payload.uid} not found")

    checkout = db_update_checkout(db, iid, updates)
    logger.debug("Updated checkout iid=%s", checkout.iid)
    return checkout


@router.delete("/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkout(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Delete checkout iid=%s", iid)
    get_or_404(db, iid)
    db_delete_checkout(db, iid)
    return None