from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Item, User
from ..schemas import ItemCreate, ItemResponse, ItemUpdate
from ..security import get_current_user, require_roles


router = APIRouter(prefix="/items", tags=["items"])
logger = logging.getLogger(__name__)


def get_or_404(db: Session, iid: int) -> Item:
    item = db.get(Item, iid)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id {iid} not found")
    return item


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Create item title=%s barcode=%s", payload.title, payload.barcode)
    item = Item(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.debug("Create item failed barcode=%s", payload.barcode)
        raise HTTPException(status_code=409, detail="Item barcode must be unique")
    db.refresh(item)
    logger.debug("Created item id=%s", item.iid)
    return item

# TODO: update route to handle use-cases for filtering by certain fields and sorting by criteria
@router.get("", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    title: str | None = None,
    barcode: str | None = None,
    item_type: str | None = Query(default=None, alias="type"),
):
    logger.debug("List items skip=%s limit=%s title=%s barcode=%s type=%s", skip, limit, title, barcode, item_type)
    query = db.query(Item)
    if title:
        query = query.filter(Item.title.contains(title))
    if barcode:
        query = query.filter(Item.barcode == barcode)
    if item_type:
        query = query.filter(Item.type == item_type)
    return query.offset(skip).limit(limit).all()


@router.get("/{iid}", response_model=ItemResponse)
def get_item(iid: int, db: Session = Depends(get_db)):
    logger.debug("Get item id=%s", iid)
    return get_or_404(db, iid)


@router.put("/{iid}", response_model=ItemResponse)
def update_item(
    iid: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Update item id=%s", iid)
    item = get_or_404(db, iid)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.debug("Update item failed barcode conflict id=%s", iid)
        raise HTTPException(status_code=409, detail="Item barcode must be unique")
    db.refresh(item)
    logger.debug("Updated item id=%s", item.iid)
    return item


@router.delete("/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Delete item id=%s", iid)
    item = get_or_404(db, iid)
    db.delete(item)
    db.commit()
    return None