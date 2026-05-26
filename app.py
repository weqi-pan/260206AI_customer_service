import time

import streamlit as st
from agent.react_agent import ReactAgent

# 标题
st.title("扫地机器人客服")
st.divider()

# 创建机器人
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()
# 历史会话记录保存
if "message" not in st.session_state:
    st.session_state["message"] =[]

for message in st.session_state["message"]:
    st.chat_message("assistant").write(message["content"])

# 用户输入提示词
prompt = st.chat_input("请输入你的问题：")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})
    response_message = []
    with st.spinner("智能客服处理中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)
        def capture(generator, chunk_list):
            for chunk in generator:
                chunk_list.append(chunk)
                for char in chunk:
                    time.sleep(0.01)
                    yield  char
        st.chat_message("assistant").write(capture(res_stream, response_message))
        st.session_state["message"].append({"role": "assistant", "content": response_message[-1]})
        st.rerun()