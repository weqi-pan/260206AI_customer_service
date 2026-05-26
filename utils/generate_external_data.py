import csv
import os

from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path

external_data = {}

def generate_external_data():
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件不存在:{external_data_path}")
        with open(external_data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_fields = {"用户ID", "特征", "清洁效率", "耗材", "对比", "时间"}
            if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
                raise ValueError(f"外部数据CSV表头不完整，需要字段：{', '.join(sorted(required_fields))}")

            for row in reader:
                user_id: str = row["用户ID"].strip()
                feature: str = row["特征"].strip()
                efficiency: str = row["清洁效率"].strip()
                consumables: str = row["耗材"].strip()
                comparison: str = row["对比"].strip()
                time: str = row["时间"].strip()

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "消耗": consumables,
                    "对比": comparison,
                }
