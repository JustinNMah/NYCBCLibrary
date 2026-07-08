import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "library.db")
MIGRATIONS_PATH = os.getenv("MIGRATIONS_PATH")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / DATABASE_PATH
MIGRATIONS_DIR = PROJECT_ROOT / MIGRATIONS_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_migrations_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def applied_migrations(conn):
    rows = conn.execute(
        "SELECT filename FROM schema_migrations"
    ).fetchall()
    return {row[0] for row in rows}


def apply_migration(conn, migration_file):
    print(f"Applying {migration_file.name}...")

    sql = migration_file.read_text(encoding="utf-8")

    with conn:
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)",
            (migration_file.name,),
        )


def migrate():
    conn = get_connection()

    ensure_migrations_table(conn)

    applied = applied_migrations(conn)

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for migration in migration_files:
        if migration.name not in applied:
            apply_migration(conn, migration)

    conn.close()

    print("Database is up to date.")


if __name__ == "__main__":
    migrate()