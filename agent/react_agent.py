from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from model.factory import get_chat_model
from utils.prompt_loader import load_system_prompt
from agent.tools.agent_tools import rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, fetch_external_data, fill_context_for_report
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch

class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model = get_chat_model(),
            system_prompt = load_system_prompt(),
            tools = [rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, fetch_external_data, fill_context_for_report],
            middleware = [monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query: str, history: list[dict[str, str]] | None = None):
        messages = []
        for message in history or []:
            role = message.get("role")
            content = message.get("content", "")
            if not content:
                continue
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=query))
        input_dict = {
            "messages": messages
        }
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"

if __name__ == "__main__":
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
