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
    query = """
    INSERT INTO Users(name, role, phone, email, hashed_password) 
    VALUES (?, ?, ?, ?, ?)
    RETURNING *;
    """
    params  = (name, role, phone, email, hashed_password)
    res = db.execute(query, params).fetchone()
    res = tuple(res)
    db.commit()
    return User(*tuple(res))


def db_list_users(db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
    query = """
    SELECT * FROM Users LIMIT ? OFFSET ?;
    """
    params  = (limit, skip)
    res = db.execute(query, params).fetchall()
    return [User(*tuple(row)) for row in res]


def db_get_user_by_uid(db: Session, uid: int) -> User | None:
    query = """
    SELECT * FROM Users WHERE uid=?;
    """
    params  = (uid,)
    res = db.execute(query, params).fetchone()
    if res:
        res = tuple(res)
        return User(*tuple(res))
    return None


def db_update_user(db: Session, uid: int, updates: dict[str, object]) -> User:
    # if no updates, the user is unchanged
    if not updates:
        return db_get_user_by_uid(db, uid)
    
    query = ("UPDATE Users SET "
            + ','.join([f"{k}=?" for k in updates.keys()])
            + " WHERE uid=? RETURNING *")
    params  = list(updates.values()) + [uid]
    res = db.execute(query, params).fetchone()
    res = tuple(res)
    db.commit()
    return User(*tuple(res))


def db_delete_user(db: Session, uid: int) -> None:
    query = """
    DELETE FROM Users WHERE uid = ?;
    """
    params  = (uid,)
    db.execute(query, params)
    db.commit()


def db_get_user_by_token(db: Session, token: str) -> User | None:
    query = """
    SELECT * FROM Users WHERE session_token  = ? LIMIT 1;
    """
    params  = (token,)
    res = db.execute(query, params).fetchone()
    if res:
        res = tuple(res)
        return User(*tuple(res))
    return None

def db_set_user_session_token(db: Session, uid: int, token: str | None) -> None:
    query = """
    UPDATE Users SET session_token = ? WHERE uid = ?;
    """
    params  = (token, uid)
    db.execute(query, params)
    db.commit()



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