from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Generator, Protocol

from .config import DATABASE_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH_FULL = PROJECT_ROOT / DATABASE_PATH


class Session(Protocol):
    """Temporary database session interface for future raw SQL helpers."""

    def execute(self, __sql: str, __parameters: Any = None, /) -> Any: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


def get_db() -> Generator[Session, None, None]:
    """Get a raw SQLite database connection."""
    conn = sqlite3.connect(str(DATABASE_PATH_FULL))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Placeholder for database initialization via SQL migrations."""
    return None