from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Item, User
from ..schemas import ItemCreate, ItemResponse, ItemUpdate
from ..security import get_current_user, require_roles


router = APIRouter(prefix="/items", tags=["items"])


def get_or_404(db: Session, iid: int) -> Item:
    item = db.get(Item, iid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    item = Item(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Item barcode must be unique")
    db.refresh(item)
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
    return get_or_404(db, iid)


@router.put("/{iid}", response_model=ItemResponse)
def update_item(
    iid: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    item = get_or_404(db, iid)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Item barcode must be unique")
    db.refresh(item)
    return item


@router.delete("/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    item = get_or_404(db, iid)
    db.delete(item)
    db.commit()
    return None