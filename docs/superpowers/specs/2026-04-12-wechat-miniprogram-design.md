# 小桥微信小程序改造设计文档

**日期**：2026-04-12  
**状态**：已确认，待实现  
**环境**：CloudBase `wenwen2code-4gxuthj048ae0fb0`

---

## 一、项目背景

将现有 Python/Streamlit Web 应用"小桥"改造为微信小程序。原应用具备能力评估、计划生成、问答咨询三大功能，已有 CloudBase 云开发环境和 tcb CLI 登录凭据。

**核心决策**：
- 原生 WXML（非 Taro/uni-app），最轻量、与微信生态最契合
- CloudBase Node.js 18 云函数，无需额外服务器运维
- 删除 LangChain + ChromaDB，改用原生 fetch + 知识库全文注入
- 知识库（5.5KB）直接嵌入 system prompt，无需向量检索

---

## 二、技术栈

| 层级 | 技术选型 | 说明 |
|------|------|------|
| 前端 | 原生 WXML + WXSS | 无框架依赖，主包体积可控在 1MB 以内 |
| UI 组件库 | Vant Weapp v4.x | Form/Field/Popup/Toast/Picker 等 |
| 图表 | Apache ECharts for 微信 | 评估结果雷达图 |
| 云函数 | Node.js 18（CloudBase） | 4个云函数，见下节 |
| 数据库 | CloudBase NoSQL | 3个集合 |
| LLM | SiliconFlow `Pro/deepseek-ai/DeepSeek-V3.2` | OpenAI 兼容接口 |
| 部署 | tcb CLI（已配置） | `wenwen2code` 环境 |

---

## 三、整体架构

```
小程序前端（WXML + Vant Weapp）
        ↓ wx.cloud.callFunction()
CloudBase 云函数（Node.js 18）
  ├── assessment     纯 JS 评分（无 API 调用）
  ├── generatePlan   DeepSeek 生成4周计划
  ├── chat           DeepSeek + 知识库全文上下文
  └── analyzeDeep    多次历史评估对比分析（进阶）
        ↓
SiliconFlow API（Pro/deepseek-ai/DeepSeek-V3.2）
        ↓
CloudBase 数据库（NoSQL）
  ├── children       孩子档案
  ├── assessments    评估记录（含历史）
  └── plans          生成的计划
```

---

## 四、数据模型

### 4.1 children 集合

```javascript
{
  _id: string,           // 自动生成
  openid: string,        // 微信用户 openid
  name: string,          // 孩子姓名
  age: number,           // 年龄（如 5.5）
  hometown: string,      // 籍贯，如"浙江省杭州市"（Vant 省市 Picker）
  createdAt: timestamp
}
```

### 4.2 assessments 集合

```javascript
{
  _id: string,
  childId: string,       // ref -> children
  scores: {
    language: {
      listening: number,         // 1-5
      expression: number,
      reading: number,
      writing_interest: number
    },
    math: {
      counting: number,
      operation: number,
      shapes: number,
      space: number
    },
    social: number,
    self_care: number,
    motor: number,
    focus: number,
    emotion: number,
    time_awareness: number
  },
  result: {
    overall_level: string,       // "优秀" | "良好" | "需加强关注"
    strengths: string[],
    areas_to_improve: string[],
    recommendations: string[]
  },
  createdAt: timestamp
}
```

### 4.3 plans 集合

```javascript
{
  _id: string,
  childId: string,
  assessmentId: string,
  duration: string,              // 如"3个月"
  weekly_goals: string[],        // 每周目标（4条）
  daily_activities: [{
    time: string,                // "早晨"|"下午"|"傍晚"|"睡前"
    activity: string,
    goal: string
  }],
  resources: string[],
  parent_tips: string[],
  evaluation_criteria: string[],
  currentWeek: number,           // 时间轴当前进度，默认 1
  createdAt: timestamp
}
```

---

## 五、云函数设计

### 5.1 assessment（纯 JS，无 API 调用）

移植自 `assessment.py`，逻辑完全一致：8 个维度评分，计算优势/弱项/建议。响应时间 < 100ms。

**入参**：`scores` 对象（同数据库结构）  
**出参**：`{ overall_level, strengths, areas_to_improve, recommendations }`

### 5.2 generatePlan

**入参**：`{ childProfile, assessmentResult }`  
**出参**：`TransitionPlan` JSON  
**实现**：
- system prompt 注入全量 `knowledge_base.md`（5.5KB）
- 若 `childProfile.hometown` 存在，追加："请结合 ${hometown} 当地幼小衔接政策和小学入学要求，给出针对性建议"
- 调用 SiliconFlow API，请求结构化 JSON 输出
- 超时设置 60s，失败时返回本地默认计划（`fallback_qa.json` 兜底）

### 5.3 chat

**入参**：`{ message, history[] }`  
**出参**：`{ reply: string }`  
**实现**：
- system prompt = "小桥"角色设定 + 全量知识库
- 支持多轮对话历史传入
- 无网络/API 失败时降级到本地 `fallback_qa.json` 关键词匹配
- 可选：SSE 流式响应（微信基础库 2.10.4+）

### 5.4 analyzeDeep（进阶，完成 2 次以上评估后解锁）

**入参**：`{ childId, assessments[] }`（多次历史评估数据）  
**出参**：`{ growth_curve, weak_spots_plan, estimated_readiness, local_policy_tips }`  
**实现**：
- 对比多次评估，识别成长轨迹
- 对得分 ≤ 2 的维度生成专项每日练习
- 估算达到"入学准备"水平所需时间
- 结合籍贯动态生成当地政策适配建议

---

## 六、页面设计

### 6.1 页面路由

| 页面 | 路由 | TabBar |
|------|------|------|
| 首页 | `/pages/home/home` | 首页 |
| 评估 | `/pages/assessment/assessment` | 评估 |
| 计划 | `/pages/plan/plan` | 计划 |
| 问答 | `/pages/chat/chat` | 问答 |

### 6.2 视觉规范

| 项目 | 值 |
|------|------|
| 主色 | `#52C41A`（青草绿） |
| 浅背景 | `#F6FFED` |
| 辅助绿 | `#D9F7BE` |
| 深绿 | `#389E0D` |
| 字色 | `#333333` |
| 辅助字色 | `#888888` |
| 圆角 | 卡片 16rpx，按钮 40rpx |
| 评分方式 | 星级（1-5 颗 ⭐） |
| 单位 | rpx（全机型适配） |

### 6.3 首页

- 绿色渐变 Hero 区：🌱 图标 + "小桥" + 副标题
- 3个功能入口卡片（评估 / 计划 / 问答）
- 底部 TabBar

### 6.4 评估页（图卡总览模式）

**交互流程**：
1. 顶部展示孩子姓名 + 进度（已完成 X / 8）
2. 8 张维度卡片（2列网格）：灰色=待评，绿色+✅=已评
3. 点击卡片 → Vant Popup 底部弹窗：
   - 维度说明文字（1-2句）
   - 5颗星评分
   - 确认按钮
4. 8 张全部完成 → "查看评估结果"按钮高亮
5. 跳转结果页：雷达图（ECharts）+ 优势标签 + 弱项建议
6. 结果页底部 → "生成个性化计划"按钮

**8 个维度卡片**：
| 图标 | 名称 | 评分维度 |
|------|------|------|
| 👂 | 倾听理解 | language.listening |
| 🗣️ | 语言表达 | language.expression |
| 📖 | 阅读习惯 | language.reading |
| ✏️ | 书写兴趣 | language.writing_interest |
| 🔢 | 数学能力 | math（4项均值） |
| 🤝 | 社交能力 | social |
| 🧹 | 自理能力 | self_care |
| 🎯 | 专注力 | focus |

> 注：motor / emotion / time_awareness 合并入专注力卡片弹窗的子项，保持卡片数量简洁。

### 6.5 计划页（成长时间轴）

- 顶部 Tab：计划 | 资源 | 家长贴士
- 时间轴按周排列（4周）：已过周实色，当前周高亮，未来周淡显
- 点击某周 → 展开：本周目标 + 每日活动（早/午/晚/睡前 4 条）
- 右上角分享按钮 → 生成计划图片（wx.canvasToTempFilePath）
- 生成中显示 loading + 进度提示文案

### 6.6 问答页（气泡对话）

- 顶部 FAQ 快捷标签（3-4 个常见问题）
- 聊天气泡界面（用户蓝，AI 白+绿头像）
- 输入框 + 发送；AI 回复时显示"小桥正在思考…"动效
- 无 API 时降级：关键词匹配 `fallback_qa.json`

---

## 七、AI 能力分层

| 层级 | 触发 | 实现 | 响应时间 | 成本 |
|------|------|------|------|------|
| 基础 | 评分完成即时 | 纯 JS 规则（assessment 云函数） | <100ms | 零 |
| 标准 | 点击"生成计划" | DeepSeek 单次调用 | 5-8秒 | 极低 |
| 进阶 | ≥2 次历史评估后解锁 | DeepSeek 多轮，携带历史数据 + 籍贯 | 8-15秒 | 低 |

**籍贯适配实现**：
- 孩子档案录入时通过 Vant 省市 Picker 选择
- 籍贯信息注入 generatePlan / analyzeDeep 的 system prompt
- DeepSeek V3.2 训练数据涵盖各省教育政策，动态生成本地建议
- 知识库保持全国通用（教育部指南），不维护各省政策数据库

---

## 八、文件结构（改造后）

```
kindergarten_to_school/
├── miniprogram/                  # 小程序前端
│   ├── app.js / app.json / app.wxss
│   ├── pages/
│   │   ├── home/
│   │   ├── assessment/
│   │   ├── plan/
│   │   └── chat/
│   └── components/               # 自定义组件（如雷达图封装）
├── cloudfunctions/               # 云函数
│   ├── assessment/
│   │   └── index.js              # 移植自 assessment.py
│   ├── generatePlan/
│   │   ├── index.js
│   │   └── knowledge_base.js     # 嵌入知识库文本
│   ├── chat/
│   │   └── index.js
│   └── analyzeDeep/
│       └── index.js
├── knowledge_base.md             # 保留原文件（嵌入云函数时引用）
├── fallback_qa.json              # 保留（降级使用）
├── project.config.json           # 小程序配置（AppID 等）
└── docs/
    └── superpowers/specs/
        └── 2026-04-12-wechat-miniprogram-design.md

# 废弃文件（可删除）
# app.py / phone_components.py / kindergarten_agent_full.py
# assessment.py / requirements.txt
```

---

## 九、废弃文件清单

| 文件 | 原用途 | 处置 |
|------|------|------|
| `app.py` | Streamlit UI 主入口 | 废弃 |
| `phone_components.py` | 仿写小程序 HTML 原型 | 废弃 |
| `kindergarten_agent_full.py` | LangChain Agent | 废弃 |
| `assessment.py` | Python 评分逻辑 | 移植为 JS 后废弃 |
| `requirements.txt` | Python 依赖 | 废弃 |

---

## 十、待确认事项（实现前需明确）

1. **AppID**：是否已有微信小程序 AppID？`wenwen2code` 环境绑定的是哪个 AppID？
2. **SiliconFlow API Key**：已在 `.env` 中配置，云函数部署时需在 CloudBase 环境变量中同步设置。
3. **主包体积**：ECharts 较大，考虑按需引入或改用轻量替代（wx-charts）。
4. **分享功能**：计划海报生成是否为 MVP 必需，或可列为 v2 功能？
