from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.logger_handler import logger
from agent.tools.providers import get_external_provider
from db.init_db import initialize_database
from db.repositories import get_usage_record

_rag_service = None
provider = get_external_provider()


def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RagSummarizeService()
    return _rag_service

@tool(description="从向量资料库当中检索参考资料")
def rag_summarize(query: str) -> str:
    return get_rag_service().rag_summarize(query)

@tool(description="获取指定城市天气，以消息字符串格式返回")
def get_weather(city: str) -> str:
    return provider.get_weather(city)

@tool(description="获取用户所在城市的定位，以纯字符串格式返回")
def get_user_location() -> str:
    return provider.get_user_location()

@tool(description="获取用户ID，以纯字符串格式返回")
def get_user_id() -> str:
    return provider.get_user_id()

@tool(description="获取当前月份，以纯字符串格式返回")
def get_current_month() -> str:
    return provider.get_current_month()

@tool(description="从外部系统中获取用户在指定月份的使用记录，以纯字符串格式返回，若未检索到则返回明确提示")
def fetch_external_data(user_id: str, month: str) -> str:
    initialize_database()
    data = get_usage_record(user_id, month)
    if not data:
        logger.warning(f"[fetch_external_data]未找到用户ID为{user_id}的指定月份数据{month}")
        return f"未找到用户ID为{user_id}在{month}的使用记录，请确认用户ID或月份是否正确。"
    return str(data)

@tool(description="无入参和返回消息，调用后触发中间件自动为报告生成场景注入上下文信息，为后续提示词切换上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"
