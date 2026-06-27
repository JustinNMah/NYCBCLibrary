from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ORMOutModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: str | None = None
    role: Literal["admin", "user", "librarian"] | None = None
    phone: str | None = None
    email: str | None = None
    password: str | None = Field(default=None, min_length=8)


class UserResponse(ORMOutModel, UserBase):
    uid: int
    role: Literal["admin", "user", "librarian"]


class ItemBase(BaseModel):
    barcode: str | None = None
    type: str | None = None
    title: str | None = None
    author: str | None = None
    place_publisher: str | None = None
    language_location: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    barcode: str | None = None
    type: str | None = None
    title: str | None = None
    author: str | None = None
    place_publisher: str | None = None
    language_location: str | None = None


class ItemResponse(ORMOutModel, ItemBase):
    iid: int


class CheckedOutCreate(BaseModel):
    iid: int
    uid: int
    start_date: date
    due_date: date


class CheckedOutUpdate(BaseModel):
    uid: int | None = None
    start_date: date | None = None
    due_date: date | None = None


class CheckedOutResponse(ORMOutModel):
    iid: int
    uid: int
    start_date: date
    due_date: date