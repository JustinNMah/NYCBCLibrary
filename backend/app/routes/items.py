from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..database import Session, get_db
from ..db_helpers import db_create_item, db_delete_item, db_get_item_by_iid, db_list_items, db_update_item
from ..models import Item, User
from ..schemas import ItemCreate, ItemResponse, ItemUpdate
from ..security import get_current_user, require_roles
from sqlite3 import IntegrityError

router = APIRouter(prefix="/items", tags=["items"])
logger = logging.getLogger(__name__)


def get_or_404(db: Session, iid: int) -> Item:
    item = db_get_item_by_iid(db, iid)
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
    try:
        item = db_create_item(db, **payload.model_dump())
        logger.debug("Created item id=%s", item.iid)
        return item
    except IntegrityError as e:
        # if barcode violates unique constraint, throw a 400 exception
        raise HTTPException(status_code=400, detail=f"Request body {{{payload}}} raised exception: {str(e)}")
    

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
    return db_list_items(db, skip=skip, limit=limit, title=title, barcode=barcode, item_type=item_type)


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
    updates = payload.model_dump(exclude_unset=True)
    get_or_404(db, iid)
    item = db_update_item(db, iid, updates)
    logger.debug("Updated item id=%s", item.iid)
    return item


@router.delete("/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    iid: int,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("admin"))] = None,
):
    logger.debug("Delete item id=%s", iid)
    get_or_404(db, iid)
    db_delete_item(db, iid)
    return None