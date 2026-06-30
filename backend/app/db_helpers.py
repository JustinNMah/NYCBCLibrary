from __future__ import annotations

from datetime import date

from .database import Session
from .models import CheckedOut, Item, User


def _not_implemented(operation: str) -> None:
    raise NotImplementedError(f"Implement custom SQL for {operation}")


def db_create_user(
    db: Session,
    *,
    name: str,
    role: str,
    phone: str | None,
    email: str | None,
    hashed_password: str,
) -> User:
    _not_implemented("create_user")


def db_list_users(db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
    _not_implemented("list_users")


def db_get_user_by_uid(db: Session, uid: int) -> User | None:
    _not_implemented("get_user_by_uid")


def db_update_user(db: Session, uid: int, updates: dict[str, object]) -> User:
    _not_implemented("update_user")


def db_delete_user(db: Session, uid: int) -> None:
    _not_implemented("delete_user")


def db_get_user_by_token(db: Session, token: str) -> User | None:
    _not_implemented("get_user_by_token")


def db_set_user_session_token(db: Session, uid: int, token: str | None) -> None:
    _not_implemented("set_user_session_token")


def db_create_item(
    db: Session,
    *,
    barcode: str | None,
    type: str | None,
    title: str | None,
    author: str | None,
    place_publisher: str | None,
    language_location: str | None,
) -> Item:
    _not_implemented("create_item")


def db_list_items(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    title: str | None = None,
    barcode: str | None = None,
    item_type: str | None = None,
) -> list[Item]:
    _not_implemented("list_items")


def db_get_item_by_iid(db: Session, iid: int) -> Item | None:
    _not_implemented("get_item_by_iid")


def db_update_item(db: Session, iid: int, updates: dict[str, object]) -> Item:
    _not_implemented("update_item")


def db_delete_item(db: Session, iid: int) -> None:
    _not_implemented("delete_item")


def db_create_checkout(
    db: Session,
    *,
    iid: int,
    uid: int,
    start_date: date,
    due_date: date,
) -> CheckedOut:
    _not_implemented("create_checkout")


def db_list_checkouts(db: Session, *, skip: int = 0, limit: int = 100) -> list[CheckedOut]:
    _not_implemented("list_checkouts")


def db_list_my_checkouts(
    db: Session,
    *,
    uid: int,
    skip: int = 0,
    limit: int = 100,
) -> list[CheckedOut]:
    _not_implemented("list_my_checkouts")


def db_get_checkout_by_iid(db: Session, iid: int) -> CheckedOut | None:
    _not_implemented("get_checkout_by_iid")


def db_update_checkout(db: Session, iid: int, updates: dict[str, object]) -> CheckedOut:
    _not_implemented("update_checkout")


def db_delete_checkout(db: Session, iid: int) -> None:
    _not_implemented("delete_checkout")