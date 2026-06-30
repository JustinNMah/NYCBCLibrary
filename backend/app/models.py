from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class User:
    uid: int
    name: str
    role: str
    phone: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    session_token: str | None = None


@dataclass
class Item:
    iid: int
    title: str | None = None
    author: str | None = None
    barcode: str | None = None
    type: str | None = None
    place_publisher: str | None = None
    language_location: str | None = None


@dataclass
class CheckedOut:
    iid: int
    uid: int
    start_date: date
    due_date: date