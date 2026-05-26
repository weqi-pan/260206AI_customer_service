# 扫地机器人智能客服 Agent

> 基于 LangChain + LangGraph + 大语言模型 + RAG 技术构建的专业扫地机器人智能客服系统

---

## 项目简介

本项目是一个采用 ReAct（推理-行动-观察）架构的扫地机器人智能客服 Agent 系统。系统结合了 RAG（检索增强生成）技术，通过向量数据库存储专业知识库，能够为用户提供专业的扫地机器人咨询服务。

### 核心特性

- **ReAct 架构**：采用"思考→行动→观察→再思考"的循环推理模式
- **RAG 技术**：基于向量检索的知识库问答，提供专业领域知识
- **动态提示词**：根据场景（常规咨询/报告生成）自动切换系统提示词
- **中间件模式**：工具调用监控、日志记录、动态提示词切换
- **流式输出**：实时展示 Agent 思考过程和回答内容
- **环境感知**：根据用户所在城市天气提供使用建议

---

## 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| AI 框架 | LangChain | 1.2.10 | LLM 应用开发框架 |
| Agent 框架 | LangGraph | 1.0.8 | Agent 状态机与工具编排 |
| 向量数据库 | Chroma | - | 知识库向量存储 |
| Web 框架 | Streamlit | 1.54.0 | Web 应用界面 |
| 大模型 | 通义千问 (qwen3-max) | - | 对话生成与推理 |
| 嵌入模型 | DashScope (text-embedding-v4) | - | 文本向量化 |

```bash
pip install -r requirements.txt
```

---

## 项目结构

```
260206langchain_demo/
├── agent/                          # Agent 核心模块
│   ├── tools/                      # 工具集合
│   │   ├── agent_tools.py         # 7个工具函数定义
│   │   ├── providers.py           # 外部服务Provider（默认演示实现）
│   │   └── middleware.py          # 中间件（监控、日志、提示词切换）
│   └── react_agent.py             # ReAct Agent 主类
│
├── config/                         # 配置文件目录
│   ├── agent.yml                  # Agent 配置
│   ├── chroma.yml                 # 向量数据库配置
│   ├── prompts.yml                # 提示词路径配置
│   └── rag.yml                    # RAG 模型配置
│
├── data/                           # 知识库数据
│   ├── external/records.csv        # 用户使用记录
│   ├── 故障排除.txt
│   ├── 扫地机器人100问.pdf
│   ├── 扫拖一体机器人100问.txt
│   ├── 维护保养.txt
│   └── 选购指南.txt
│
├── db/                            # SQLite 本地数据层
│   ├── connection.py              # SQLite 连接管理
│   ├── init_db.py                 # 建表与样例数据导入
│   ├── repositories.py            # 用户、使用记录、会话历史查询
│   └── schema.sql                 # SQLite 表结构
│
├── model/factory.py                # 模型工厂（聊天模型、嵌入模型）
├── prompts/                       # 提示词模板目录
│   ├── main_prompt.txt            # 主系统提示词
│   ├── rag_summary_prompt.txt     # RAG 总结提示词
│   └── report_prompt.txt          # 报告生成提示词
│
├── rag/                           # RAG 服务模块
│   ├── rag_service.py             # RAG 服务类
│   └── vector_store.py            # 向量存储服务
│
├── utils/                         # 工具类
│   ├── config_handler.py          # 配置加载器
│   ├── file_handler.py            # 文件处理
│   ├── generate_external_data.py  # 外部数据生成器
│   ├── logger_handler.py          # 日志处理器
│   ├── path_tool.py               # 路径工具
│   └── prompt_loader.py           # 提示词加载器
│
├── app.py                         # Streamlit 应用入口
└── requirements.txt               # Python 依赖
```

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│                      (app.py - 用户界面层)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ReactAgent (ReAct 架构)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Middleware  │  │    Tools     │  │   Prompts    │      │
│  │   (3个)      │  │   (7个工具)   │  │  (动态切换)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Agent                          │
│         (create_agent + 中间件装饰器模式)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      模型层                                  │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  ChatTongyi      │      │ DashScopeEmbed-  │            │
│  │  (qwen3-max)     │      │  dings (v4)      │            │
│  └──────────────────┘      └──────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   数据层                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chroma向量库 │  │ 外部数据CSV  │  │  知识库文件   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### ReAct 执行流程

```
用户提问
    ↓
思考 (Thought) - 分析问题，判断需要什么信息
    ↓
行动 (Action) - 调用相应工具获取信息
    ↓
观察 (Observation) - 获取工具返回结果
    ↓
再次思考 - 判断信息是否充足
    ↓
信息充足 → 生成最终回答
信息不足 → 继续调用工具 (最多5次)
```

---

## 功能实现路径

### 1. 应用入口层

**文件：`app.py`**

| 功能 | 说明 |
|------|------|
| 初始化 ReactAgent | 创建 Agent 实例 |
| 管理会话历史 | 保存用户和助手对话记录 |
| 提供聊天界面 | Streamlit 聊天输入框 |
| 流式输出响应 | 打字机效果显示回答 |

**联动关系**：`app.py` → `ReactAgent` → `LangGraph Agent` → 大模型

---

### 2. Agent 核心层

**文件：`agent/react_agent.py`**

| 组件 | 功能 |
|------|------|
| `ReactAgent.__init__()` | 初始化 Agent，组装模型、提示词、工具、中间件 |
| `ReactAgent.execute_stream()` | 流式执行查询，返回生成器 |

**依赖注入**：
- 模型：`model/factory.py` 的 `chat_model`
- 提示词：`utils/prompt_loader.py` 的 `load_system_prompt()`
- 工具：`agent/tools/agent_tools.py` 的 7 个工具函数
- 中间件：`agent/tools/middleware.py` 的 3 个中间件

---

### 3. 工具层

**文件：`agent/tools/agent_tools.py`**

| 工具名称 | 功能描述 | 参数 | 返回值 | 调用模块 |
|---------|---------|------|--------|----------|
| `rag_summarize` | 向量库检索+总结 | query（检索词） | 参考资料总结 | `rag/rag_service.py` |
| `get_weather` | 获取城市天气 | city（城市名） | 天气信息字符串 | Provider |
| `get_user_location` | 获取用户城市 | 无 | SQLite 用户城市或配置默认城市 | Provider |
| `get_user_id` | 获取用户ID | 无 | 配置中的默认用户ID | Provider |
| `get_current_month` | 获取当前月份 | 无 | 当前月份或演示月份 | Provider |
| `fetch_external_data` | 获取使用记录 | user_id, month | 使用记录数据 | `db/repositories.py` |
| `fill_context_for_report` | 触发报告上下文 | 无 | 确认消息 | 设置 context["report"]=True |
| `search_devices` | 搜索设备 | keyword | 匹配设备列表 | `db/repositories.py` |
| `query_device_info` | 查询设备详情 | model_id | 设备参数、价格、功能 | `db/repositories.py` |
| `query_inventory` | 查询设备库存 | model_id | 各仓库库存和总库存 | `db/repositories.py` |

**工具联动**：
- `rag_summarize` → `RagSummarizeService` → `VectorStoreService` → Chroma 向量库
- `fetch_external_data` → `db.repositories.get_usage_record()` → SQLite 使用记录
- `search_devices/query_device_info/query_inventory` → SQLite 设备与库存数据
- `fill_context_for_report` → 触发中间件设置 `context["report"]=True` → 动态提示词切换

---

### 4. 中间件层

**文件：`agent/tools/middleware.py`**

| 中间件 | 装饰器 | 功能 | 执行时机 |
|--------|--------|------|----------|
| 工具监控 | `@wrap_tool_call` | 记录工具调用开始/成功/失败，特殊处理报告场景 | 每次工具调用前后 |
| 日志记录 | `@before_model` | 记录模型调用前的消息状态 | 模型调用前 |
| 动态提示词 | `@dynamic_prompt` | 根据 context["report"] 切换提示词 | 每次生成提示词前 |

**联动关系**：
- `monitor_tool` 检测到 `fill_context_for_report` 调用 → 设置 `context["report"]=True`
- `report_prompt_switch` 检测 `context["report"]` → 切换到 `report_prompt.txt`

---

### 5. RAG 服务层

**文件：`rag/rag_service.py`**

| 方法 | 功能 | 依赖 |
|------|------|------|
| `retrieve(query)` | 从向量库检索相关文档 | `VectorStoreService` |
| `rag_summarize(query)` | 检索+生成总结 | `prompt` + `model` + `StrOutputParser` |

**联动关系**：
```
rag_summarize 工具
    ↓
RagSummarizeService.rag_summarize()
    ↓
VectorStoreService.get_retriever()
    ↓
Chroma 向量库检索
    ↓
PromptTemplate + ChatModel + StrOutputParser
    ↓
返回总结文本
```

---

### 6. 向量存储层

**文件：`rag/vector_store.py`**

| 方法 | 功能 | 关键技术 |
|------|------|----------|
| `get_retriever()` | 返回向量检索器 | Chroma.as_retriever(k=3) |
| `load_documents()` | 加载知识库到向量库 | MD5 去重 + 文本分块 |

**核心特性**：
- Chroma 向量数据库持久化存储
- RecursiveCharacterTextSplitter 文本分块（chunk_size=200, overlap=20）
- MD5 去重机制避免重复加载
- 支持 PDF 和 TXT 文件

**联动关系**：
```
load_documents()
    ↓
utils/file_handler.py (pdf_loader/txt_loader)
    ↓
RecursiveCharacterTextSplitter.split_documents()
    ↓
Chroma.add_documents()
    ↓
保存 MD5 记录到 md5.text
```

---

### 7. 模型工厂层

**文件：`model/factory.py`**

| 类 | 生成模型 | 配置来源 |
|------|----------|----------|
| `ChatModelFactory` | ChatTongyi (qwen3-max) | `config/rag.yml` |
| `EmbeddingModelFactory` | DashScopeEmbeddings (text-embedding-v4) | `config/rag.yml` |

**全局实例**：
- `chat_model`：用于 Agent 对话和 RAG 总结
- `embedding_model`：用于向量存储的文本嵌入

---

### 8. 工具类层

**目录：`utils/`**

| 文件 | 功能 | 被调用方 |
|------|------|----------|
| `config_handler.py` | 加载 YAML 配置文件 | 全局配置初始化 |
| `file_handler.py` | PDF/TXT 加载、MD5 计算 | `rag/vector_store.py` |
| `generate_external_data.py` | 兼容保留的 CSV 解析工具 | 样例数据处理 |
| `logger_handler.py` | 创建日志记录器 | 全局日志记录 |
| `path_tool.py` | 项目根目录、绝对路径转换 | 所有文件操作 |
| `prompt_loader.py` | 加载提示词文件 | `ReactAgent`、`RagSummarizeService` |

---

### 9. 配置层

**目录：`config/`**

| 文件 | 配置项 | 使用方 |
|------|--------|--------|
| `rag.yml` | 模型名称、API 密钥 | `model/factory.py` |
| `chroma.yml` | 向量库配置、分块参数 | `rag/vector_store.py` |
| `prompts.yml` | 提示词文件路径 | `utils/prompt_loader.py` |
| `agent.yml` | 外部数据路径 | `utils/generate_external_data.py` |

---

### 10. 提示词层

**目录：`prompts/`**

| 文件 | 用途 | 使用场景 |
|------|------|----------|
| `main_prompt.txt` | 主系统提示词 | 常规咨询 |
| `rag_summary_prompt.txt` | RAG 总结提示词 | 知识库检索总结 |
| `report_prompt.txt` | 报告生成提示词 | 使用报告生成 |

**动态切换机制**：
- 默认使用 `main_prompt.txt`
- 调用 `fill_context_for_report` 后切换到 `report_prompt.txt`

---

## 完整调用链路

### 场景 1：常规知识问答

```
用户输入问题
    ↓
app.py: ReactAgent.execute_stream()
    ↓
agent/react_agent.py: LangGraph Agent 执行
    ↓
[中间件] report_prompt_switch: 使用 main_prompt.txt
    ↓
Agent 思考：需要专业知识
    ↓
[中间件] monitor_tool: 记录工具调用开始
    ↓
工具调用: rag_summarize(query)
    ↓
rag/rag_service.py: RagSummarizeService.rag_summarize()
    ↓
rag/vector_store.py: VectorStoreService.get_retriever()
    ↓
Chroma 向量库检索
    ↓
[中间件] monitor_tool: 记录工具调用成功
    ↓
[中间件] log_before_model: 记录模型调用
    ↓
大模型生成最终回答
    ↓
流式输出给用户
```

### 场景 2：使用报告生成

```
用户: "给我生成我的使用报告"
    ↓
Agent 思考：需要获取用户ID和月份
    ↓
工具调用: get_user_id() → 返回 "1001"
    ↓
工具调用: get_current_month() → 返回 "2026-05"
    ↓
工具调用: fill_context_for_report()
    ↓
[中间件] monitor_tool: 检测到报告工具，设置 context["report"]=True
    ↓
[中间件] report_prompt_switch: 切换到 report_prompt.txt
    ↓
工具调用: fetch_external_data("1001", "2026-05")
    ↓
db/repositories.py: 从 SQLite 获取记录
    ↓
Agent 使用新的提示词和外部数据生成报告
    ↓
流式输出 Markdown 格式的使用报告
```

---

## 配置文件说明

### `config/rag.yml` - RAG 模型配置
```yaml
chat_model_name: qwen3-max
embedding_model_name: text-embedding-v4
api_key: ${DASHSCOPE_API_KEY}
```

`api_key` 支持环境变量占位符。不要把真实 API Key 直接提交到仓库。

### `config/chroma.yml` - 向量数据库配置
```yaml
collection_name: agent
persist_directory: chroma_db
k: 3                    # 检索返回的文档数量
data_path: data
chunk_size: 200         # 文本分块大小
chunk_overlap: 20
```

### `config/prompts.yml` - 提示词路径配置
```yaml
main_prompt_path: prompts/main_prompt.txt
rag_summary_prompt_path: prompts/rag_summary_prompt.txt
report_prompt_path: prompts/report_prompt.txt
```

### `config/agent.yml` - Agent 配置
```yaml
external_data_path: data/external/records.csv
external_provider: sqlite
default_user_id: "1001"
default_city: 上海
demo_month: "2026-05"
storage:
  provider: sqlite
  sqlite_path: data/app.db
```

---

## 使用方法

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
export DASHSCOPE_API_KEY=sk-你的API密钥
```

首次启动时，如果本地没有 `chroma_db/` 或 `md5.text`，系统会自动读取 `data/` 下的知识库文件并构建向量库。`chroma_db/` 是本地运行产物，不提交到仓库。

### 2. 启动应用

```bash
streamlit run app.py
```

访问：http://localhost:8501

### 3. 使用示例

| 类型 | 示例问题 |
|------|----------|
| 常规咨询 | 扫地机器人会漏扫吗？大户型适合什么扫地机器人？ |
| 天气相关 | 我这里天气潮湿能用扫地机器人吗？ |
| 报告生成 | 给我生成我的使用报告、查一下我的机器人使用记录 |
| 设备搜索 | 有哪些扫拖一体机器人？宠物家庭适合哪款？ |
| 设备详情 | R1-Pro这个型号怎么样？RT2-Max有什么功能？ |
| 库存查询 | R1-Pro还有库存吗？RT2-Max哪个仓库有货？ |

---

## 开发说明

### 外部服务 Provider

当前默认使用 `sqlite` Provider，用户ID、城市、演示月份和天气数据来自 `config/agent.yml` 与 SQLite 样例数据，因此演示结果是确定性的。后续接入真实用户系统、定位或天气服务时，可在 `agent/tools/providers.py` 中新增 Provider，并通过 `external_provider` 配置切换。

当前推荐配置为 `external_provider: sqlite`，应用启动时会自动创建 `data/app.db`，从 `data/external/records.csv` 导入样例使用记录，并将 Streamlit 对话写入 `conversation_history` 表。`data/app.db` 是本地运行产物，不提交到仓库。

### 添加新工具

1. 在 `agent/tools/agent_tools.py` 中使用 `@tool` 装饰器定义工具
2. 在 `agent/react_agent.py` 的 `tools` 列表中注册
3. 在 `prompts/main_prompt.txt` 中添加工具使用说明

### 添加新知识库文件

1. 将文件放入 `data/` 目录
2. 确保 `config/chroma.yml` 的 `allow_knowledge_file_types` 包含文件扩展名
3. 重启应用，系统会在检测到本地向量库缺失时自动加载

### 日志查看

日志文件：`logs/agent_YYYYMMDD.log`

---

## 项目亮点

1. **完整的 ReAct 架构**：展示现代 Agent 设计模式
2. **中间件模式**：清晰的关注点分离
3. **RAG 集成**：向量检索与生成式回答结合
4. **动态提示词**：根据场景自动切换
5. **模块化设计**：易于扩展和维护
