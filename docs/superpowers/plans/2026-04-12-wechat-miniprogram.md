# 小桥微信小程序 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Python/Streamlit "小桥"应用改造为微信小程序，使用 CloudBase Node.js 云函数提供后端能力，原生 WXML + Vant Weapp 构建前端四个页面。

**Architecture:** 原生 WXML 前端通过 `wx.cloud.callFunction()` 调用 CloudBase 云函数；云函数使用原生 `fetch` 调用 SiliconFlow（DeepSeek V3.2）API；知识库全文嵌入云函数 system prompt；CloudBase NoSQL 存储孩子档案与评估历史。

**Tech Stack:** 原生 WXML/WXSS/JS、Vant Weapp v4.x、Apache ECharts（雷达图）、CloudBase Node.js 18、Jest（云函数单测）、SiliconFlow `Pro/deepseek-ai/DeepSeek-V3.2`

---

## 前置条件（开始前确认）

- [ ] 微信开发者工具已安装（https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html）
- [ ] 已有小程序 AppID（在 `wenwen2code` 云开发环境绑定的那个）
- [ ] `tcb` CLI 已登录（`tcb env list` 显示 wenwen2code 环境正常）

---

## 文件结构（改造后完整目录）

```
kindergarten_to_school/
├── project.config.json               # 微信小程序项目配置（AppID）
├── miniprogram/                      # 小程序前端
│   ├── app.js                        # App 初始化 + 云开发 init
│   ├── app.json                      # 全局配置、TabBar、页面路由
│   ├── app.wxss                      # 全局样式变量
│   └── pages/
│       ├── home/
│       │   ├── home.js
│       │   ├── home.json
│       │   ├── home.wxml
│       │   └── home.wxss
│       ├── assessment/
│       │   ├── assessment.js
│       │   ├── assessment.json
│       │   ├── assessment.wxml
│       │   └── assessment.wxss
│       ├── result/
│       │   ├── result.js
│       │   ├── result.json
│       │   ├── result.wxml
│       │   └── result.wxss
│       ├── plan/
│       │   ├── plan.js
│       │   ├── plan.json
│       │   ├── plan.wxml
│       │   └── plan.wxss
│       └── chat/
│           ├── chat.js
│           ├── chat.json
│           ├── chat.wxml
│           └── chat.wxss
└── cloudfunctions/                   # CloudBase 云函数
    ├── assessment/
    │   ├── index.js                  # 云函数入口
    │   ├── assessment-logic.js       # 纯算法逻辑（可单测）
    │   ├── package.json
    │   └── __tests__/
    │       └── assessment-logic.test.js
    ├── generatePlan/
    │   ├── index.js
    │   ├── knowledge-base.js         # 嵌入知识库文本
    │   ├── fallback-plan.js          # 无 LLM 时默认计划
    │   └── package.json
    ├── chat/
    │   ├── index.js
    │   ├── fallback-qa.js            # 本地问答降级
    │   └── package.json
    └── analyzeDeep/
        ├── index.js
        └── package.json
```

---

## Phase 1：项目脚手架

### Task 1：初始化项目结构

**Files:**
- Create: `project.config.json`
- Create: `miniprogram/app.json`
- Create: `miniprogram/app.js`
- Create: `miniprogram/app.wxss`

- [ ] **Step 1：创建 project.config.json**

将 `YOUR_APPID` 替换为实际 AppID（在微信公众平台查询）：

```json
{
  "miniprogramRoot": "miniprogram/",
  "cloudfunctionRoot": "cloudfunctions/",
  "setting": {
    "urlCheck": true,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "minified": true
  },
  "appid": "YOUR_APPID",
  "projectname": "kindergarten-to-school",
  "libVersion": "2.25.0",
  "description": "小桥 - 幼小衔接规划助手"
}
```

- [ ] **Step 2：创建全局配置 miniprogram/app.json**

```json
{
  "pages": [
    "pages/home/home",
    "pages/assessment/assessment",
    "pages/result/result",
    "pages/plan/plan",
    "pages/chat/chat"
  ],
  "tabBar": {
    "color": "#888888",
    "selectedColor": "#52C41A",
    "backgroundColor": "#ffffff",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/home/home",
        "text": "首页",
        "iconPath": "assets/icons/home.png",
        "selectedIconPath": "assets/icons/home-active.png"
      },
      {
        "pagePath": "pages/assessment/assessment",
        "text": "评估",
        "iconPath": "assets/icons/assess.png",
        "selectedIconPath": "assets/icons/assess-active.png"
      },
      {
        "pagePath": "pages/plan/plan",
        "text": "计划",
        "iconPath": "assets/icons/plan.png",
        "selectedIconPath": "assets/icons/plan-active.png"
      },
      {
        "pagePath": "pages/chat/chat",
        "text": "问答",
        "iconPath": "assets/icons/chat.png",
        "selectedIconPath": "assets/icons/chat-active.png"
      }
    ]
  },
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#52C41A",
    "navigationBarTitleText": "小桥",
    "navigationBarTextStyle": "white"
  },
  "usingComponents": {
    "van-button": "@vant/weapp/button/index",
    "van-popup": "@vant/weapp/popup/index",
    "van-rate": "@vant/weapp/rate/index",
    "van-toast": "@vant/weapp/toast/index",
    "van-loading": "@vant/weapp/loading/index",
    "van-field": "@vant/weapp/field/index",
    "van-picker": "@vant/weapp/picker/index",
    "van-tab": "@vant/weapp/tab/index",
    "van-tabs": "@vant/weapp/tabs/index",
    "van-icon": "@vant/weapp/icon/index",
    "van-tag": "@vant/weapp/tag/index"
  },
  "sitemapLocation": "sitemap.json"
}
```

- [ ] **Step 3：创建 miniprogram/app.js**

```javascript
// miniprogram/app.js
App({
  onLaunch() {
    wx.cloud.init({
      env: 'wenwen2code-4gxuthj048ae0fb0',
      traceUser: true,
    })
  },
  globalData: {
    // 当前孩子档案，评估流程中共享
    currentChild: null,
  },
})
```

- [ ] **Step 4：创建 miniprogram/app.wxss（全局样式变量）**

```css
/* miniprogram/app.wxss */
page {
  --color-primary: #52C41A;
  --color-primary-light: #F6FFED;
  --color-primary-mid: #D9F7BE;
  --color-primary-dark: #389E0D;
  --color-text: #333333;
  --color-text-sub: #888888;
  --color-border: #f0f0f0;
  --radius-card: 16rpx;
  --radius-btn: 40rpx;

  background-color: #f5f5f5;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: var(--color-text);
  font-size: 28rpx;
  line-height: 1.6;
}

.card {
  background: #fff;
  border-radius: var(--radius-card);
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.btn-primary {
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-btn);
  padding: 20rpx 0;
  text-align: center;
  font-size: 30rpx;
  font-weight: 600;
}

.btn-primary-disabled {
  background: #b7eb8f;
  color: #fff;
  border-radius: var(--radius-btn);
  padding: 20rpx 0;
  text-align: center;
  font-size: 30rpx;
}
```

- [ ] **Step 5：安装 Vant Weapp**

```bash
cd miniprogram
npm init -y
npm i @vant/weapp
```

在微信开发者工具中：工具 → 构建 npm，确认 `miniprogram_npm/` 目录生成。

- [ ] **Step 6：Commit**

```bash
git add project.config.json miniprogram/
git commit -m "feat: scaffold miniprogram project structure with Vant Weapp"
```

---

## Phase 2：云函数 — assessment

### Task 2：移植评估算法为 Node.js

**Files:**
- Create: `cloudfunctions/assessment/assessment-logic.js`
- Create: `cloudfunctions/assessment/__tests__/assessment-logic.test.js`
- Create: `cloudfunctions/assessment/index.js`
- Create: `cloudfunctions/assessment/package.json`

- [ ] **Step 1：创建 cloudfunctions/assessment/package.json**

```json
{
  "name": "assessment",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

- [ ] **Step 2：安装 Jest**

```bash
cd cloudfunctions/assessment
npm install
```

- [ ] **Step 3：写失败测试 cloudfunctions/assessment/__tests__/assessment-logic.test.js**

```javascript
const { calculateAssessment } = require('../assessment-logic')

const baseProfile = {
  language: { listening: 3, expression: 3, reading: 3, writing_interest: 3 },
  math: { counting: 3, operation: 3, shapes: 3, space: 3 },
  social: 3, self_care: 3, motor: 3,
  focus: 3, emotion: 3, time_awareness: 3,
}

test('全3分返回良好', () => {
  const result = calculateAssessment(baseProfile)
  expect(result.overall_level).toBe('良好')
  expect(result.strengths).toBeInstanceOf(Array)
  expect(result.areas_to_improve).toBeInstanceOf(Array)
  expect(result.recommendations).toBeInstanceOf(Array)
})

test('全5分返回优秀', () => {
  const highProfile = {
    language: { listening: 5, expression: 5, reading: 5, writing_interest: 5 },
    math: { counting: 5, operation: 5, shapes: 5, space: 5 },
    social: 5, self_care: 5, motor: 5,
    focus: 5, emotion: 5, time_awareness: 5,
  }
  const result = calculateAssessment(highProfile)
  expect(result.overall_level).toBe('优秀')
  expect(result.strengths.length).toBeGreaterThan(0)
  expect(result.areas_to_improve).toHaveLength(0)
})

test('全1分返回需加强关注并有建议', () => {
  const lowProfile = {
    language: { listening: 1, expression: 1, reading: 1, writing_interest: 1 },
    math: { counting: 1, operation: 1, shapes: 1, space: 1 },
    social: 1, self_care: 1, motor: 1,
    focus: 1, emotion: 1, time_awareness: 1,
  }
  const result = calculateAssessment(lowProfile)
  expect(result.overall_level).toBe('需加强关注')
  expect(result.areas_to_improve.length).toBeGreaterThan(0)
  expect(result.recommendations.length).toBeGreaterThan(0)
})

test('缺失字段使用默认值3，不崩溃', () => {
  expect(() => calculateAssessment({})).not.toThrow()
})

test('分数超出范围自动截断', () => {
  const profile = { ...baseProfile, social: 10 }
  const result = calculateAssessment(profile)
  expect(result.overall_level).toBeDefined()
})

test('语言得分>=4时有倾听优势', () => {
  const profile = { ...baseProfile, language: { listening: 4, expression: 4, reading: 4, writing_interest: 4 } }
  const result = calculateAssessment(profile)
  expect(result.strengths.some(s => s.includes('倾听'))).toBe(true)
})
```

- [ ] **Step 4：运行测试确认失败**

```bash
cd cloudfunctions/assessment
npm test
```

预期：FAIL — `Cannot find module '../assessment-logic'`

- [ ] **Step 5：实现 cloudfunctions/assessment/assessment-logic.js**

```javascript
// cloudfunctions/assessment/assessment-logic.js
'use strict'

const LANG_KEYS = ['listening', 'expression', 'reading', 'writing_interest']
const MATH_KEYS = ['counting', 'operation', 'shapes', 'space']

function score(value) {
  const n = parseInt(value, 10)
  if (isNaN(n)) return 3
  return Math.max(1, Math.min(5, n))
}

function addFeedback(s, strengths, areas, recs, strengthMsg, areaMsg, tip) {
  if (s >= 4) strengths.push(strengthMsg)
  else if (s <= 2) { areas.push(areaMsg); recs.push(tip) }
}

function calculateAssessment(profile = {}) {
  const language = profile.language || {}
  const math = profile.math || {}

  const langVals = LANG_KEYS.map(k => score(language[k] ?? 3))
  const mathVals = MATH_KEYS.map(k => score(math[k] ?? 3))
  const langAvg = langVals.reduce((a, b) => a + b, 0) / langVals.length
  const mathAvg = mathVals.reduce((a, b) => a + b, 0) / mathVals.length

  const social         = score(profile.social         ?? 3)
  const self_care      = score(profile.self_care      ?? 3)
  const motor          = score(profile.motor          ?? 3)
  const focus          = score(profile.focus          ?? 3)
  const emotion        = score(profile.emotion        ?? 3)
  const time_awareness = score(profile.time_awareness ?? 3)

  const total = langAvg + mathAvg + social + self_care + motor + focus + emotion + time_awareness

  const strengths = [], areas_to_improve = [], recommendations = []

  addFeedback(score(language.listening       ?? 3), strengths, areas_to_improve, recommendations,
    '倾听能力较好，能听懂指令', '倾听理解能力', '多与孩子交流复杂指令，锻炼理解能力')
  addFeedback(score(language.expression      ?? 3), strengths, areas_to_improve, recommendations,
    '语言表达清晰流畅', '语言表达能力', '每天15分钟亲子对话，鼓励孩子复述故事')
  addFeedback(score(language.reading         ?? 3), strengths, areas_to_improve, recommendations,
    '阅读兴趣浓厚', '阅读习惯', '建立固定阅读时间，选择孩子感兴趣的绘本')
  addFeedback(score(language.writing_interest?? 3), strengths, areas_to_improve, recommendations,
    '对书写有兴趣，能进行简单书写', '书写兴趣与握笔习惯', '用描红、描写名字等方式增强书写兴趣')

  addFeedback(score(math.counting ?? 3), strengths, areas_to_improve, recommendations,
    '计数能力较强', '计数能力', '通过实物点数练习，20以内手口一致点数')
  addFeedback(score(math.operation?? 3), strengths, areas_to_improve, recommendations,
    '运算能力发展良好', '简单运算', '用实物游戏理解加减法含义')
  addFeedback(score(math.shapes   ?? 3), strengths, areas_to_improve, recommendations,
    '图形认知能力好', '图形认知', '通过积木、拼图认识基本几何图形')
  addFeedback(score(math.space    ?? 3), strengths, areas_to_improve, recommendations,
    '空间方位感较强', '空间感知', '多进行上下前后左右的方位游戏')

  addFeedback(social,    strengths, areas_to_improve, recommendations,
    '社交能力强，愿意与同伴合作', '社交能力', '创造合作游戏机会，鼓励轮流与分享')
  addFeedback(self_care, strengths, areas_to_improve, recommendations,
    '自理能力强', '自理能力', '开始训练独立整理书包、穿脱衣物')
  addFeedback(motor,     strengths, areas_to_improve, recommendations,
    '运动和动手能力好', '运动能力', '增加户外运动和精细动作练习')
  addFeedback(focus,     strengths, areas_to_improve, recommendations,
    '专注力强，能持续较长时间', '专注力', '从15分钟开始训练，使用计时器分段完成任务')
  addFeedback(emotion,   strengths, areas_to_improve, recommendations,
    '情绪稳定，能自我调节', '情绪管理', '教孩子识别和表达情绪，建立冷静角')
  addFeedback(time_awareness, strengths, areas_to_improve, recommendations,
    '时间观念强，能按时完成任务', '时间观念', '使用可视化计时器，建立固定作息表')

  let overall_level
  if (total >= 32) {
    overall_level = '优秀'
    recommendations.push('孩子发展良好，可以顺利过渡到小学')
  } else if (total >= 24) {
    overall_level = '良好'
  } else {
    overall_level = '需加强关注'
    recommendations.push('建议增加幼小衔接训练的投入')
  }

  return { overall_level, strengths, areas_to_improve, recommendations }
}

module.exports = { calculateAssessment }
```

- [ ] **Step 6：运行测试确认通过**

```bash
cd cloudfunctions/assessment
npm test
```

预期：全部 6 个测试 PASS。

- [ ] **Step 7：创建云函数入口 cloudfunctions/assessment/index.js**

```javascript
// cloudfunctions/assessment/index.js
'use strict'
const cloud = require('wx-server-sdk')
const { calculateAssessment } = require('./assessment-logic')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

exports.main = async (event) => {
  const { scores } = event
  if (!scores) return { code: 400, message: '缺少 scores 参数' }
  try {
    const result = calculateAssessment(scores)
    return { code: 0, data: result }
  } catch (err) {
    return { code: 500, message: err.message }
  }
}
```

- [ ] **Step 8：Commit**

```bash
git add cloudfunctions/assessment/
git commit -m "feat: add assessment cloud function with JS port of assessment.py"
```

---

## Phase 3：云函数 — generatePlan

### Task 3：知识库嵌入 + LLM 计划生成

**Files:**
- Create: `cloudfunctions/generatePlan/knowledge-base.js`
- Create: `cloudfunctions/generatePlan/fallback-plan.js`
- Create: `cloudfunctions/generatePlan/index.js`
- Create: `cloudfunctions/generatePlan/package.json`

- [ ] **Step 1：创建 cloudfunctions/generatePlan/package.json**

```json
{
  "name": "generatePlan",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "wx-server-sdk": "latest"
  }
}
```

- [ ] **Step 2：创建 cloudfunctions/generatePlan/knowledge-base.js**

将 `knowledge_base.md` 内容嵌入为 JS 常量（直接复制文件内容）：

```javascript
// cloudfunctions/generatePlan/knowledge-base.js
'use strict'

const KNOWLEDGE_BASE = `
# 幼小衔接知识库（基于《3-6岁儿童学习与发展指南》）

## 一、语言能力（5-6岁目标）

### 1.1 倾听与表达
**目标1：认真倾听并理解常用语言**
- 能听懂日常对话，听懂公共场合的规则要求
- 能理解指令性语言（"请把...收好"、"先...再..."）
- 能理解故事情节，复述故事主要内容
- 能理解简单的时间顺序（先...然后...最后）

**目标2：愿意讲话并能清楚地表达**
- 愿意在集体面前发言，回答问题声音响亮
- 能围绕主题讲述自己的见闻和经历
- 能有序、连贯、清楚地讲述一件事

**目标3：文明用语习惯**
- 会使用"请"、"谢谢"、"对不起"等礼貌用语

### 1.2 阅读与书写准备
- 喜欢听故事、看图书，每天阅读不少于20分钟
- 认识自己的名字和常见汉字（100-200个）
- 会正确握笔，尝试书写自己的名字

## 二、数学认知（5-6岁目标）
- 会手口一致地点数20以内的物体
- 掌握10以内数的加减运算
- 认识正方形、长方形、三角形、圆形等基本图形
- 能区分上下、前后、左右方位

## 三、其他核心能力
- 自理：独立如厕、整理书包、穿脱衣服、系鞋带
- 社交：愿意与同伴交往，懂得轮流、分享和合作
- 专注：专注力15-20分钟，能在规定时间内完成简单任务

## 四、家长常见问题
Q: 要不要提前学小学内容？
A: 不建议系统学习，重点是能力培养，不是知识灌输。

Q: 孩子注意力不集中怎么办？
A: 从15分钟开始训练，通过拼图、积木等游戏培养专注力。

Q: 如何培养时间观念？
A: 使用可视化计时器，制定固定作息表，让孩子参与时间管理。

## 五、推荐资源
- 绘本：《我上小学了》《跑跑镇》《首先有一个苹果》
- APP：洪恩识字、斑马思维、小火花数学
- 动画：《蓝色小考拉》《小鼠波波》

## 参考依据
- 教育部《3-6岁儿童学习与发展指南》（2012）
`

module.exports = { KNOWLEDGE_BASE }
```

- [ ] **Step 3：创建 cloudfunctions/generatePlan/fallback-plan.js**

```javascript
// cloudfunctions/generatePlan/fallback-plan.js
'use strict'

function getDefaultPlan(duration = '3个月') {
  return {
    duration,
    weekly_goals: [
      '培养时间观念，养成固定作息',
      '加强语言表达和倾听能力',
      '提升自理能力（整理书包、如厕等）',
      '增强社交合作能力',
    ],
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

- [ ] **Step 4：创建 cloudfunctions/generatePlan/index.js**

```javascript
// cloudfunctions/generatePlan/index.js
'use strict'
const cloud = require('wx-server-sdk')
const { KNOWLEDGE_BASE } = require('./knowledge-base')
const { getDefaultPlan } = require('./fallback-plan')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const SILICONFLOW_API_KEY = process.env.SILICONFLOW_API_KEY
const SILICONFLOW_BASE_URL = 'https://api.siliconflow.cn/v1'
const MODEL = 'Pro/deepseek-ai/DeepSeek-V3'

async function callLLM(systemPrompt, userPrompt) {
  const resp = await fetch(`${SILICONFLOW_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${SILICONFLOW_API_KEY}`,
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.7,
      response_format: { type: 'json_object' },
    }),
  })
  if (!resp.ok) throw new Error(`LLM API error: ${resp.status}`)
  const data = await resp.json()
  return data.choices[0].message.content
}

exports.main = async (event) => {
  const { childProfile, assessmentResult, duration = '3个月' } = event
  if (!childProfile || !assessmentResult) {
    return { code: 400, message: '缺少 childProfile 或 assessmentResult' }
  }

  const hometownTip = childProfile.hometown
    ? `\n请结合${childProfile.hometown}当地幼小衔接政策和小学入学要求，给出针对性建议。`
    : ''

  const systemPrompt = `你是"小桥"——幼小衔接规划专家。请根据孩子信息生成个性化计划。
请严格返回 JSON 格式，结构如下：
{"duration":"3个月","weekly_goals":["目标1","目标2","目标3","目标4"],"daily_activities":[{"time":"早晨","activity":"活动内容","goal":"活动目标"}],"resources":["资源1"],"parent_tips":["建议1"],"evaluation_criteria":["标准1"]}

知识库参考：
${KNOWLEDGE_BASE}${hometownTip}`

  const userPrompt = `请为以下孩子生成${duration}的幼小衔接计划：
姓名：${childProfile.name || '孩子'}
年龄：${childProfile.age || 5.5}岁
整体水平：${assessmentResult.overall_level}
优势：${assessmentResult.strengths?.join('、') || '暂无'}
需加强：${assessmentResult.areas_to_improve?.join('、') || '暂无'}
兴趣爱好：${childProfile.interests?.join('、') || '暂无'}
家长担忧：${childProfile.concerns?.join('、') || '暂无'}`

  try {
    if (!SILICONFLOW_API_KEY) throw new Error('未配置 API Key')
    const raw = await callLLM(systemPrompt, userPrompt)
    const plan = typeof raw === 'string' ? JSON.parse(raw) : raw
    return { code: 0, data: plan }
  } catch (err) {
    console.error('generatePlan error:', err)
    return { code: 0, data: getDefaultPlan(duration), fallback: true }
  }
}
```

- [ ] **Step 5：在 CloudBase 控制台配置环境变量**

登录腾讯云 CloudBase 控制台 → wenwen2code 环境 → 云函数 → generatePlan → 环境变量：

```
SILICONFLOW_API_KEY = sk-tivkaulejqfzawrpfdtkxaruhxpafomtvxzesbtahjpdeupa
```

（chat 和 analyzeDeep 云函数部署后同样需要设置此变量）

- [ ] **Step 6：Commit**

```bash
git add cloudfunctions/generatePlan/
git commit -m "feat: add generatePlan cloud function with DeepSeek + fallback"
```

---

## Phase 4：云函数 — chat

### Task 4：问答云函数（知识库上下文 + 本地降级）

**Files:**
- Create: `cloudfunctions/chat/fallback-qa.js`
- Create: `cloudfunctions/chat/index.js`
- Create: `cloudfunctions/chat/package.json`

- [ ] **Step 1：创建 cloudfunctions/chat/package.json**

```json
{
  "name": "chat",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "wx-server-sdk": "latest"
  }
}
```

- [ ] **Step 2：创建 cloudfunctions/chat/fallback-qa.js**

```javascript
// cloudfunctions/chat/fallback-qa.js
'use strict'

const QA = [
  {
    keywords: ['提前学', '小学内容', '超前学习'],
    answer: '不建议系统学习小学内容，但可以通过游戏方式接触。重点是培养学习习惯和基础能力，避免超前学习导致入学后厌学。',
  },
  {
    keywords: ['不想去小学', '害怕小学', '入学焦虑'],
    answer: '可以带孩子参观小学熟悉环境，读《我上小学了》等绘本，认识邻居的哥哥姐姐，用正向引导取代恐吓。',
  },
  {
    keywords: ['注意力', '专注力', '坐不住'],
    answer: '从15分钟开始训练专注力，保持安静环境，通过拼图、积木、棋类游戏培养，每次只做一件事。',
  },
  {
    keywords: ['时间观念', '磨蹭', '拖拉'],
    answer: '使用可视化计时器（沙漏、番茄钟），制定固定作息表，提前提醒将要进行的活动，让孩子参与时间管理。',
  },
  {
    keywords: ['拼音', '学拼音'],
    answer: '不建议系统学习拼音，通过亲子阅读培养语感即可，避免超前学习导致入学后失去兴趣。',
  },
  {
    keywords: ['写字', '握笔', '姿势'],
    answer: '从握笔姿势开始，使用矫正器辅助，控制书写时间每次不超过15分钟，注意坐姿"三个一"（一尺一寸一拳头）。',
  },
  {
    keywords: ['社交', '内向', '不合群'],
    answer: '多安排与同龄人玩耍，通过角色扮演练习打招呼，及时鼓励社交行为，了解孩子不愿交往的原因。',
  },
  {
    keywords: ['自理', '独立', '依赖'],
    answer: '让孩子自己穿衣整理书包，把复杂任务分解成小步骤，耐心等待不代劳，及时鼓励独立行为。',
  },
]

const DEFAULT = '这个问题建议咨询专业教育人士或查看当地教育部门官方指南。'

function fallbackAnswer(message) {
  const msg = message.toLowerCase()
  for (const item of QA) {
    if (item.keywords.some(kw => msg.includes(kw))) {
      return item.answer
    }
  }
  return DEFAULT
}

module.exports = { fallbackAnswer }
```

- [ ] **Step 3：创建 cloudfunctions/chat/index.js**

```javascript
// cloudfunctions/chat/index.js
'use strict'
const cloud = require('wx-server-sdk')
const { fallbackAnswer } = require('./fallback-qa')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const SILICONFLOW_API_KEY = process.env.SILICONFLOW_API_KEY
const SILICONFLOW_BASE_URL = 'https://api.siliconflow.cn/v1'
const MODEL = 'Pro/deepseek-ai/DeepSeek-V3'

const KNOWLEDGE_BASE = require('../generatePlan/knowledge-base').KNOWLEDGE_BASE

const SYSTEM_PROMPT = `你是"小桥"——幼小衔接规划专家，专为5-6岁儿童家庭服务。
回答原则：温暖、专业、实用，给出具体可操作的建议，控制在200字以内。

知识库参考：
${KNOWLEDGE_BASE}`

exports.main = async (event) => {
  const { message, history = [] } = event
  if (!message) return { code: 400, message: '缺少 message 参数' }

  try {
    if (!SILICONFLOW_API_KEY) throw new Error('未配置 API Key')

    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...history.slice(-6),  // 保留最近6条历史
      { role: 'user', content: message },
    ]

    const resp = await fetch(`${SILICONFLOW_BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SILICONFLOW_API_KEY}`,
      },
      body: JSON.stringify({ model: MODEL, messages, temperature: 0.7 }),
    })

    if (!resp.ok) throw new Error(`API error: ${resp.status}`)
    const data = await resp.json()
    const reply = data.choices[0].message.content
    return { code: 0, data: { reply } }
  } catch (err) {
    console.error('chat error:', err)
    const reply = fallbackAnswer(message)
    return { code: 0, data: { reply }, fallback: true }
  }
}
```

- [ ] **Step 4：Commit**

```bash
git add cloudfunctions/chat/
git commit -m "feat: add chat cloud function with fallback QA"
```

---

## Phase 5：云函数 — analyzeDeep

### Task 5：进阶 AI 分析（多次评估对比）

**Files:**
- Create: `cloudfunctions/analyzeDeep/index.js`
- Create: `cloudfunctions/analyzeDeep/package.json`

- [ ] **Step 1：创建 cloudfunctions/analyzeDeep/package.json**

```json
{
  "name": "analyzeDeep",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "wx-server-sdk": "latest"
  }
}
```

- [ ] **Step 2：创建 cloudfunctions/analyzeDeep/index.js**

```javascript
// cloudfunctions/analyzeDeep/index.js
'use strict'
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const SILICONFLOW_API_KEY = process.env.SILICONFLOW_API_KEY
const SILICONFLOW_BASE_URL = 'https://api.siliconflow.cn/v1'
const MODEL = 'Pro/deepseek-ai/DeepSeek-V3'

exports.main = async (event) => {
  const { child, assessments } = event

  if (!assessments || assessments.length < 2) {
    return { code: 400, message: '需要至少2次评估记录才能进行深度分析' }
  }

  const hometownTip = child?.hometown
    ? `\n请结合${child.hometown}当地幼小衔接政策给出针对性升学建议。`
    : ''

  const systemPrompt = `你是"小桥"幼小衔接分析专家。根据孩子多次评估数据，生成深度分析报告。
返回严格 JSON 格式：
{"growth_summary":"总体成长描述","dimension_trends":[{"dimension":"维度名","trend":"上升/稳定/下降","detail":"具体说明"}],"weak_spots_plan":[{"dimension":"弱项维度","daily_exercise":"每日练习内容"}],"estimated_weeks":8,"local_policy_tips":"当地政策建议"}${hometownTip}`

  const assessmentSummary = assessments.map((a, i) => {
    const s = a.scores
    return `第${i+1}次评估（${new Date(a.createdAt).toLocaleDateString('zh-CN')}）：
整体水平=${a.result.overall_level}
语言均分=${((s.language?.listening??3)+(s.language?.expression??3)+(s.language?.reading??3)+(s.language?.writing_interest??3))/4}
数学均分=${((s.math?.counting??3)+(s.math?.operation??3)+(s.math?.shapes??3)+(s.math?.space??3))/4}
社交=${s.social??3} 自理=${s.self_care??3} 专注=${s.focus??3}`
  }).join('\n\n')

  const userPrompt = `孩子：${child?.name || '孩子'}，${child?.age || 5.5}岁\n\n${assessmentSummary}`

  try {
    if (!SILICONFLOW_API_KEY) throw new Error('未配置 API Key')
    const resp = await fetch(`${SILICONFLOW_BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SILICONFLOW_API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.6,
        response_format: { type: 'json_object' },
      }),
    })
    if (!resp.ok) throw new Error(`API error: ${resp.status}`)
    const data = await resp.json()
    const analysis = JSON.parse(data.choices[0].message.content)
    return { code: 0, data: analysis }
  } catch (err) {
    console.error('analyzeDeep error:', err)
    return { code: 500, message: '深度分析暂时不可用，请稍后重试' }
  }
}
```

- [ ] **Step 3：部署全部4个云函数**

```bash
tcb fn deploy assessment --envId wenwen2code-4gxuthj048ae0fb0
tcb fn deploy generatePlan --envId wenwen2code-4gxuthj048ae0fb0
tcb fn deploy chat --envId wenwen2code-4gxuthj048ae0fb0
tcb fn deploy analyzeDeep --envId wenwen2code-4gxuthj048ae0fb0
```

预期输出：每个函数显示 `Deployment completed`。

- [ ] **Step 4：验证 assessment 云函数（在 CloudBase 控制台测试）**

在 CloudBase 控制台 → 云函数 → assessment → 测试，输入：

```json
{
  "scores": {
    "language": {"listening":4,"expression":3,"reading":3,"writing_interest":2},
    "math": {"counting":4,"operation":3,"shapes":3,"space":3},
    "social":3,"self_care":2,"motor":4,"focus":3,"emotion":3,"time_awareness":3
  }
}
```

预期返回：`{"code":0,"data":{"overall_level":"良好","strengths":[...],"areas_to_improve":[...],"recommendations":[...]}}`

- [ ] **Step 5：Commit**

```bash
git add cloudfunctions/analyzeDeep/
git commit -m "feat: add analyzeDeep cloud function + deploy all 4 functions"
```

---

## Phase 6：小程序页面

### Task 6：首页

**Files:**
- Create: `miniprogram/pages/home/home.json`
- Create: `miniprogram/pages/home/home.wxml`
- Create: `miniprogram/pages/home/home.wxss`
- Create: `miniprogram/pages/home/home.js`

- [ ] **Step 1：创建 home.json**

```json
{ "navigationBarTitleText": "小桥", "usingComponents": {} }
```

- [ ] **Step 2：创建 home.wxml**

```xml
<!-- miniprogram/pages/home/home.wxml -->
<view class="container">
  <!-- Hero 区 -->
  <view class="hero">
    <view class="hero-emoji">🌱</view>
    <view class="hero-title">小桥</view>
    <view class="hero-sub">幼小衔接规划助手</view>
  </view>

  <!-- 功能入口 -->
  <view class="section-title">开始探索</view>

  <view class="menu-card" bindtap="goAssessment">
    <view class="menu-icon">📋</view>
    <view class="menu-info">
      <view class="menu-name">能力评估</view>
      <view class="menu-desc">评估孩子8个维度发展水平</view>
    </view>
    <view class="menu-arrow">›</view>
  </view>

  <view class="menu-card" bindtap="goPlan">
    <view class="menu-icon">📅</view>
    <view class="menu-info">
      <view class="menu-name">个性化计划</view>
      <view class="menu-desc">AI 定制幼小衔接方案</view>
    </view>
    <view class="menu-arrow">›</view>
  </view>

  <view class="menu-card" bindtap="goChat">
    <view class="menu-icon">💬</view>
    <view class="menu-info">
      <view class="menu-name">问答咨询</view>
      <view class="menu-desc">随时解答入学疑问</view>
    </view>
    <view class="menu-arrow">›</view>
  </view>

  <!-- 使用说明 -->
  <view class="guide card">
    <view class="guide-title">💡 使用步骤</view>
    <view class="guide-step">1. 填写孩子基本信息</view>
    <view class="guide-step">2. 完成 8 项能力评估</view>
    <view class="guide-step">3. 生成个性化计划</view>
    <view class="guide-step">4. 有问题随时咨询</view>
  </view>
</view>
```

- [ ] **Step 3：创建 home.wxss**

```css
/* miniprogram/pages/home/home.wxss */
.container { padding: 0 0 120rpx; }

.hero {
  background: linear-gradient(135deg, #52C41A 0%, #95DE64 100%);
  padding: 60rpx 40rpx 80rpx;
  text-align: center;
  color: #fff;
}
.hero-emoji { font-size: 80rpx; margin-bottom: 16rpx; }
.hero-title { font-size: 48rpx; font-weight: 700; margin-bottom: 8rpx; }
.hero-sub { font-size: 26rpx; opacity: 0.85; }

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: var(--color-text-sub);
  padding: 32rpx 32rpx 16rpx;
  text-transform: uppercase;
  letter-spacing: 2rpx;
}

.menu-card {
  display: flex;
  align-items: center;
  background: #fff;
  margin: 0 24rpx 16rpx;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}
.menu-icon { font-size: 48rpx; margin-right: 20rpx; }
.menu-info { flex: 1; }
.menu-name { font-size: 30rpx; font-weight: 600; margin-bottom: 6rpx; }
.menu-desc { font-size: 24rpx; color: var(--color-text-sub); }
.menu-arrow { font-size: 40rpx; color: #ccc; }

.guide {
  margin: 8rpx 24rpx 0;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  background: var(--color-primary-light);
}
.guide-title { font-size: 28rpx; font-weight: 700; color: var(--color-primary-dark); margin-bottom: 16rpx; }
.guide-step { font-size: 26rpx; color: var(--color-text); padding: 6rpx 0; }
```

- [ ] **Step 4：创建 home.js**

```javascript
// miniprogram/pages/home/home.js
Page({
  goAssessment() {
    wx.switchTab({ url: '/pages/assessment/assessment' })
  },
  goPlan() {
    wx.switchTab({ url: '/pages/plan/plan' })
  },
  goChat() {
    wx.switchTab({ url: '/pages/chat/chat' })
  },
})
```

- [ ] **Step 5：在微信开发者工具中验证**

打开微信开发者工具，导入项目，模拟器中确认：
- [ ] 绿色渐变 Hero 区正常显示
- [ ] 3张菜单卡片显示且可点击
- [ ] TabBar 显示且切换正常

- [ ] **Step 6：Commit**

```bash
git add miniprogram/pages/home/
git commit -m "feat: add home page with green hero and menu cards"
```

---

### Task 7：评估页（图卡总览）

**Files:**
- Create: `miniprogram/pages/assessment/assessment.json`
- Create: `miniprogram/pages/assessment/assessment.wxml`
- Create: `miniprogram/pages/assessment/assessment.wxss`
- Create: `miniprogram/pages/assessment/assessment.js`

- [ ] **Step 1：创建 assessment.json**

```json
{
  "navigationBarTitleText": "能力评估",
  "usingComponents": {
    "van-popup": "@vant/weapp/popup/index",
    "van-rate": "@vant/weapp/rate/index",
    "van-button": "@vant/weapp/button/index",
    "van-toast": "@vant/weapp/toast/index"
  }
}
```

- [ ] **Step 2：创建 assessment.wxml**

```xml
<!-- miniprogram/pages/assessment/assessment.wxml -->
<van-toast id="van-toast" />

<view class="container">
  <!-- 进度头部 -->
  <view class="progress-bar">
    <view class="progress-label">已完成 {{doneCount}} / {{dimensions.length}}</view>
    <view class="progress-track">
      <view class="progress-fill" style="width: {{doneCount / dimensions.length * 100}}%"></view>
    </view>
  </view>

  <!-- 孩子信息简介 -->
  <view class="child-info card" wx:if="{{childName}}">
    <text>🌱 正在评估：{{childName}}，{{childAge}} 岁</text>
  </view>

  <!-- 维度卡片网格 -->
  <view class="dim-grid">
    <view
      class="dim-card {{item.done ? 'dim-card--done' : ''}} {{currentDim === index ? 'dim-card--active' : ''}}"
      wx:for="{{dimensions}}"
      wx:key="key"
      bindtap="openPopup"
      data-index="{{index}}"
    >
      <view class="dim-check" wx:if="{{item.done}}">✅</view>
      <view class="dim-icon">{{item.icon}}</view>
      <view class="dim-name">{{item.name}}</view>
      <view class="dim-score" wx:if="{{item.done}}">
        <text wx:for="{{item.rating}}" wx:key="*this">⭐</text>
      </view>
      <view class="dim-score dim-score--pending" wx:else>待评估</view>
    </view>
  </view>

  <!-- 完成按钮 -->
  <view class="bottom-btn">
    <van-button
      type="primary"
      block
      round
      disabled="{{doneCount < dimensions.length}}"
      custom-class="{{doneCount < dimensions.length ? 'btn-disabled' : 'btn-submit'}}"
      bindclick="submitAssessment"
      loading="{{submitting}}"
    >
      {{doneCount < dimensions.length ? '完成全部评估后查看结果' : '查看评估结果 →'}}
    </van-button>
  </view>
</view>

<!-- 评分弹窗 -->
<van-popup
  show="{{showPopup}}"
  position="bottom"
  round
  bind:close="closePopup"
  custom-style="padding: 40rpx 32rpx 80rpx;"
>
  <view wx:if="{{currentDimData}}">
    <view class="popup-icon">{{currentDimData.icon}}</view>
    <view class="popup-title">{{currentDimData.name}}</view>
    <view class="popup-desc">{{currentDimData.desc}}</view>
    <view class="popup-rate-label">
      <text>需加强</text>
      <text>非常棒</text>
    </view>
    <van-rate
      value="{{currentRating}}"
      bind:change="onRateChange"
      size="40"
      color="#52C41A"
      void-color="#d9f7be"
      count="5"
    />
    <van-button type="primary" block round custom-style="margin-top: 32rpx;" bindclick="confirmRating">
      确认 ({{currentRating}} 分)
    </van-button>
  </view>
</van-popup>
```

- [ ] **Step 3：创建 assessment.wxss**

```css
/* miniprogram/pages/assessment/assessment.wxss */
.container { padding-bottom: 160rpx; }

.progress-bar { padding: 24rpx 32rpx 16rpx; background: #fff; }
.progress-label { font-size: 24rpx; color: var(--color-text-sub); margin-bottom: 12rpx; }
.progress-track { height: 8rpx; background: var(--color-primary-mid); border-radius: 4rpx; }
.progress-fill { height: 8rpx; background: var(--color-primary); border-radius: 4rpx; transition: width 0.3s; }

.child-info { margin: 16rpx 24rpx 0; padding: 20rpx 24rpx; font-size: 26rpx; color: var(--color-primary-dark); }

.dim-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
  padding: 20rpx 24rpx;
}

.dim-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 32rpx 20rpx;
  text-align: center;
  border: 3rpx solid var(--color-border);
  position: relative;
  transition: all 0.2s;
}
.dim-card--done { border-color: var(--color-primary); background: var(--color-primary-light); }
.dim-card--active { box-shadow: 0 0 0 4rpx rgba(82,196,26,.3); }

.dim-check { position: absolute; top: 12rpx; right: 16rpx; font-size: 24rpx; }
.dim-icon { font-size: 56rpx; margin-bottom: 12rpx; }
.dim-name { font-size: 26rpx; font-weight: 600; margin-bottom: 8rpx; }
.dim-score { font-size: 22rpx; color: var(--color-primary); }
.dim-score--pending { color: var(--color-text-sub); }

.bottom-btn { position: fixed; bottom: 0; left: 0; right: 0; padding: 24rpx 32rpx 48rpx; background: #fff; box-shadow: 0 -2rpx 12rpx rgba(0,0,0,.06); }

.popup-icon { font-size: 72rpx; text-align: center; margin-bottom: 16rpx; }
.popup-title { font-size: 34rpx; font-weight: 700; text-align: center; margin-bottom: 12rpx; }
.popup-desc { font-size: 26rpx; color: var(--color-text-sub); text-align: center; margin-bottom: 32rpx; line-height: 1.6; }
.popup-rate-label { display: flex; justify-content: space-between; font-size: 22rpx; color: var(--color-text-sub); margin-bottom: 16rpx; }
van-rate { display: flex; justify-content: center; }
```

- [ ] **Step 4：创建 assessment.js**

```javascript
// miniprogram/pages/assessment/assessment.js
const Toast = require('@vant/weapp/toast/toast')

const DIMENSIONS = [
  {
    key: 'listening', name: '倾听理解', icon: '👂',
    desc: '孩子能否听懂老师的指令和故事内容，理解日常对话？',
    scoreKeys: ['language.listening'],
  },
  {
    key: 'expression', name: '语言表达', icon: '🗣️',
    desc: '孩子能否清楚地说出自己的想法，讲述一件事情？',
    scoreKeys: ['language.expression'],
  },
  {
    key: 'reading', name: '阅读习惯', icon: '📖',
    desc: '孩子是否喜欢阅读绘本，能否理解图书内容？',
    scoreKeys: ['language.reading'],
  },
  {
    key: 'writing', name: '书写兴趣', icon: '✏️',
    desc: '孩子是否对写字感兴趣，握笔姿势是否正确？',
    scoreKeys: ['language.writing_interest'],
  },
  {
    key: 'math', name: '数学能力', icon: '🔢',
    desc: '孩子能否数20以内的数，理解简单加减法，认识基本图形？',
    scoreKeys: ['math.counting', 'math.operation', 'math.shapes', 'math.space'],
  },
  {
    key: 'social', name: '社交能力', icon: '🤝',
    desc: '孩子能否与同龄人合作游戏，学会轮流和分享？',
    scoreKeys: ['social'],
  },
  {
    key: 'self_care', name: '自理能力', icon: '🧹',
    desc: '孩子能否独立穿衣、整理书包、自己如厕？',
    scoreKeys: ['self_care'],
  },
  {
    key: 'focus', name: '专注力', icon: '🎯',
    desc: '孩子能否持续专注15分钟以上完成一项任务？',
    scoreKeys: ['focus', 'motor', 'emotion', 'time_awareness'],
  },
]

Page({
  data: {
    dimensions: DIMENSIONS.map(d => ({ ...d, done: false, rating: 0 })),
    doneCount: 0,
    showPopup: false,
    currentDim: null,
    currentDimData: null,
    currentRating: 3,
    submitting: false,
    childName: '',
    childAge: '',
    // 最终评分存储
    scores: {
      language: { listening: 3, expression: 3, reading: 3, writing_interest: 3 },
      math: { counting: 3, operation: 3, shapes: 3, space: 3 },
      social: 3, self_care: 3, motor: 3,
      focus: 3, emotion: 3, time_awareness: 3,
    },
  },

  onLoad() {
    const app = getApp()
    const child = app.globalData.currentChild
    if (child) {
      this.setData({ childName: child.name, childAge: child.age })
    }
  },

  openPopup(e) {
    const index = e.currentTarget.dataset.index
    const dim = this.data.dimensions[index]
    this.setData({
      showPopup: true,
      currentDim: index,
      currentDimData: dim,
      currentRating: dim.rating || 3,
    })
  },

  closePopup() {
    this.setData({ showPopup: false })
  },

  onRateChange(e) {
    this.setData({ currentRating: e.detail })
  },

  confirmRating() {
    const { currentDim, currentRating, dimensions, scores } = this.data
    const dim = dimensions[currentDim]
    const rating = currentRating || 1

    // 将评分写入 scores 对象
    const newScores = { ...scores }
    if (dim.key === 'listening')  newScores.language.listening = rating
    else if (dim.key === 'expression') newScores.language.expression = rating
    else if (dim.key === 'reading')    newScores.language.reading = rating
    else if (dim.key === 'writing')    newScores.language.writing_interest = rating
    else if (dim.key === 'math') {
      newScores.math.counting = rating; newScores.math.operation = rating
      newScores.math.shapes = rating;   newScores.math.space = rating
    }
    else if (dim.key === 'social')    newScores.social = rating
    else if (dim.key === 'self_care') newScores.self_care = rating
    else if (dim.key === 'focus') {
      newScores.focus = rating; newScores.motor = rating
      newScores.emotion = rating; newScores.time_awareness = rating
    }

    const newDimensions = [...dimensions]
    newDimensions[currentDim] = { ...dim, done: true, rating }
    const doneCount = newDimensions.filter(d => d.done).length

    this.setData({ dimensions: newDimensions, doneCount, showPopup: false, scores: newScores })
  },

  async submitAssessment() {
    this.setData({ submitting: true })
    wx.showLoading({ title: '正在评估...' })
    try {
      const res = await wx.cloud.callFunction({
        name: 'assessment',
        data: { scores: this.data.scores },
      })
      if (res.result.code !== 0) throw new Error(res.result.message)
      const result = res.result.data

      // 保存到数据库
      const app = getApp()
      const child = app.globalData.currentChild
      const db = wx.cloud.database()
      const record = await db.collection('assessments').add({
        data: {
          childId: child?._id || '',
          scores: this.data.scores,
          result,
          createdAt: db.serverDate(),
        },
      })

      wx.navigateTo({
        url: `/pages/result/result?assessmentId=${record._id}`,
        success: () => {
          wx.setStorageSync('lastAssessmentResult', result)
          wx.setStorageSync('lastAssessmentScores', this.data.scores)
        },
      })
    } catch (err) {
      Toast.fail('评估失败，请重试')
      console.error(err)
    } finally {
      wx.hideLoading()
      this.setData({ submitting: false })
    }
  },
})
```

- [ ] **Step 5：在模拟器中验证**

- [ ] 8 张维度卡片 2列网格正常显示
- [ ] 点击卡片弹出底部 Popup
- [ ] 星级评分可以点击，确认后卡片变绿+显示星数
- [ ] 所有卡片完成后按钮高亮

- [ ] **Step 6：Commit**

```bash
git add miniprogram/pages/assessment/
git commit -m "feat: add assessment page with card overview and star rating popup"
```

---

### Task 8：评估结果页

**Files:**
- Create: `miniprogram/pages/result/result.json`
- Create: `miniprogram/pages/result/result.wxml`
- Create: `miniprogram/pages/result/result.wxss`
- Create: `miniprogram/pages/result/result.js`

- [ ] **Step 1：创建 result.json**

```json
{
  "navigationBarTitleText": "评估结果",
  "usingComponents": {
    "van-tag": "@vant/weapp/tag/index",
    "van-button": "@vant/weapp/button/index"
  }
}
```

- [ ] **Step 2：创建 result.wxml**

```xml
<!-- miniprogram/pages/result/result.wxml -->
<view class="container">
  <!-- 整体水平 -->
  <view class="level-card card">
    <view class="level-emoji">{{levelEmoji}}</view>
    <view class="level-text">{{result.overall_level}}</view>
    <view class="level-sub">综合评估结果</view>
  </view>

  <!-- 优势 -->
  <view class="section card" wx:if="{{result.strengths.length > 0}}">
    <view class="section-head">💪 孩子的优势</view>
    <view class="tag-wrap">
      <van-tag
        wx:for="{{result.strengths}}"
        wx:key="*this"
        type="success"
        custom-style="margin: 6rpx 8rpx; font-size: 24rpx; padding: 6rpx 16rpx;"
      >{{item}}</van-tag>
    </view>
  </view>

  <!-- 待提升 -->
  <view class="section card" wx:if="{{result.areas_to_improve.length > 0}}">
    <view class="section-head">🌱 可以加强的方向</view>
    <view class="improve-item" wx:for="{{result.areas_to_improve}}" wx:key="*this">
      <text class="dot">·</text><text>{{item}}</text>
    </view>
  </view>

  <!-- 建议 -->
  <view class="section card" wx:if="{{result.recommendations.length > 0}}">
    <view class="section-head">💡 具体建议</view>
    <view class="rec-item" wx:for="{{result.recommendations}}" wx:key="*this">
      <text class="rec-num">{{index+1}}</text>
      <text>{{item}}</text>
    </view>
  </view>

  <!-- 操作按钮 -->
  <view class="btn-group">
    <van-button type="primary" block round bindclick="generatePlan" loading="{{loading}}">
      生成个性化计划 →
    </van-button>
    <van-button plain type="primary" block round custom-style="margin-top: 16rpx;" bindclick="goBack">
      重新评估
    </van-button>
  </view>
</view>
```

- [ ] **Step 3：创建 result.wxss**

```css
/* miniprogram/pages/result/result.wxss */
.container { padding: 24rpx 24rpx 160rpx; }

.level-card { text-align: center; padding: 48rpx 24rpx; }
.level-emoji { font-size: 80rpx; margin-bottom: 16rpx; }
.level-text { font-size: 48rpx; font-weight: 700; color: var(--color-primary); margin-bottom: 8rpx; }
.level-sub { font-size: 24rpx; color: var(--color-text-sub); }

.section { margin-top: 0; }
.section-head { font-size: 30rpx; font-weight: 700; margin-bottom: 20rpx; color: var(--color-text); }
.tag-wrap { display: flex; flex-wrap: wrap; }

.improve-item { display: flex; gap: 10rpx; font-size: 26rpx; line-height: 1.6; padding: 6rpx 0; color: var(--color-text); }
.dot { color: var(--color-primary); font-size: 32rpx; }

.rec-item { display: flex; gap: 12rpx; font-size: 26rpx; line-height: 1.6; padding: 8rpx 0; border-bottom: 1rpx solid var(--color-border); }
.rec-num { background: var(--color-primary); color: #fff; border-radius: 50%; width: 36rpx; height: 36rpx; min-width: 36rpx; display: flex; align-items: center; justify-content: center; font-size: 20rpx; margin-top: 4rpx; }

.btn-group { position: fixed; bottom: 0; left: 0; right: 0; padding: 24rpx 32rpx 48rpx; background: #fff; box-shadow: 0 -2rpx 12rpx rgba(0,0,0,.06); }
```

- [ ] **Step 4：创建 result.js**

```javascript
// miniprogram/pages/result/result.js
const LEVEL_EMOJI = { '优秀': '🌟', '良好': '👍', '需加强关注': '💪' }

Page({
  data: {
    result: null,
    levelEmoji: '',
    loading: false,
  },

  onLoad() {
    const result = wx.getStorageSync('lastAssessmentResult')
    if (result) {
      this.setData({
        result,
        levelEmoji: LEVEL_EMOJI[result.overall_level] || '📊',
      })
    }
  },

  async generatePlan() {
    this.setData({ loading: true })
    wx.showLoading({ title: '正在生成计划...' })
    try {
      const app = getApp()
      const child = app.globalData.currentChild
      const scores = wx.getStorageSync('lastAssessmentScores')
      const result = this.data.result

      const res = await wx.cloud.callFunction({
        name: 'generatePlan',
        data: {
          childProfile: { ...child, interests: [], concerns: [] },
          assessmentResult: result,
          duration: '3个月',
        },
      })

      if (res.result.code !== 0) throw new Error(res.result.message)
      const plan = res.result.data

      // 存入数据库
      const db = wx.cloud.database()
      const savedPlan = await db.collection('plans').add({
        data: {
          childId: child?._id || '',
          ...plan,
          currentWeek: 1,
          createdAt: db.serverDate(),
        },
      })

      wx.setStorageSync('lastPlan', plan)
      wx.switchTab({ url: '/pages/plan/plan' })
    } catch (err) {
      wx.showToast({ title: '生成失败，请重试', icon: 'none' })
      console.error(err)
    } finally {
      wx.hideLoading()
      this.setData({ loading: false })
    }
  },

  goBack() {
    wx.navigateBack()
  },
})
```

- [ ] **Step 5：Commit**

```bash
git add miniprogram/pages/result/
git commit -m "feat: add assessment result page with strengths/improvements/recommendations"
```

---

### Task 9：计划页（成长时间轴）

**Files:**
- Create: `miniprogram/pages/plan/plan.json`
- Create: `miniprogram/pages/plan/plan.wxml`
- Create: `miniprogram/pages/plan/plan.wxss`
- Create: `miniprogram/pages/plan/plan.js`

- [ ] **Step 1：创建 plan.json**

```json
{
  "navigationBarTitleText": "我的计划",
  "usingComponents": {
    "van-tabs": "@vant/weapp/tabs/index",
    "van-tab": "@vant/weapp/tab/index",
    "van-button": "@vant/weapp/button/index"
  }
}
```

- [ ] **Step 2：创建 plan.wxml**

```xml
<!-- miniprogram/pages/plan/plan.wxml -->
<view wx:if="{{!plan}}" class="empty">
  <view class="empty-icon">📅</view>
  <view class="empty-text">还没有计划</view>
  <view class="empty-sub">完成能力评估后生成计划</view>
  <van-button type="primary" round custom-style="margin-top: 32rpx; width: 300rpx;" bindclick="goAssessment">
    去评估
  </van-button>
</view>

<view wx:else class="container">
  <van-tabs active="{{activeTab}}" bind:change="onTabChange" color="#52C41A" title-active-color="#52C41A">
    <van-tab title="计划">
      <!-- 时间轴 -->
      <view class="timeline">
        <view
          class="tl-item {{index < currentWeek ? 'tl-item--done' : ''}} {{index === currentWeek - 1 ? 'tl-item--current' : ''}}"
          wx:for="{{plan.weekly_goals}}"
          wx:key="index"
          bindtap="toggleWeek"
          data-index="{{index}}"
        >
          <view class="tl-line-wrap">
            <view class="tl-dot"></view>
            <view class="tl-line" wx:if="{{index < plan.weekly_goals.length - 1}}"></view>
          </view>
          <view class="tl-content">
            <view class="tl-week">第 {{index + 1}} 周</view>
            <view class="tl-goal">{{item}}</view>
            <!-- 展开的每日活动 -->
            <view class="tl-activities" wx:if="{{expandedWeek === index}}">
              <view class="activity-item" wx:for="{{plan.daily_activities}}" wx:for-item="act" wx:key="time">
                <view class="act-time">{{act.time}}</view>
                <view class="act-detail">
                  <view class="act-name">{{act.activity}}</view>
                  <view class="act-goal">目标：{{act.goal}}</view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </van-tab>

    <van-tab title="资源">
      <view class="res-list">
        <view class="res-item" wx:for="{{plan.resources}}" wx:key="*this">
          <text class="res-dot">📌</text><text>{{item}}</text>
        </view>
      </view>
    </van-tab>

    <van-tab title="家长贴士">
      <view class="tips-list">
        <view class="tip-item" wx:for="{{plan.parent_tips}}" wx:key="*this">
          <text class="tip-num">{{index + 1}}</text>
          <text>{{item}}</text>
        </view>
      </view>
    </van-tab>
  </van-tabs>
</view>
```

- [ ] **Step 3：创建 plan.wxss**

```css
/* miniprogram/pages/plan/plan.wxss */
.empty { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; }
.empty-icon { font-size: 100rpx; margin-bottom: 24rpx; }
.empty-text { font-size: 32rpx; font-weight: 600; margin-bottom: 8rpx; }
.empty-sub { font-size: 26rpx; color: var(--color-text-sub); }

.container { padding-bottom: 40rpx; }

/* 时间轴 */
.timeline { padding: 32rpx 24rpx; }
.tl-item { display: flex; gap: 16rpx; margin-bottom: 0; }
.tl-line-wrap { display: flex; flex-direction: column; align-items: center; width: 28rpx; }
.tl-dot { width: 24rpx; height: 24rpx; border-radius: 50%; background: var(--color-primary-mid); border: 3rpx solid var(--color-primary-mid); flex-shrink: 0; margin-top: 8rpx; }
.tl-line { flex: 1; width: 4rpx; background: var(--color-primary-mid); margin: 4rpx 0; min-height: 60rpx; }

.tl-item--done .tl-dot { background: var(--color-primary); border-color: var(--color-primary); }
.tl-item--done .tl-line { background: var(--color-primary); }
.tl-item--current .tl-dot { background: var(--color-primary); border-color: #fff; box-shadow: 0 0 0 4rpx var(--color-primary); }

.tl-content { flex: 1; padding-bottom: 28rpx; }
.tl-week { font-size: 22rpx; color: var(--color-text-sub); margin-bottom: 6rpx; }
.tl-goal { font-size: 28rpx; font-weight: 600; color: var(--color-text); line-height: 1.4; }

.tl-activities { margin-top: 16rpx; background: var(--color-primary-light); border-radius: 16rpx; padding: 16rpx; }
.activity-item { display: flex; gap: 12rpx; padding: 10rpx 0; border-bottom: 1rpx solid var(--color-primary-mid); }
.activity-item:last-child { border: none; }
.act-time { background: var(--color-primary); color: #fff; border-radius: 8rpx; padding: 4rpx 10rpx; font-size: 20rpx; white-space: nowrap; height: fit-content; }
.act-name { font-size: 26rpx; font-weight: 500; }
.act-goal { font-size: 22rpx; color: var(--color-text-sub); }

/* 资源 & 贴士 */
.res-list, .tips-list { padding: 24rpx 32rpx; }
.res-item { display: flex; gap: 12rpx; font-size: 28rpx; line-height: 1.6; padding: 12rpx 0; border-bottom: 1rpx solid var(--color-border); }
.tip-item { display: flex; gap: 12rpx; font-size: 28rpx; line-height: 1.6; padding: 12rpx 0; border-bottom: 1rpx solid var(--color-border); }
.tip-num { background: var(--color-primary); color: #fff; border-radius: 50%; width: 40rpx; height: 40rpx; min-width: 40rpx; display: flex; align-items: center; justify-content: center; font-size: 22rpx; margin-top: 4rpx; }
```

- [ ] **Step 4：创建 plan.js**

```javascript
// miniprogram/pages/plan/plan.js
Page({
  data: {
    plan: null,
    activeTab: 0,
    currentWeek: 1,
    expandedWeek: null,
  },

  onShow() {
    const plan = wx.getStorageSync('lastPlan')
    if (plan) this.setData({ plan })
  },

  onTabChange(e) {
    this.setData({ activeTab: e.detail.index })
  },

  toggleWeek(e) {
    const index = e.currentTarget.dataset.index
    this.setData({
      expandedWeek: this.data.expandedWeek === index ? null : index,
    })
  },

  goAssessment() {
    wx.switchTab({ url: '/pages/assessment/assessment' })
  },
})
```

- [ ] **Step 5：在模拟器中验证**

- [ ] 无计划时显示空状态，点击"去评估"跳转
- [ ] 有计划时显示时间轴，当前周高亮
- [ ] 点击周展开每日活动
- [ ] Tab 切换到"资源"和"家长贴士"正常

- [ ] **Step 6：Commit**

```bash
git add miniprogram/pages/plan/
git commit -m "feat: add plan page with weekly timeline and expandable activities"
```

---

### Task 10：问答页

**Files:**
- Create: `miniprogram/pages/chat/chat.json`
- Create: `miniprogram/pages/chat/chat.wxml`
- Create: `miniprogram/pages/chat/chat.wxss`
- Create: `miniprogram/pages/chat/chat.js`

- [ ] **Step 1：创建 chat.json**

```json
{
  "navigationBarTitleText": "问答咨询",
  "usingComponents": {
    "van-field": "@vant/weapp/field/index",
    "van-button": "@vant/weapp/button/index",
    "van-loading": "@vant/weapp/loading/index"
  }
}
```

- [ ] **Step 2：创建 chat.wxml**

```xml
<!-- miniprogram/pages/chat/chat.wxml -->
<view class="container">
  <!-- FAQ 快捷标签 -->
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

  <!-- 对话区 -->
  <scroll-view scroll-y class="chat-scroll" scroll-into-view="{{scrollToId}}">
    <view class="chat-list">
      <view
        class="bubble-wrap {{item.role === 'user' ? 'bubble-wrap--user' : 'bubble-wrap--ai'}}"
        wx:for="{{messages}}"
        wx:key="id"
        id="msg-{{item.id}}"
      >
        <view class="avatar" wx:if="{{item.role === 'ai'}}">🌱</view>
        <view class="bubble {{item.role === 'user' ? 'bubble--user' : 'bubble--ai'}}">
          {{item.content}}
        </view>
        <view class="avatar-user" wx:if="{{item.role === 'user'}}">👤</view>
      </view>

      <!-- 思考中动效 -->
      <view class="bubble-wrap bubble-wrap--ai" wx:if="{{thinking}}">
        <view class="avatar">🌱</view>
        <view class="bubble bubble--ai bubble--thinking">
          <van-loading size="20px" color="#52C41A" /> 小桥正在思考...
        </view>
      </view>
    </view>
  </scroll-view>

  <!-- 输入区 -->
  <view class="input-bar">
    <van-field
      value="{{inputMsg}}"
      bind:change="onInput"
      placeholder="输入问题..."
      custom-class="input-field"
    />
    <van-button
      type="primary"
      round
      size="small"
      bindclick="sendMessage"
      disabled="{{!inputMsg || thinking}}"
    >发送</van-button>
  </view>
</view>
```

- [ ] **Step 3：创建 chat.wxss**

```css
/* miniprogram/pages/chat/chat.wxss */
.container { display: flex; flex-direction: column; height: 100vh; }

.faq-scroll { background: #fff; border-bottom: 1rpx solid var(--color-border); flex-shrink: 0; }
.faq-wrap { display: flex; gap: 16rpx; padding: 16rpx 24rpx; white-space: nowrap; }
.faq-tag {
  display: inline-block;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  border: 2rpx solid var(--color-primary-mid);
  border-radius: 32rpx;
  padding: 10rpx 24rpx;
  font-size: 24rpx;
  white-space: nowrap;
}

.chat-scroll { flex: 1; overflow: hidden; }
.chat-list { padding: 24rpx 24rpx 24rpx; }

.bubble-wrap { display: flex; align-items: flex-end; gap: 12rpx; margin-bottom: 24rpx; }
.bubble-wrap--user { flex-direction: row-reverse; }

.avatar { font-size: 48rpx; flex-shrink: 0; }
.avatar-user { font-size: 48rpx; flex-shrink: 0; }

.bubble {
  max-width: 70%;
  padding: 20rpx 24rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  line-height: 1.6;
}
.bubble--ai { background: #fff; border-bottom-left-radius: 4rpx; color: var(--color-text); }
.bubble--user { background: var(--color-primary); color: #fff; border-bottom-right-radius: 4rpx; }
.bubble--thinking { display: flex; align-items: center; gap: 12rpx; color: var(--color-text-sub); }

.input-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx 48rpx;
  background: #fff;
  border-top: 1rpx solid var(--color-border);
  flex-shrink: 0;
}
.input-field { flex: 1; }
```

- [ ] **Step 4：创建 chat.js**

```javascript
// miniprogram/pages/chat/chat.js
const FAQS = [
  '需要提前学拼音吗？',
  '孩子注意力不集中怎么办？',
  '如何培养时间观念？',
  '孩子不想去小学怎么办？',
]

Page({
  data: {
    faqs: FAQS,
    messages: [],
    inputMsg: '',
    thinking: false,
    scrollToId: '',
    msgCounter: 0,
  },

  onInput(e) {
    this.setData({ inputMsg: e.detail })
  },

  sendFaq(e) {
    this.setData({ inputMsg: e.currentTarget.dataset.msg })
    this.sendMessage()
  },

  async sendMessage() {
    const text = this.data.inputMsg.trim()
    if (!text) return

    const userMsg = { id: this.data.msgCounter, role: 'user', content: text }
    const newCounter = this.data.msgCounter + 1
    const history = this.data.messages
      .slice(-6)
      .map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))

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
        data: { message: text, history },
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

- [ ] **Step 5：在模拟器中验证**

- [ ] FAQ 标签横向滚动，点击发送
- [ ] 用户气泡右侧绿色，AI 气泡左侧白色
- [ ] 发送时显示"思考中"动效
- [ ] 对话区自动滚动到最新消息

- [ ] **Step 6：Commit**

```bash
git add miniprogram/pages/chat/
git commit -m "feat: add chat page with bubble UI and FAQ shortcuts"
```

---

## Phase 7：孩子档案与籍贯

### Task 11：孩子信息录入（评估前置步骤）

**Files:**
- Modify: `miniprogram/pages/assessment/assessment.js`
- Modify: `miniprogram/pages/assessment/assessment.wxml`

- [ ] **Step 1：在评估页顶部加孩子信息采集弹窗**

在 `assessment.wxml` 的 `<van-popup>` 之前添加孩子信息弹窗：

```xml
<!-- 孩子信息弹窗（首次进入时展示） -->
<van-popup
  show="{{showChildSetup}}"
  position="bottom"
  round
  custom-style="padding: 40rpx 32rpx 80rpx;"
>
  <view class="popup-title">先告诉我关于孩子的信息</view>
  <van-field label="孩子姓名" value="{{form.name}}" bind:change="onFormChange" data-key="name" placeholder="请输入" />
  <van-field label="年龄" value="{{form.age}}" bind:change="onFormChange" data-key="age" placeholder="如：5.5" type="digit" />
  <van-field label="籍贯" value="{{form.hometown}}" bind:change="onFormChange" data-key="hometown" placeholder="如：浙江省杭州市" />
  <van-button type="primary" block round custom-style="margin-top: 32rpx;" bindclick="saveChildInfo">
    开始评估
  </van-button>
</van-popup>
```

- [ ] **Step 2：在 assessment.js 中添加孩子信息逻辑**

在 `data` 中添加：

```javascript
showChildSetup: false,
form: { name: '', age: '', hometown: '' },
```

在 `onLoad` 中检查是否已有档案：

```javascript
onLoad() {
  const app = getApp()
  if (!app.globalData.currentChild) {
    this.setData({ showChildSetup: true })
  } else {
    const child = app.globalData.currentChild
    this.setData({ childName: child.name, childAge: child.age })
  }
},

onFormChange(e) {
  const key = e.currentTarget.dataset.key
  this.setData({ [`form.${key}`]: e.detail })
},

async saveChildInfo() {
  const { name, age, hometown } = this.data.form
  if (!name) return wx.showToast({ title: '请输入孩子姓名', icon: 'none' })
  const child = { name, age: parseFloat(age) || 5.5, hometown }
  const db = wx.cloud.database()
  const res = await db.collection('children').add({ data: { ...child, createdAt: db.serverDate() } })
  child._id = res._id
  getApp().globalData.currentChild = child
  this.setData({ showChildSetup: false, childName: name, childAge: child.age })
},
```

- [ ] **Step 3：Commit**

```bash
git add miniprogram/pages/assessment/
git commit -m "feat: add child profile setup with hometown field before assessment"
```

---

## Phase 8：部署与集成验证

### Task 12：部署云函数并配置环境变量

- [ ] **Step 1：为 chat 和 analyzeDeep 云函数设置环境变量**

在 CloudBase 控制台 → wenwen2code → 云函数 → 分别为 chat、analyzeDeep 设置：

```
SILICONFLOW_API_KEY = sk-tivkaulejqfzawrpfdtkxaruhxpafomtvxzesbtahjpdeupa
```

- [ ] **Step 2：CloudBase 数据库创建集合**

在 CloudBase 控制台 → 数据库，创建以下集合（权限均设为"仅创建者可读写"）：

- `children`
- `assessments`
- `plans`

- [ ] **Step 3：端到端流程验证（微信开发者工具模拟器）**

按顺序验证：
- [ ] 首次进入评估页，弹出孩子信息填写
- [ ] 填写姓名、年龄、籍贯并保存
- [ ] 完成 8 张维度卡片评分
- [ ] 点击"查看评估结果"，结果页正常展示
- [ ] 点击"生成个性化计划"，等待 5-10 秒后跳转计划页
- [ ] 计划页时间轴显示，点击第 1 周展开每日活动
- [ ] 问答页发送 FAQ 问题，收到 AI 回复

- [ ] **Step 4：上传代码到微信审核**

在微信开发者工具中：上传 → 填写版本号（0.1.0）和备注 → 提交

- [ ] **Step 5：最终 Commit**

```bash
git add .
git commit -m "feat: complete WeChat miniprogram MVP - all pages and cloud functions"
```

---

## Self-Review

**Spec 覆盖检查：**

| Spec 要求 | 对应 Task |
|------|------|
| 原生 WXML + Vant Weapp | Task 1, 6-10 |
| CloudBase Node.js 云函数 × 4 | Task 2-5 |
| assessment.py 移植为 JS，附单测 | Task 2 |
| 知识库全文嵌入（无 RAG） | Task 3 |
| fallback_qa.json 降级 | Task 4 |
| 图卡总览评估交互 | Task 7 |
| 成长时间轴计划展示 | Task 9 |
| 问答气泡 + FAQ | Task 10 |
| 孩子籍贯字段 + 政策注入 | Task 3, 11 |
| 进阶分析（≥2次评估） | Task 5 |
| CloudBase 数据库 3 个集合 | Task 12 |
| 部署至 wenwen2code 环境 | Task 5, 12 |

**无 TBD 或占位符** ✓  
**类型一致性** ✓（`scores` 结构在 assessment-logic.js、assessment.js、generatePlan/index.js 中完全一致）  
**函数名一致性** ✓（`calculateAssessment`、`getDefaultPlan`、`fallbackAnswer` 定义与调用一致）
