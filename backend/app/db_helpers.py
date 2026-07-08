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
    item = db.execute(
        """
        INSERT INTO items (
            barcode,
            type,
            title,
            author,
            place_publisher,
            language_location
        )
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING iid;
        """,
        (
            barcode,
            type,
            title,
            author,
            place_publisher,
            language_location,
        ),
    ).fetchone()
    db.commit()

    return Item(*tuple(item))


def db_list_items(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    title: str | None = None,
    barcode: str | None = None,
    item_type: str | None = None,
) -> list[Item]:
    query = "SELECT * FROM Items WHERE 1=1"
    params = ()
    if title:
        query += " AND title=?"
        params += (title,)
    if barcode:
        query += " AND barcode=?"
        params += (barcode,)
    if item_type:
        query += " AND item_type=?"
        params += (item_type,)
    query += " LIMIT ? OFFSET ?;"
    params += (limit, skip)
    res = db.execute(query, params).fetchall()
    return [Item(*tuple(row)) for row in res]


def db_get_item_by_iid(db: Session, iid: int) -> Item | None:
    query = """
    SELECT * FROM Items WHERE iid=?;
    """
    params  = (iid,)
    res = db.execute(query, params).fetchone()
    if res:
        return Item(*tuple(res))
    return None


def db_update_item(db: Session, iid: int, updates: dict[str, object]) -> Item:
    if not updates:
        return db_get_item_by_iid(db, iid)
    
    query = ("UPDATE Items SET "
            + ','.join([f"{k}=?" for k in updates.keys()])
            + " WHERE iid=? RETURNING *")
    params  = list(updates.values()) + [iid]
    res = db.execute(query, params).fetchone()
    db.commit()
    return Item(*tuple(res))


def db_delete_item(db: Session, iid: int) -> None:
    query = """
    DELETE FROM Items WHERE iid=?;
    """
    params  = (iid,)
    db.execute(query, params)
    db.commit()


def db_create_checkout(
    db: Session,
    *,
    iid: int,
    uid: int,
    start_date: date | None,
    due_date: date | None,
) -> CheckedOut:
    cur = db.cursor()
    
    checkout = cur.execute(
        """
        INSERT INTO CheckedOut (
            iid,
            uid,
            start_date,
            due_date
        )
        VALUES (?, ?, ?, COALESCE(?, date('now', '+1 month')))
        RETURNING
            iid,
            uid,
            start_date,
            due_date
        """,
        (
            iid,
            uid,
            start_date,
            due_date,
        ),
    ).fetchone()

    return CheckedOut(
        iid=checkout[0],
        uid=checkout[1],
        start_date=checkout[2],
        due_date=checkout[3],
    )

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

def db_commit(db: Session) -> None:
    db.commit()