from db.connection import get_connection


def get_user(user_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id, username, city, phone FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def get_usage_record(user_id: str, month: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT user_id, month, feature, efficiency, consumables, comparison
            FROM device_usage_records
            WHERE user_id = ? AND month = ?
            """,
            (user_id, month),
        ).fetchone()
    if not row:
        return None
    return {
        "用户ID": row["user_id"],
        "月份": row["month"],
        "特征": row["feature"],
        "效率": row["efficiency"],
        "消耗": row["consumables"],
        "对比": row["comparison"],
    }


def search_devices_by_keyword(keyword: str, limit: int = 3) -> list[dict]:
    pattern = f"%{keyword.strip()}%"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT model_id, model_name, category, specs, description, price, features
            FROM devices
            WHERE model_id LIKE ?
               OR model_name LIKE ?
               OR category LIKE ?
               OR specs LIKE ?
               OR description LIKE ?
               OR features LIKE ?
            ORDER BY price ASC
            LIMIT ?
            """,
            (pattern, pattern, pattern, pattern, pattern, pattern, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_device(model_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT model_id, model_name, category, specs, description, price, features
            FROM devices
            WHERE model_id = ?
            """,
            (model_id,),
        ).fetchone()
    return dict(row) if row else None


def get_inventory(model_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT model_id, warehouse, stock, updated_at
            FROM inventory
            WHERE model_id = ?
            ORDER BY warehouse ASC
            """,
            (model_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_message(session_id: str, user_id: str, role: str, content: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversation_history(session_id, user_id, role, content)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, user_id, role, content),
        )


def get_recent_messages(session_id: str, limit: int = 20) -> list[dict[str, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM conversation_history
            WHERE session_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]
