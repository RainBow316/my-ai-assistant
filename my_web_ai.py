import streamlit as st
from zhipuai import ZhipuAI

# === 1. 基础页面配置 ===
st.set_page_config(page_title="我的私人 AI 助手", page_icon="🤖")
st.title("🤖 我的智谱 GLM-4 助手")

# === 2. 智能获取 API Key (这是你修改的核心部分) ===
# 逻辑：优先检查 Streamlit 的 secrets (云端环境变量)，如果没有，则在侧边栏显示输入框
api_key = None

if "ZHIPU_API_KEY" in st.secrets:
    # 情况 A：在云端或本地 .streamlit/secrets.toml 中找到了 Key
    api_key = st.secrets["ZHIPU_API_KEY"]
    st.sidebar.success("✅ 云端 Key 已自动加载")
else:
    # 情况 B：没找到 Key，显示输入框让用户手动填
    api_key = st.sidebar.text_input("请输入智谱 API Key", type="password")
    if not api_key:
        st.sidebar.info("👈 请在左侧输入 Key，或在云端配置 Secrets")

# === 3. 初始化聊天记录 (记忆功能) ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === 4. 渲染历史聊天记录 ===
# 每次刷新页面时，把之前的对话重画一遍
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# === 5. 处理用户输入 ===
if prompt := st.chat_input("输入你的问题..."):
    # 5.1 先在界面上显示用户说的话
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5.2 只有拿到了 Key 才去请求 AI
    if api_key:
        try:
            # 实例化客户端
            client = ZhipuAI(api_key=api_key)
            
            # 发起请求
            response = client.chat.completions.create(
                model="glm-4",  # 想要更便宜/更快，可以改成 "glm-4-flash"
                messages=st.session_state.messages,
                stream=True,
            )
            
            # 5.3 流式输出 AI 的回答 (打字机效果)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in response:
                    # 获取当前这一小块的内容
                    chunk_content = chunk.choices[0].delta.content or ""
                    full_response += chunk_content
                    # 显示当前内容 + 光标
                    message_placeholder.markdown(full_response + "▌")
                
                # 循环结束，显示最终完整内容（去掉光标）
                message_placeholder.markdown(full_response)
            
            # 5.4 把 AI 的回答存入记忆
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"❌ 发生错误: {e}")
    else:
        st.error("请先配置 API Key 才能进行对话！")