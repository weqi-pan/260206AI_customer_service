import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path


def get_database_path() -> str:
    storage_conf = agent_conf.get("storage", {})
    sqlite_path = storage_conf.get("sqlite_path", "data/app.db")
    return get_abs_path(sqlite_path)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    db_path = get_database_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
