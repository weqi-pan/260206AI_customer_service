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
        seed_devices_and_inventory(conn)
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


def seed_devices_and_inventory(conn) -> None:
    devices = [
        (
            "R1-Lite",
            "清巧扫地机器人 R1-Lite",
            "扫地机器人",
            "吸力2800Pa; 续航100分钟; 适合60-90平方米户型; 支持APP控制",
            "轻量入门款，适合小户型日常清扫和木地板、瓷砖环境。",
            1299.0,
            "自动回充; 定时清扫; 防跌落传感器; 低噪音模式",
        ),
        (
            "R1-Pro",
            "全能扫拖机器人 R1-Pro",
            "扫拖一体机器人",
            "吸力4500Pa; 续航150分钟; 适合90-140平方米户型; 支持地毯增压",
            "均衡型扫拖一体机，适合多房间家庭和混合地面。",
            2499.0,
            "扫拖一体; 激光导航; 地毯增压; 分区清扫; 断点续扫",
        ),
        (
            "RT2-Max",
            "旗舰自清洁扫拖机器人 RT2-Max",
            "扫拖一体机器人",
            "吸力6000Pa; 续航200分钟; 适合140平方米以上户型; 自动集尘洗拖布",
            "旗舰款，适合大户型、宠物家庭和高频拖地需求。",
            3999.0,
            "自动集尘; 自动洗拖布; 热风烘干; AI避障; 多楼层地图",
        ),
    ]
    conn.executemany(
        """
        INSERT INTO devices(model_id, model_name, category, specs, description, price, features)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(model_id) DO UPDATE SET
            model_name = excluded.model_name,
            category = excluded.category,
            specs = excluded.specs,
            description = excluded.description,
            price = excluded.price,
            features = excluded.features
        """,
        devices,
    )

    inventory = [
        ("R1-Lite", "北京仓", 36),
        ("R1-Lite", "上海仓", 24),
        ("R1-Pro", "北京仓", 18),
        ("R1-Pro", "上海仓", 32),
        ("R1-Pro", "广州仓", 12),
        ("RT2-Max", "上海仓", 9),
        ("RT2-Max", "广州仓", 7),
    ]
    conn.executemany(
        """
        INSERT INTO inventory(model_id, warehouse, stock)
        VALUES (?, ?, ?)
        ON CONFLICT(model_id, warehouse) DO UPDATE SET
            stock = excluded.stock,
            updated_at = CURRENT_TIMESTAMP
        """,
        inventory,
    )


if __name__ == "__main__":
    initialize_database()
