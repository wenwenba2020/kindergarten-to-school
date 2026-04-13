# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供代码库工作指导。

## 项目概述

"小桥" - 面向浙江省 5-6 岁儿童的幼小衔接规划助手。基于 Streamlit 和 LangChain 构建，依据《3-6 岁儿童学习与发展指南》提供能力评估、个性化计划生成和问答咨询服务。

## 常用命令

```bash
# 启动 Web 应用
streamlit run app.py

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env  # 然后编辑 .env 填入 API Key

# 直接运行 Agent（测试用）
python kindergarten_agent_full.py
```

## 架构说明

**核心文件：**
- `app.py` - Streamlit Web 界面，包含首页、能力评估、生成计划、问答咨询四个模块
- `assessment.py` - 评估核心逻辑，计算语言、数学、社交、自理、运动五个维度的得分
- `kindergarten_agent_full.py` - 主 Agent，含 RAG 知识库检索（ChromaDB 向量库）
- `kindergarten_agent.py` - 简化版 Agent，使用 OpenAI Function Calling
- `knowledge_base.md` - 领域知识库，用于 RAG 检索

**数据流程：**
1. 用户在 `app.py` 填写评估表单 → 分数存入 `st.session_state.profile`
2. `assessment.py` 的 `calculate_assessment()` 计算优势与待提升项
3. `KindergartenAgent.generate_plan()` 调用 LLM 生成个性化计划
4. 问答功能：问题 → `KnowledgeBase.retrieve()` 检索 → 带 context 调用 LLM

**LLM 配置：**
- 主用 OpenAI（`OPENAI_API_KEY`，可选 `OPENAI_BASE_URL` 自定义网关）
- 备用 Anthropic（需设置 `ANTHROPIC_MODEL` + `ANTHROPIC_API_KEY` 或 `ANTHROPIC_AUTH_TOKEN`）
- 向量检索：可选 ChromaDB（由 `OPENAI_USE_EMBEDDINGS` 控制）

**核心类：**
- `ChildProfile` / `LanguageAbility` / `MathAbility` - Pydantic 数据模型
- `KnowledgeBase` - 管理向量库（ChromaDB）或降级为纯文本搜索
- `KindergartenAgent` - 主 Agent，方法：`assess_child()`、`generate_plan()`、`chat()`

## 注意事项

- 无 LLM Key 时应用仍可运行：显示示例计划并使用本地问答降级方案
- 评估分数为 1-5 分制（8个维度，总分8-40分）；整体水平判定：优秀（≥32分）、良好（24-31分）、需加强关注（<24分）
- 知识库基于教育部《3-6 岁儿童学习与发展指南》及浙江省学前教育政策
