from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.logger_handler import logger
from agent.tools.providers import get_external_provider
from db.init_db import initialize_database
from db.repositories import get_device, get_inventory, get_usage_record, search_devices_by_keyword

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


@tool(description="搜索扫地机器人或扫拖一体机器人设备，参数为keyword（关键词），返回匹配设备列表")
def search_devices(keyword: str) -> str:
    initialize_database()
    devices = search_devices_by_keyword(keyword)
    if not devices:
        logger.warning(f"[search_devices]未找到相关设备：{keyword}")
        return f"未找到与“{keyword}”相关的设备。"

    lines = [f"找到与“{keyword}”相关的设备："]
    for device in devices:
        lines.append(
            f"- {device['model_id']}｜{device['model_name']}｜{device['category']}｜"
            f"价格：{device['price']:.0f}元｜特点：{device['features']}"
        )
    return "\n".join(lines)


@tool(description="查询设备详情，参数为model_id（设备型号ID），返回设备参数、价格、功能和适用场景")
def query_device_info(model_id: str) -> str:
    initialize_database()
    device = get_device(model_id)
    if not device:
        logger.warning(f"[query_device_info]未找到设备：{model_id}")
        return f"未找到型号为 {model_id} 的设备信息。"

    return (
        f"型号：{device['model_id']}\n"
        f"名称：{device['model_name']}\n"
        f"类别：{device['category']}\n"
        f"价格：{device['price']:.0f}元\n"
        f"规格：{device['specs']}\n"
        f"功能：{device['features']}\n"
        f"说明：{device['description']}"
    )


@tool(description="查询设备库存，参数为model_id（设备型号ID），返回各仓库库存和总库存")
def query_inventory(model_id: str) -> str:
    initialize_database()
    rows = get_inventory(model_id)
    if not rows:
        logger.warning(f"[query_inventory]未找到库存：{model_id}")
        return f"未找到型号 {model_id} 的库存信息。"

    total_stock = sum(row["stock"] for row in rows)
    lines = [f"型号 {model_id} 的库存情况："]
    for row in rows:
        lines.append(f"- {row['warehouse']}：{row['stock']}台")
    lines.append(f"总库存：{total_stock}台")
    lines.append("状态：有货" if total_stock > 0 else "状态：暂时缺货")
    return "\n".join(lines)

@tool(description="无入参和返回消息，调用后触发中间件自动为报告生成场景注入上下文信息，为后续提示词切换上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"
