# 个性化问答与 Fallback 计划实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 问答基于孩子的具体评估结果和计划进行个性化回答；未评估时显示引导卡禁止问答；fallback 计划根据待提升维度匹配预置模板。

**Architecture:** 前端 chat.js 在 onLoad 时聚合本地存储的评估结果、计划、孩子信息，发送时作为 childContext 传给 chat 云函数；云函数将 childContext 注入 system prompt 头部；fallback-plan.js 按 areas_to_improve 维度匹配预置周目标模板。

**Tech Stack:** 微信小程序 WXML/WXSS/JS、微信云函数（Node.js）、SiliconFlow DeepSeek-V3 API

---

## 文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `cloudfunctions/generatePlan/fallback-plan.js` | 修改 | getDefaultPlan 接受 areas_to_improve，按维度匹配 weekly_goals |
| `cloudfunctions/generatePlan/index.js` | 修改 | 调用 getDefaultPlan 时传入 assessmentResult?.areas_to_improve |
| `cloudfunctions/chat/index.js` | 修改 | 接收 childContext，buildSystemPrompt 注入个性化块 |
| `miniprogram/pages/chat/chat.js` | 修改 | onLoad 读上下文、动态 FAQ、sendMessage 传 childContext、gate 判断 |
| `miniprogram/pages/chat/chat.wxml` | 修改 | 加未评估引导卡（条件渲染包裹现有内容） |
| `miniprogram/pages/chat/chat.wxss` | 修改 | 新增 gate-card 相关样式 |

---

## Task 1：Fallback 计划个性化

**Files:**
- Modify: `cloudfunctions/generatePlan/fallback-plan.js`
- Modify: `cloudfunctions/generatePlan/index.js`

- [ ] **Step 1: 替换 fallback-plan.js 为完整新版**

将 `cloudfunctions/generatePlan/fallback-plan.js` 完整替换为：

```js
'use strict'

const DIMENSION_GOALS = {
  '数学认知': '巩固20以内加减法运算能力，通过游戏方式感知数量关系',
  '语言能力': '每天亲子阅读20分钟，练习完整表达一件事情',
  '专注力':   '每天15分钟专注训练（拼图/棋类游戏），减少电子产品干扰',
  '社交能力': '每周参加一次同伴活动练习合作，学习轮流发言和分享',
  '自理能力': '练习独立整理书包和文具，掌握系鞋带、穿脱衣服',
  '阅读习惯': '建立每日固定阅读时间（睡前20分钟），读完后复述故事主要情节',
  '运动协调': '每天20分钟户外运动，练习跳绳、投接球等协调性游戏',
  '情绪管理': '学习认识并命名自己的情绪，练习深呼吸和暂停平静法',
}

const FALLBACK_GOALS = [
  '培养时间观念，养成固定作息习惯',
  '每天亲子阅读15分钟，培养阅读兴趣',
  '练习独立整理书包和文具',
  '适应小学课堂节奏，培养专注力',
]

function getDefaultPlan(duration = '3个月', areas_to_improve = []) {
  const priorityGoals = areas_to_improve
    .slice(0, 4)
    .map(dim => DIMENSION_GOALS[dim])
    .filter(Boolean)

  const weekly_goals = [...priorityGoals, ...FALLBACK_GOALS].slice(0, 4)

  return {
    duration,
    _isFallback: true,
    weekly_goals,
    daily_activities: [
      { time: '早晨', activity: '亲子阅读15分钟', goal: '语言发展' },
      { time: '下午', activity: '益智游戏/积木', goal: '数学思维' },
      { time: '傍晚', activity: '户外运动30分钟', goal: '体能发展' },
      { time: '睡前', activity: '整理自己的书包/玩具', goal: '自理能力' },
    ],
    resources: [
      '《我的第一本数学思维书》',
      '幼小衔接APP：洪恩识字、斑马思维',
      '动画片：《蓝色小考拉》、《小鼠波波》',
    ],
    parent_tips: [
      '每天坚持，形成习惯',
      '多鼓励、少批评',
      '保持耐心，循序渐进',
    ],
    evaluation_criteria: [
      '能独立完成基本自理行为',
      '能完整表达自己的想法',
      '能与其他小朋友合作游戏',
      '对学习有积极兴趣',
    ],
  }
}

module.exports = { getDefaultPlan }
```

- [ ] **Step 2: 修改 generatePlan/index.js 第82行传入 areas_to_improve**

找到 `cloudfunctions/generatePlan/index.js` 中的这一行：
```js
return { code: 0, data: getDefaultPlan(duration), fallback: true }
```
替换为：
```js
return { code: 0, data: getDefaultPlan(duration, assessmentResult?.areas_to_improve), fallback: true }
```

- [ ] **Step 3: 验证 getDefaultPlan 逻辑**

在项目根目录运行快速验证：

```bash
cd /Users/robertzf/cc_workspace/kindergarten_to_school
node -e "
const { getDefaultPlan } = require('./cloudfunctions/generatePlan/fallback-plan')
const plan1 = getDefaultPlan('3个月', ['数学认知', '专注力'])
console.log('with areas:', plan1.weekly_goals)
console.log('isFallback:', plan1._isFallback)

const plan2 = getDefaultPlan('3个月', [])
console.log('no areas:', plan2.weekly_goals)
"
```

预期输出：
```
with areas: [
  '巩固20以内加减法运算能力，通过游戏方式感知数量关系',
  '每天15分钟专注训练（拼图/棋类游戏），减少电子产品干扰',
  '培养时间观念，养成固定作息习惯',
  '每天亲子阅读15分钟，培养阅读兴趣'
]
isFallback: true
no areas: [
  '培养时间观念，养成固定作息习惯',
  '每天亲子阅读15分钟，培养阅读兴趣',
  '练习独立整理书包和文具',
  '适应小学课堂节奏，培养专注力'
]
```

- [ ] **Step 4: Commit**

```bash
git add cloudfunctions/generatePlan/fallback-plan.js cloudfunctions/generatePlan/index.js
git commit -m "feat: personalize fallback plan by areas_to_improve dimension matching"
```

---

## Task 2：Chat 云函数个性化 System Prompt

**Files:**
- Modify: `cloudfunctions/chat/index.js`

- [ ] **Step 1: 在 index.js 中新增 buildSystemPrompt 函数并更新 main**

将 `cloudfunctions/chat/index.js` 中现有的 `SYSTEM_PROMPT` 常量（第175-179行）和 `exports.main` 中对 `SYSTEM_PROMPT` 的使用，替换为以下内容。

**删除**这几行（约175-179行）：
```js
const SYSTEM_PROMPT = `你是"小桥"——幼小衔接规划专家，专为5-6岁儿童家庭服务。
回答原则：温暖、专业、实用，给出具体可操作的建议，控制在200字以内。

知识库参考：
${KNOWLEDGE_BASE}`
```

**替换为**（插在 `exports.main` 之前）：
```js
function buildSystemPrompt(childContext) {
  let personalBlock = ''
  if (childContext) {
    const { name, age, hometown, overall_level, strengths = [], areas_to_improve = [], weekly_goals = [] } = childContext
    const goalsText = weekly_goals.length
      ? '\n\n【当前计划目标】\n' + weekly_goals.map((g, i) => `第${i + 1}周：${g}`).join('\n')
      : ''
    personalBlock = `你正在为一个具体的孩子提供个性化指导：

【孩子信息】
姓名：${name || '孩子'}（${age || 5.5}岁${hometown ? `，${hometown}` : ''}）
整体水平：${overall_level || '未知'}
优势：${strengths.join('、') || '暂无'}
需重点提升：${areas_to_improve.join('、') || '暂无'}${goalsText}

回答时请结合以上孩子的具体情况，给出有针对性的建议。若家长问到计划中的具体活动，请结合计划目标解释如何执行。\n\n`
  }
  return `${personalBlock}你是"小桥"——幼小衔接规划专家，专为5-6岁儿童家庭服务。
回答原则：温暖、专业、实用，给出具体可操作的建议，控制在200字以内。

知识库参考：
${KNOWLEDGE_BASE}`
}
```

**同时修改** `exports.main` 函数：

将：
```js
const { message, history = [] } = event
```
改为：
```js
const { message, history = [], childContext = null } = event
```

将：
```js
const messages = [
  { role: 'system', content: SYSTEM_PROMPT },
```
改为：
```js
const messages = [
  { role: 'system', content: buildSystemPrompt(childContext) },
```

- [ ] **Step 2: 验证函数逻辑**

```bash
node -e "
// 临时测试 buildSystemPrompt 逻辑（不含 KNOWLEDGE_BASE）
function buildSystemPrompt(childContext) {
  let personalBlock = ''
  if (childContext) {
    const { name, age, hometown, overall_level, strengths = [], areas_to_improve = [], weekly_goals = [] } = childContext
    const goalsText = weekly_goals.length
      ? '\n\n【当前计划目标】\n' + weekly_goals.map((g, i) => '第' + (i+1) + '周：' + g).join('\n')
      : ''
    personalBlock = '孩子：' + (name||'孩子') + '，' + overall_level + '，待提升：' + areas_to_improve.join('、') + goalsText + '\n\n'
  }
  return personalBlock + '[通用知识库]'
}

const ctx = { name: '小明', age: 5.5, hometown: '杭州', overall_level: '良好', strengths: ['语言'], areas_to_improve: ['数学认知'], weekly_goals: ['巩固加减法'] }
console.log('with context:', buildSystemPrompt(ctx).slice(0, 100))
console.log('no context:', buildSystemPrompt(null).slice(0, 50))
"
```

预期输出：
```
with context: 孩子：小明，良好，待提升：数学认知

【当前计划目标】
第1周：巩固加减法

[通用知识库]
no context: [通用知识库]
```

- [ ] **Step 3: Commit**

```bash
git add cloudfunctions/chat/index.js
git commit -m "feat: inject childContext into chat system prompt for personalized Q&A"
```

---

## Task 3：Chat 前端 JS（gate + 上下文 + 动态 FAQ）

**Files:**
- Modify: `miniprogram/pages/chat/chat.js`

- [ ] **Step 1: 完整替换 chat.js**

将 `miniprogram/pages/chat/chat.js` 完整替换为：

```js
const DIMENSION_FAQS = {
  '数学认知': '有什么方法提高孩子的数学能力？',
  '语言能力': '怎么提升孩子的语言表达能力？',
  '专注力':   '怎么训练孩子的专注力？',
  '社交能力': '孩子社交能力弱怎么帮助？',
  '自理能力': '如何培养孩子的自理习惯？',
  '阅读习惯': '如何帮孩子养成阅读习惯？',
  '运动协调': '有什么运动游戏提升孩子协调性？',
  '情绪管理': '孩子情绪不稳定怎么引导？',
}

const DEFAULT_FAQS = ['计划里的活动怎么执行？', '入学前还要注意什么？']

function buildFaqs(areas_to_improve = []) {
  const faqs = areas_to_improve
    .slice(0, 4)
    .map(dim => DIMENSION_FAQS[dim])
    .filter(Boolean)
  return faqs.length ? faqs : DEFAULT_FAQS
}

function buildChildContext(result, plan, child) {
  if (!result) return null
  return {
    name: child?.name || '',
    age: child?.age || 5.5,
    hometown: child?.hometown || '',
    overall_level: result.overall_level || '',
    strengths: result.strengths || [],
    areas_to_improve: result.areas_to_improve || [],
    weekly_goals: plan?.weekly_goals || [],
  }
}

Page({
  data: {
    hasAssessment: false,
    faqs: DEFAULT_FAQS,
    messages: [],
    inputMsg: '',
    thinking: false,
    scrollToId: '',
    msgCounter: 0,
    childContext: null,
  },

  onLoad() {
    const result = wx.getStorageSync('lastAssessmentResult')
    const plan = wx.getStorageSync('lastPlan')
    const child = getApp().globalData.currentChild || {}
    const childContext = buildChildContext(result, plan, child)
    const faqs = result ? buildFaqs(result.areas_to_improve) : DEFAULT_FAQS
    this.setData({ hasAssessment: !!result, childContext, faqs })
  },

  onShow() {
    // 每次显示时重新读取，以防评估在其他页面完成
    const result = wx.getStorageSync('lastAssessmentResult')
    const plan = wx.getStorageSync('lastPlan')
    const child = getApp().globalData.currentChild || {}
    const childContext = buildChildContext(result, plan, child)
    const faqs = result ? buildFaqs(result.areas_to_improve) : DEFAULT_FAQS
    this.setData({ hasAssessment: !!result, childContext, faqs })
  },

  goAssessment() {
    wx.switchTab({ url: '/pages/assessment/assessment' })
  },

  onInput(e) { this.setData({ inputMsg: e.detail }) },

  sendFaq(e) {
    const msg = e.currentTarget.dataset.msg
    this.setData({ inputMsg: msg }, () => this.sendMessage())
  },

  async sendMessage() {
    const text = this.data.inputMsg.trim()
    if (!text) return
    const userMsg = { id: this.data.msgCounter, role: 'user', content: text }
    const newCounter = this.data.msgCounter + 1
    const history = this.data.messages.slice(-6).map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content,
    }))
    this.setData({
      messages: [...this.data.messages, userMsg],
      inputMsg: '',
      thinking: true,
      msgCounter: newCounter,
      scrollToId: `msg-${userMsg.id}`,
    })
    try {
      const res = await wx.cloud.callFunction({
        name: 'chat',
        data: { message: text, history, childContext: this.data.childContext },
      })
      const reply = res.result.data?.reply || '暂时无法回答，请稍后再试。'
      const aiMsg = { id: newCounter, role: 'ai', content: reply }
      this.setData({
        messages: [...this.data.messages, aiMsg],
        msgCounter: newCounter + 1,
        scrollToId: `msg-${aiMsg.id}`,
      })
    } catch (err) {
      const aiMsg = { id: newCounter, role: 'ai', content: '网络异常，请检查连接后重试。' }
      this.setData({ messages: [...this.data.messages, aiMsg] })
    } finally {
      this.setData({ thinking: false })
    }
  },
})
```

- [ ] **Step 2: Commit**

```bash
git add miniprogram/pages/chat/chat.js
git commit -m "feat: add assessment gate, dynamic FAQ, and childContext to chat page"
```

---

## Task 4：Chat WXML + WXSS（引导卡）

**Files:**
- Modify: `miniprogram/pages/chat/chat.wxml`
- Modify: `miniprogram/pages/chat/chat.wxss`

- [ ] **Step 1: 替换 chat.wxml**

将 `miniprogram/pages/chat/chat.wxml` 完整替换为：

```xml
<view class="container">
  <!-- 未评估引导卡 -->
  <view wx:if="{{!hasAssessment}}" class="gate-card">
    <view class="gate-icon">📋</view>
    <view class="gate-title">请先完成能力评估</view>
    <view class="gate-desc">完成评估后，问答将根据孩子的具体情况给出个性化建议</view>
    <view class="gate-btn" bindtap="goAssessment">去评估 →</view>
  </view>

  <!-- 正常问答界面 -->
  <block wx:else>
    <scroll-view scroll-x class="faq-scroll">
      <view class="faq-wrap">
        <view
          class="faq-tag"
          wx:for="{{faqs}}"
          wx:key="*this"
          bindtap="sendFaq"
          data-msg="{{item}}"
        >{{item}}</view>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="chat-scroll" scroll-into-view="{{scrollToId}}">
      <view class="chat-list">
        <view
          class="bubble-wrap {{item.role === 'user' ? 'bubble-wrap--user' : 'bubble-wrap--ai'}}"
          wx:for="{{messages}}"
          wx:key="id"
          id="msg-{{item.id}}"
        >
          <view class="avatar" wx:if="{{item.role === 'ai'}}">🌱</view>
          <view class="bubble {{item.role === 'user' ? 'bubble--user' : 'bubble--ai'}}">{{item.content}}</view>
          <view class="avatar-user" wx:if="{{item.role === 'user'}}">👤</view>
        </view>

        <view class="bubble-wrap bubble-wrap--ai" wx:if="{{thinking}}">
          <view class="avatar">🌱</view>
          <view class="bubble bubble--ai bubble--thinking">
            <van-loading size="20px" color="#52C41A" /> 小桥正在思考...
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="input-bar">
      <van-field value="{{inputMsg}}" bind:input="onInput" placeholder="输入问题..." custom-class="input-field" />
      <van-button type="primary" round size="small" bindclick="sendMessage" disabled="{{!inputMsg || thinking}}">发送</van-button>
    </view>
  </block>
</view>
```

- [ ] **Step 2: 在 chat.wxss 末尾追加 gate-card 样式**

在 `miniprogram/pages/chat/chat.wxss` 末尾（现有最后一行 `.input-field { flex: 1; }` 之后）追加：

```css
/* 未评估引导卡 */
.gate-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  padding: 60rpx 48rpx;
  text-align: center;
}
.gate-icon { font-size: 100rpx; margin-bottom: 32rpx; }
.gate-title { font-size: 34rpx; font-weight: 800; color: var(--color-text); margin-bottom: 16rpx; }
.gate-desc { font-size: 26rpx; color: var(--color-text-sub); line-height: 1.7; margin-bottom: 48rpx; }
.gate-btn {
  background: var(--color-orange);
  color: #fff;
  border-radius: var(--radius-btn);
  padding: 22rpx 60rpx;
  font-size: 30rpx;
  font-weight: 700;
}
```

- [ ] **Step 3: 在开发者工具模拟器截图验证（需 MCP 连接 ws://localhost:9420）**

先清除本地存储模拟未评估状态：
```js
// 在开发者工具 Console 中执行
wx.removeStorageSync('lastAssessmentResult')
wx.removeStorageSync('lastPlan')
```
然后切换到问答 tab，截图确认：显示引导卡，无输入框。

再模拟有评估状态：
```js
wx.setStorageSync('lastAssessmentResult', {
  overall_level: '良好',
  strengths: ['语言能力', '社交能力'],
  areas_to_improve: ['数学认知', '专注力'],
})
```
刷新页面，截图确认：FAQ 显示"有什么方法提高孩子的数学能力？"和"怎么训练孩子的专注力？"

- [ ] **Step 4: Commit**

```bash
git add miniprogram/pages/chat/chat.wxml miniprogram/pages/chat/chat.wxss
git commit -m "feat: add assessment gate card and update chat WXML/WXSS"
```

---

## Task 5：整体验证

- [ ] **Step 1: 确认所有文件已提交**

```bash
git status
```
预期：`nothing to commit, working tree clean`

- [ ] **Step 2: 截图验证未评估状态**

MCP 连接（wsEndpoint: ws://localhost:9420），切换到问答 tab，确认引导卡正常显示。

- [ ] **Step 3: 截图验证有评估状态**

在开发者工具 Console 注入模拟数据：
```js
wx.setStorageSync('lastAssessmentResult', {
  overall_level: '良好',
  strengths: ['语言能力'],
  areas_to_improve: ['数学认知', '专注力'],
})
wx.setStorageSync('lastPlan', {
  weekly_goals: ['巩固20以内加减法', '每天15分钟专注训练'],
})
```

切换到问答 tab，截图确认 FAQ 显示维度对应的快捷问题。

- [ ] **Step 4: Final commit（如有遗漏文件）**

```bash
git add -A
git status  # 确认 clean 后跳过此步
```

---

## 注意事项

1. **onShow vs onLoad**：chat.js 同时实现 `onLoad` 和 `onShow`，因为用户可能在评估后直接切换回问答 tab（不触发 onLoad），`onShow` 确保状态更新。

2. **childContext 大小**：`weekly_goals` 只传计划的周目标数组（字符串列表），不传 `daily_activities` 等完整结构，控制每次请求体积。

3. **云函数部署**：修改云函数后需在微信开发者工具右键点击云函数目录 → "上传并部署"，本地模拟器测试不需要部署但真机需要。

4. **buildSystemPrompt 防御**：无 childContext 时完全回退到原有通用 prompt，确保向后兼容。
