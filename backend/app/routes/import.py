from __future__ import annotations

import logging
from typing import Annotated
import csv, sqlite3

from fastapi import APIRouter, status, File, UploadFile

from ..database import Session, get_db
from ..db_helpers import (
    db_create_checkout,
    db_create_item,
    db_commit
)
from ..schemas import CheckedOutCreate, CheckedOutResponse, CheckedOutUpdate
from ..security import get_current_user, require_roles


router = APIRouter(prefix="/import", tags=["import"])
logger = logging.getLogger(__name__)


def get_or_404(db: Session, iid: int) -> CheckedOut:
    checkout = db_get_checkout_by_iid(db, iid)
    if not checkout:
        raise HTTPException(status_code=404, detail=f"Checkout for item {iid} not found")
    return checkout


@router.post("import-csv", response_model=ImportCSVResponse, status_code=status.HTTP_201_CREATED)
async def import_csv(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode("utf-8")

    reader = csv.DictReader(StringIO(decoded))
    cur = db.cursor() # single cursor to reduce overhead

    for row in reader:
        item = (
            {
                "title": row.get("Title"),
                "author": row.get("Author"),
                "barcode": row.get("Bar-Code"),
                "type": row.get("Type"),
                "place_publisher": row.get("Place, Publisher"),
                "language_location": row.get("Language/Location"),
            }
        )
        item = db_create_item(db, cursor=cur, **item)
        iid = item["iid"]
        if row.get("Checked Out"):
            checkout = {
                "iid": iid,
                "uid": 0,
                "start_date": None,
                "due_date": None
            }
            db_create_checkout(db, cursor=cur, **checkout)
        
    db_commit(db)

    return {status: "Success"}