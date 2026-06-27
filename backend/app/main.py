from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


# Project root: .../NYCBCLibrary
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'library.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "Users"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)


class Item(Base):
    __tablename__ = "Items"

    iid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    place_publisher: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language_location: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class CheckedOut(Base):
    __tablename__ = "CheckedOut"

    iid: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)


class UserCreate(BaseModel):
    name: str
    role: str = "user"
    phone: Optional[str] = None
    email: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: int
    name: str
    role: str
    phone: Optional[str]
    email: Optional[str]


class ItemCreate(BaseModel):
    barcode: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    place_publisher: Optional[str] = None
    language_location: Optional[str] = None


class ItemUpdate(BaseModel):
    barcode: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    place_publisher: Optional[str] = None
    language_location: Optional[str] = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iid: int
    barcode: Optional[str]
    type: Optional[str]
    title: Optional[str]
    author: Optional[str]
    place_publisher: Optional[str]
    language_location: Optional[str]


class CheckedOutCreate(BaseModel):
    iid: int
    uid: int
    start_date: date
    due_date: date


class CheckedOutUpdate(BaseModel):
    uid: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class CheckedOutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iid: int
    uid: int
    start_date: date
    due_date: date


Base.metadata.create_all(bind=engine)

app = FastAPI(title="NYCBC Library API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "NYCBC Library API"}


# ----- Users CRUD -----
@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return db.query(User).offset(skip).limit(limit).all()


@app.get("/users/{uid}", response_model=UserOut)
def get_user(uid: int, db: Session = Depends(get_db)):
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{uid}", response_model=UserOut)
def update_user(uid: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(uid: int, db: Session = Depends(get_db)):
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None


# ----- Items CRUD -----
@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Item barcode must be unique")
    db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    title: Optional[str] = None,
    barcode: Optional[str] = None,
    item_type: Optional[str] = Query(default=None, alias="type"),
):
    query = db.query(Item)
    if title:
        query = query.filter(Item.title.contains(title))
    if barcode:
        query = query.filter(Item.barcode == barcode)
    if item_type:
        query = query.filter(Item.type == item_type)
    return query.offset(skip).limit(limit).all()


@app.get("/items/{iid}", response_model=ItemOut)
def get_item(iid: int, db: Session = Depends(get_db)):
    item = db.get(Item, iid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{iid}", response_model=ItemOut)
def update_item(iid: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(Item, iid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

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


@app.delete("/items/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(iid: int, db: Session = Depends(get_db)):
    item = db.get(Item, iid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None


# ----- CheckedOut CRUD -----
@app.post("/checked-out", response_model=CheckedOutOut, status_code=status.HTTP_201_CREATED)
def create_checkout(payload: CheckedOutCreate, db: Session = Depends(get_db)):
    if payload.start_date > payload.due_date:
        raise HTTPException(status_code=400, detail="start_date must be <= due_date")

    item = db.get(Item, payload.iid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    user = db.get(User, payload.uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.get(CheckedOut, payload.iid)
    if existing:
        raise HTTPException(status_code=409, detail="Item is already checked out")

    checkout = CheckedOut(**payload.model_dump())
    db.add(checkout)
    db.commit()
    db.refresh(checkout)
    return checkout


@app.get("/checked-out", response_model=list[CheckedOutOut])
def list_checkouts(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return db.query(CheckedOut).offset(skip).limit(limit).all()


@app.get("/checked-out/{iid}", response_model=CheckedOutOut)
def get_checkout(iid: int, db: Session = Depends(get_db)):
    checkout = db.get(CheckedOut, iid)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    return checkout


@app.put("/checked-out/{iid}", response_model=CheckedOutOut)
def update_checkout(iid: int, payload: CheckedOutUpdate, db: Session = Depends(get_db)):
    checkout = db.get(CheckedOut, iid)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(checkout, field, value)

    if checkout.start_date > checkout.due_date:
        raise HTTPException(status_code=400, detail="start_date must be <= due_date")

    if payload.uid is not None:
        user = db.get(User, payload.uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    db.commit()
    db.refresh(checkout)
    return checkout


@app.delete("/checked-out/{iid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkout(iid: int, db: Session = Depends(get_db)):
    checkout = db.get(CheckedOut, iid)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    db.delete(checkout)
    db.commit()
    return None
