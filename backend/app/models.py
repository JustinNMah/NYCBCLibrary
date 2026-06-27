from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "Users"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    email: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    session_token: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class Item(Base):
    __tablename__ = "Items"

    iid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    barcode: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    author: Mapped[str | None] = mapped_column(String(50), nullable=True)
    place_publisher: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_location: Mapped[str | None] = mapped_column(String(50), nullable=True)


class CheckedOut(Base):
    __tablename__ = "CheckedOut"

    iid: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)