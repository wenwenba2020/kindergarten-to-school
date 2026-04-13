# 个性化问答与 Fallback 计划设计方案

**日期：** 2026-04-13  
**项目：** 小桥 微信小程序  
**分支：** 基于 feat/wechat-miniprogram（UI 改版 PR 合并后新开分支）

---

## 背景

当前两个功能缺陷：

1. **问答无个性化**：`chat` 云函数只有通用知识库，不知道当前孩子的评估结果和计划，无法给出针对性建议
2. **Fallback 计划无个性化**：LLM 不可用时返回完全写死的通用计划，与评估结果无关

目标：问答基于孩子的具体评估结果和计划进行，不做开放式通用问答；fallback 计划根据待提升维度匹配预置模板。

---

## 一、问答页前端（chat.js + chat.wxml）

### 1.1 评估 Gate

`onLoad` 时读取本地存储，判断是否有评估数据：

```js
const result = wx.getStorageSync('lastAssessmentResult')
const plan = wx.getStorageSync('lastPlan')
const child = getApp().globalData.currentChild
this.setData({ hasAssessment: !!result, childContext: result ? { ...child, ...result, weekly_goals: plan?.weekly_goals || [] } : null })
```

- `hasAssessment = false`：页面显示引导卡（"请先完成能力评估，再开始个性化问答"+ 跳转按钮），输入框和发送按钮禁用
- `hasAssessment = true`：正常显示问答界面

### 1.2 动态 FAQ 生成

根据 `assessmentResult.areas_to_improve` 在前端生成 FAQ 列表（不调用 LLM）：

**维度 → 快捷问题映射表：**

| 维度 | 快捷问题 |
|------|---------|
| 语言能力 | 怎么提升孩子的语言表达能力？ |
| 数学认知 | 有什么方法提高孩子的数学能力？ |
| 社交能力 | 孩子社交能力弱怎么帮助？ |
| 自理能力 | 如何培养孩子的自理习惯？ |
| 专注力 | 怎么训练孩子的专注力？ |
| 阅读习惯 | 如何帮孩子养成阅读习惯？ |
| 运动协调 | 有什么运动游戏提升孩子协调性？ |
| 情绪管理 | 孩子情绪不稳定怎么引导？ |

- 取 `areas_to_improve` 前4个维度匹配，展示对应快捷问题
- 若 `areas_to_improve` 为空（全优秀），展示2条通用问题：
  - "计划里的活动怎么执行？"
  - "入学前还要注意什么？"

FAQ 在 `onLoad` 时计算，存入 `data.faqs`，替换现有硬编码 FAQS 常量。

### 1.3 发送时传 childContext

`sendMessage()` 额外传 `childContext`：

```js
const childContext = this.data.childContext  // 已在 onLoad 准备好
wx.cloud.callFunction({
  name: 'chat',
  data: { message, history, childContext }
})
```

`childContext` 结构（精简，控制 token）：

```js
{
  name: string,           // 孩子姓名
  age: number,            // 年龄
  hometown: string,       // 籍贯
  overall_level: string,  // 整体水平（优秀/良好/需加强关注）
  strengths: string[],    // 优势维度
  areas_to_improve: string[],  // 待提升维度
  weekly_goals: string[]  // 计划的周目标列表
}
```

### 1.4 WXML 改动

在现有输入区上方新增条件渲染：

```xml
<!-- 未评估引导卡 -->
<view wx:if="{{!hasAssessment}}" class="gate-card">
  <text class="gate-title">请先完成能力评估</text>
  <text class="gate-desc">完成评估后，问答将根据孩子的具体情况给出个性化建议</text>
  <view class="gate-btn" bindtap="goAssessment">去评估</view>
</view>

<!-- 正常问答界面（已有评估时显示） -->
<view wx:else>
  <!-- 现有 FAQ chips + 消息列表 + 输入区 -->
</view>
```

---

## 二、chat 云函数（cloudfunctions/chat/index.js）

### 2.1 接口变更

```js
const { message, history = [], childContext = null } = event
```

### 2.2 个性化 System Prompt 构建

```js
function buildSystemPrompt(childContext) {
  let personalBlock = ''
  if (childContext) {
    const { name, age, hometown, overall_level, strengths, areas_to_improve, weekly_goals } = childContext
    personalBlock = `你正在为一个具体的孩子提供个性化指导：

【孩子信息】
姓名：${name || '孩子'}（${age || 5.5}岁${hometown ? `，${hometown}` : ''}）
整体水平：${overall_level}
优势：${(strengths || []).join('、') || '暂无'}
需重点提升：${(areas_to_improve || []).join('、') || '暂无'}
${weekly_goals?.length ? `\n【当前计划目标】\n${weekly_goals.map((g, i) => `第${i+1}周：${g}`).join('\n')}` : ''}

回答时请结合以上孩子的具体情况，给出有针对性的建议。
若家长问到计划中的具体活动，请结合计划目标解释如何执行。\n\n`
  }

  return `${personalBlock}你是"小桥"——幼小衔接规划专家，专为5-6岁儿童家庭服务。
回答原则：温暖、专业、实用，给出具体可操作的建议，控制在200字以内。

知识库参考：
${KNOWLEDGE_BASE}`
}
```

- 有 `childContext`：个性化块 + 通用知识库
- 无 `childContext`（防御性降级）：纯通用 system prompt（现有行为）

### 2.3 其余逻辑不变

LLM 调用、fallback、错误处理、history 截断——全部保持原样。

---

## 三、Fallback 计划个性化（cloudfunctions/generatePlan/fallback-plan.js）

### 3.1 接口变更

```js
// 改前
function getDefaultPlan(duration)

// 改后
function getDefaultPlan(duration, areas_to_improve = [])
```

调用处（`index.js` 第82行）：
```js
return { code: 0, data: getDefaultPlan(duration, event.assessmentResult?.areas_to_improve), fallback: true }
```

### 3.2 维度模板

```js
const DIMENSION_GOALS = {
  '数学认知': ['巩固20以内加减法运算能力', '通过游戏方式感知数量关系'],
  '语言能力': ['每天亲子阅读20分钟，培养阅读习惯', '练习完整表达一件事情'],
  '专注力':   ['每天15分钟专注训练（拼图/棋类游戏）', '减少电子产品干扰，营造安静学习环境'],
  '社交能力': ['每周参加一次同伴活动，练习合作', '学习轮流发言和分享'],
  '自理能力': ['练习独立整理书包和文具', '掌握系鞋带、穿脱衣服'],
  '阅读习惯': ['建立每日固定阅读时间（睡前20分钟）', '读完后复述故事主要情节'],
  '运动协调': ['每天20分钟户外运动', '练习跳绳、投接球等协调性游戏'],
  '情绪管理': ['学习认识并命名自己的情绪', '练习深呼吸和"暂停一下"的平静方法'],
}
```

### 3.3 生成逻辑

```js
function getDefaultPlan(duration, areas_to_improve = []) {
  // 取前4个待提升维度的目标（每个维度取第一条）作为 weekly_goals
  const priorityGoals = areas_to_improve
    .slice(0, 4)
    .map(dim => DIMENSION_GOALS[dim]?.[0])
    .filter(Boolean)

  // 不足4条时用通用目标补齐
  const fallbackGoals = ['培养良好作息习惯', '每天亲子阅读20分钟', '练习独立整理书包', '适应小学课堂节奏']
  const weekly_goals = [...priorityGoals, ...fallbackGoals].slice(0, 4)

  return {
    duration,
    _isFallback: true,  // 标记为 fallback，前端可据此显示提示
    weekly_goals,
    daily_activities: [ /* 现有通用内容保持不变 */ ],
    resources: [ /* 现有通用内容保持不变 */ ],
    parent_tips: [ /* 现有通用内容保持不变 */ ],
  }
}
```

---

## 四、改动文件清单

| 文件 | 改动 |
|------|------|
| `miniprogram/pages/chat/chat.js` | 加 gate 判断、读 childContext、动态 FAQ、sendMessage 传 childContext |
| `miniprogram/pages/chat/chat.wxml` | 加未评估引导卡（条件渲染） |
| `miniprogram/pages/chat/chat.wxss` | 新增 gate-card 样式 |
| `cloudfunctions/chat/index.js` | 接收 childContext，`buildSystemPrompt()` 构建个性化 prompt |
| `cloudfunctions/generatePlan/fallback-plan.js` | `getDefaultPlan` 接受 areas_to_improve，按维度匹配 weekly_goals |
| `cloudfunctions/generatePlan/index.js` | 调用 getDefaultPlan 时传入 assessmentResult?.areas_to_improve |

---

## 五、不改动的内容

- 评估页、结果页、计划页、首页逻辑
- LLM 调用方式、API Key 配置
- chat 云函数的 history 截断、fallback 错误处理
- generatePlan 的主流程（LLM 可用时不受影响）

---

## 六、成功标准

- [ ] 未做评估进入问答页 → 显示引导卡，输入框禁用
- [ ] 完成评估后进入问答页 → FAQ 显示孩子待提升维度对应的快捷问题
- [ ] 发送消息时 childContext 正确传给云函数
- [ ] 云函数 system prompt 包含孩子姓名、水平、优势、待提升、周目标
- [ ] LLM 不可用时 fallback 计划的 weekly_goals 反映 areas_to_improve
- [ ] 微信开发者工具模拟器无报错
