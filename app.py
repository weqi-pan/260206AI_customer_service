import time

import streamlit as st
from agent.react_agent import ReactAgent
from db.init_db import initialize_database
from db.repositories import get_recent_messages, save_message
from utils.config_handler import agent_conf
from utils.logger_handler import logger

initialize_database()

# 标题
st.title("扫地机器人客服")
st.divider()

# 创建机器人
if "agent" not in st.session_state:
    try:
        st.session_state["agent"] = ReactAgent()
    except Exception as e:
        logger.error(f"[app]Agent初始化失败：{str(e)}", exc_info=True)
        st.error(str(e))
        st.stop()
# 历史会话记录保存
user_id = str(agent_conf.get("default_user_id", "1001"))
session_id = str(agent_conf.get("conversation_session_id", f"{user_id}-default"))
history_limit = int(agent_conf.get("conversation_history_limit", 20))
st.session_state.setdefault("session_id", session_id)

if "message" not in st.session_state:
    st.session_state["message"] = get_recent_messages(st.session_state["session_id"], history_limit)

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入提示词
prompt = st.chat_input("请输入你的问题：")

if prompt:
    st.chat_message("user").write(prompt)
    history = st.session_state["message"].copy()
    st.session_state["message"].append({"role": "user", "content": prompt})
    save_message(st.session_state["session_id"], user_id, "user", prompt)
    response_message = []
    with st.spinner("智能客服处理中..."):
        def capture(generator, chunk_list):
            try:
                for chunk in generator:
                    chunk_list.append(chunk)
                    for char in chunk:
                        time.sleep(0.01)
                        yield char
            except Exception as e:
                logger.error(f"[app]Agent执行失败：{str(e)}", exc_info=True)
                error_message = f"处理请求时出现错误：{str(e)}"
                chunk_list.append(error_message)
                yield error_message

        res_stream = st.session_state["agent"].execute_stream(prompt, history=history)
        st.chat_message("assistant").write_stream(capture(res_stream, response_message))
        assistant_content = "".join(response_message).strip()
        if not assistant_content:
            assistant_content = "暂时没有生成有效回复，请稍后重试。"
        st.session_state["message"].append({"role": "assistant", "content": assistant_content})
        save_message(st.session_state["session_id"], user_id, "assistant", assistant_content)
        st.rerun()
