import random
from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.generate_external_data import generate_external_data, external_data
from utils.logger_handler import logger

rag = RagSummarizeService()
user_id = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]

@tool(description="从向量资料库当中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

@tool(description="获取指定城市天气，以消息字符串格式返回")
def get_weather(city: str) -> str:
    return f"城市{city}的天气是晴天，气温为26摄氏度，空气湿度为78%，南风2级，AQI21，最近六小时降雨概率低"

@tool(description="获取用户所在城市的定位，以纯字符串格式返回")
def get_user_location() -> str:
    return random.choice(["上海", "北京", "广州", "深圳"])

@tool(description="获取用户ID，以纯字符串格式返回")
def get_user_id() -> str:
    return random.choice(user_id)

@tool(description="获取当前月份，以纯字符串格式返回")
def get_current_month() -> str:
    return random.choice(month_arr)

@tool(description="从外部系统中获取用户在指定月份的使用记录，以纯字符串格式返回，若未检索到则返回为空")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()
    data = external_data.get(user_id, {}).get(month, {})
    if not data:
        logger.warning(f"[fetch_external_data]未找到用户ID为{user_id}的指定月份数据{month}")
        return ""
    return str(data)

@tool(description="无入参和返回消息，调用后触发中间件自动为报告生成场景注入上下文信息，为后续提示词切换上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"