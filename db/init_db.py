import csv

from db.connection import get_connection
from utils.config_handler import agent_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

_initialized = False


def initialize_database() -> None:
    global _initialized
    if _initialized:
        return
    with get_connection() as conn:
        with open(get_abs_path("db/schema.sql"), "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        seed_default_user(conn)
        import_usage_records(conn)
    _initialized = True


def seed_default_user(conn) -> None:
    user_id = str(agent_conf.get("default_user_id", "1001"))
    city = str(agent_conf.get("default_city", "上海"))
    username = str(agent_conf.get("default_username", "演示用户"))
    conn.execute(
        """
        INSERT INTO users(user_id, username, city)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            city = excluded.city
        """,
        (user_id, username, city),
    )


def import_usage_records(conn) -> None:
    csv_path = get_abs_path(agent_conf["external_data_path"])
    required_fields = {"用户ID", "特征", "清洁效率", "耗材", "对比", "时间"}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
            raise ValueError(f"外部数据CSV表头不完整，需要字段：{', '.join(sorted(required_fields))}")

        for row in reader:
            user_id = row["用户ID"].strip()
            if not user_id:
                continue
            conn.execute(
                """
                INSERT INTO users(user_id, username, city)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO NOTHING
                """,
                (user_id, f"演示用户{user_id}", str(agent_conf.get("default_city", "上海"))),
            )
            conn.execute(
                """
                INSERT INTO device_usage_records(
                    user_id, month, feature, efficiency, consumables, comparison
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, month) DO UPDATE SET
                    feature = excluded.feature,
                    efficiency = excluded.efficiency,
                    consumables = excluded.consumables,
                    comparison = excluded.comparison
                """,
                (
                    user_id,
                    row["时间"].strip(),
                    row["特征"].strip(),
                    row["清洁效率"].strip(),
                    row["耗材"].strip(),
                    row["对比"].strip(),
                ),
            )
    logger.info("[initialize_database]SQLite数据库初始化和样例数据导入完成")


if __name__ == "__main__":
    initialize_database()
