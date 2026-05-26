from typing import Callable
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompt, load_report_prompt

# 完成工具监控
@wrap_tool_call
def monitor_tool(request: ToolCallRequest, handler: Callable[[ToolCallRequest], ToolMessage | Command]) -> ToolMessage | Command:
    logger.info(f"[monitor_tool]工具调用开始:{request.tool_call['name']}")
    logger.info(f"[monitor_tool]工具调用参数:{request.tool_call['args']}")
    try:
        result = handler(request)
        logger.info(f"[monitor_tool]工具调用成功:{request.tool_call['name']}")
        if request.tool_call["name"] == "fill_context_for_report":
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        logger.error(f"[monitor_tool]工具调用异常:{request.tool_call['name']}，原因：{str(e)}")
        raise e

# 完成模型执行前输出日志
@before_model
def log_before_model(state: AgentState, runtime: Runtime, ):
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
    logger.debug(f"[log_before_model]消息类型：{type(state['messages'][-1]).__name__} | 消息内容：{state['messages'][-1].content.split()}")
    return None

# 动态切换提示词
@dynamic_prompt # 每一次生成提示词前调用此函数
def report_prompt_switch(request: ModelRequest):
    is_report = request.runtime.context.get("report", False)
    if is_report: # report的值为True时，使用报告提示词
        return load_report_prompt()
    else: # 否则使用系统提示词
        return load_system_prompt()

