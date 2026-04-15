# 次数显示优化 + 字体放大 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复聊天次数不扣减的 Bug，在首页/评估页/聊天页醒目展示月度额度，并全局放大字体以适配手机屏幕。

**Architecture:** 纯前端改动，不涉及云函数。修复 chat.js 的 catch 块未更新 remain 的 Bug，并在 onShow 刷新额度；首页 home.js 在 onShow 拉取两项额度后注入 badge；字体改动集中在各页 wxss 和 app.wxss。

**Tech Stack:** 微信小程序原生（WXML / WXSS / JS），Vant Weapp 组件库，wx.cloud.callFunction

---

## 文件清单

| 操作 | 文件 | 内容 |
|------|------|------|
| Modify | `miniprogram/pages/chat/chat.js` | 修复 Bug：catch 块扣 remain，onShow 刷新额度 |
| Modify | `miniprogram/pages/chat/chat.wxml` | quota-bar 加更清晰的额度说明 |
| Modify | `miniprogram/pages/chat/chat.wxss` | 放大字体，加强 quota-bar 视觉 |
| Modify | `miniprogram/pages/assessment/assessment.wxml` | 额度 banner 替代小 tag |
| Modify | `miniprogram/pages/assessment/assessment.wxss` | 新 banner 样式，放大字体 |
| Modify | `miniprogram/pages/home/home.js` | onShow 拉取两项额度 |
| Modify | `miniprogram/pages/home/home.wxml` | 功能卡片加额度 badge |
| Modify | `miniprogram/pages/home/home.wxss` | badge 样式 |
| Modify | `miniprogram/app.wxss` | 全局字体基准上调 |

---

## Task 1：修复聊天次数扣减 Bug

**Files:**
- Modify: `miniprogram/pages/chat/chat.js`

### 问题
1. `sendMessage()` 的 `catch` 块未更新 `remain`：云函数在 LLM 调用前已消耗 slot，但前端 UI 未同步。
2. `onShow()` 不刷新额度：切回聊天页时显示旧值。

- [ ] **Step 1: 修复 catch 块——本地扣减 remain**

打开 `miniprogram/pages/chat/chat.js`，找到 `sendMessage` 方法的 `catch` 块（约第 95-99 行），将：

```js
    } catch (err) {
      const aiMsg = { id: newCounter, role: 'ai', content: '网络异常，请检查连接后重试。' }
      this.setData({ messages: [...this.data.messages, aiMsg] })
    } finally {
```

替换为：

```js
    } catch (err) {
      const aiMsg = { id: newCounter, role: 'ai', content: '网络异常，请检查连接后重试。' }
      // 云函数已在服务端消耗 slot，本地同步扣减
      const remain = Math.max(0, this.data.remain - 1)
      this.setData({ messages: [...this.data.messages, aiMsg], remain })
    } finally {
```

- [ ] **Step 2: 在 onShow 刷新额度**

找到 `onShow()` 方法（约第 52-54 行），将：

```js
  onShow() {
    this.refreshContext()
  },
```

替换为：

```js
  onShow() {
    this.refreshContext()
    this.loadQuota()
  },
```

- [ ] **Step 3: 在微信开发者工具中验证**

打开聊天页，确认：
1. 初始额度显示正确（如"还可提问 5 次"）
2. 发送一条消息后，次数变为 4
3. 点击 FAQ 预设问题后，次数也减少
4. 切走再切回聊天页，次数仍显示正确值（不重置为 5）

- [ ] **Step 4: Commit**

```bash
cd /Users/robertzf/cc_workspace/kindergarten_to_school
git add miniprogram/pages/chat/chat.js
git commit -m "fix: sync chat remain in catch block and refresh on onShow"
```

---

## Task 2：聊天页 quota-bar 视觉强化 + 字体放大

**Files:**
- Modify: `miniprogram/pages/chat/chat.wxml`
- Modify: `miniprogram/pages/chat/chat.wxss`

### 目标
- quota-bar 字体从 24rpx 提升到 28rpx，余量数字加大到 36rpx
- 气泡正文从 28rpx → 32rpx
- FAQ 标签从 24rpx → 28rpx
- 输入框提示文字无法直接控制，可接受

- [ ] **Step 1: 更新 chat.wxml 的 quota-bar**

找到 quota-bar 块（约第 13-17 行），将：

```xml
    <!-- 限额提示 -->
    <view class="quota-bar">
      <text class="quota-icon">💬</text>
      <text class="quota-text" wx:if="{{remain > 0}}">本月还可提问 <text class="quota-num">{{remain}}</text> 次</text>
      <text class="quota-text quota-text--empty" wx:else>本月提问次数已用完，下月自动重置</text>
    </view>
```

替换为：

```xml
    <!-- 限额提示 -->
    <view class="quota-bar">
      <view class="quota-bar-left">
        <text class="quota-icon">💬</text>
        <view>
          <text class="quota-label">本月问答额度</text>
          <view wx:if="{{remain > 0}}" class="quota-detail">
            <text class="quota-num">{{remain}}</text>
            <text class="quota-of"> / 5 次</text>
          </view>
          <text class="quota-detail quota-text--empty" wx:else>已用完，下月自动重置</text>
        </view>
      </view>
    </view>
```

- [ ] **Step 2: 更新 chat.wxss**

用以下内容完整替换 `miniprogram/pages/chat/chat.wxss`：

```css
.container { display: flex; flex-direction: column; height: 100vh; }
.faq-scroll { background: #fff; border-bottom: 1rpx solid var(--color-border); flex-shrink: 0; }
.faq-wrap { display: flex; gap: 16rpx; padding: 16rpx 24rpx; white-space: nowrap; }
.faq-tag { display: inline-block; background: var(--color-primary-light); color: var(--color-primary-dark); border: 2rpx solid var(--color-primary-mid); border-radius: 32rpx; padding: 12rpx 28rpx; font-size: 28rpx; white-space: nowrap; }
.chat-scroll { flex: 1; overflow: hidden; }
.chat-list { padding: 24rpx; }
.bubble-wrap { display: flex; align-items: flex-end; gap: 12rpx; margin-bottom: 24rpx; }
.bubble-wrap--user { flex-direction: row-reverse; }
.avatar { font-size: 48rpx; flex-shrink: 0; }
.avatar-user { font-size: 48rpx; flex-shrink: 0; }
.bubble { max-width: 70%; padding: 22rpx 26rpx; border-radius: 24rpx; font-size: 32rpx; line-height: 1.7; }
.bubble--ai { background: #fff; border-bottom-left-radius: 4rpx; color: var(--color-text); }
.bubble--user { background: var(--color-primary); color: #fff; border-bottom-right-radius: 4rpx; }
.bubble--thinking { display: flex; align-items: center; gap: 12rpx; color: var(--color-text-sub); }
.disclaimer-bar { padding: 10rpx 24rpx; background: #FFF8E1; border-top: 1rpx solid #FFE082; font-size: 22rpx; color: #8D6E63; line-height: 1.6; flex-shrink: 0; }
.input-bar { display: flex; align-items: center; gap: 16rpx; padding: 16rpx 24rpx 48rpx; background: #fff; border-top: 1rpx solid var(--color-border); flex-shrink: 0; }
.input-field { flex: 1; }

/* Quota bar */
.quota-bar { display: flex; align-items: center; gap: 12rpx; padding: 18rpx 24rpx; background: var(--color-yellow-light); border-bottom: 2rpx solid #FFE082; flex-shrink: 0; }
.quota-bar-left { display: flex; align-items: center; gap: 16rpx; }
.quota-icon { font-size: 36rpx; flex-shrink: 0; }
.quota-label { font-size: 24rpx; color: var(--color-text-sub); display: block; margin-bottom: 4rpx; }
.quota-detail { display: flex; align-items: baseline; gap: 4rpx; }
.quota-num { color: var(--color-orange); font-weight: 800; font-size: 40rpx; line-height: 1; }
.quota-of { font-size: 26rpx; color: var(--color-text-sub); }
.quota-text--empty { font-size: 26rpx; color: #e57373; }

/* Gate card */
.gate-card { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; padding: 80rpx 48rpx; text-align: center; }
.gate-icon { font-size: 96rpx; margin-bottom: 32rpx; }
.gate-title { font-size: 40rpx; font-weight: 600; color: var(--color-text); margin-bottom: 16rpx; }
.gate-desc { font-size: 32rpx; color: var(--color-text-sub); line-height: 1.6; margin-bottom: 48rpx; }
.gate-btn { background: var(--color-orange); color: #fff; border-radius: 48rpx; padding: 24rpx 64rpx; font-size: 34rpx; font-weight: 600; }
```

- [ ] **Step 3: 在开发者工具预览聊天页**

确认：
- quota-bar 显示"本月问答额度 **5** / 5 次"，数字醒目
- 气泡文字明显变大
- FAQ 标签文字变大

- [ ] **Step 4: Commit**

```bash
git add miniprogram/pages/chat/chat.wxml miniprogram/pages/chat/chat.wxss
git commit -m "feat: enhance chat quota bar visibility and increase font sizes"
```

---

## Task 3：评估页额度 banner 强化 + 字体放大

**Files:**
- Modify: `miniprogram/pages/assessment/assessment.wxml`
- Modify: `miniprogram/pages/assessment/assessment.wxss`

### 目标
- 将小灰 tag 升级为独立 banner，与进度条并列显示
- 字体：题目文字 26→30rpx，选项按钮 26→30rpx

- [ ] **Step 1: 更新 assessment.wxml 的额度显示**

找到 child-info 卡片部分（约第 11-17 行），将：

```xml
  <view class="child-info card" wx:if="{{childName}}">
    <text class="child-info-text">🌱 正在评估：{{childName}}，{{childAgeDisplay}}</text>
    <view style="display:flex;align-items:center;gap:12rpx;flex-shrink:0;">
      <text wx:if="{{assessRemain !== null}}" class="remain-tag">本月剩余 {{assessRemain}} 次</text>
      <view class="child-info-edit" bindtap="editChildInfo">修改</view>
    </view>
  </view>
```

替换为：

```xml
  <view class="child-info card" wx:if="{{childName}}">
    <text class="child-info-text">🌱 正在评估：{{childName}}，{{childAgeDisplay}}</text>
    <view class="child-info-edit" bindtap="editChildInfo">修改</view>
  </view>

  <!-- 评估额度 banner -->
  <view class="assess-quota-bar card" wx:if="{{childName && assessRemain !== null}}">
    <view class="assess-quota-left">
      <text class="assess-quota-icon">📋</text>
      <view>
        <text class="assess-quota-label">本月评估额度</text>
        <view wx:if="{{assessRemain > 0}}" class="assess-quota-detail">
          <text class="assess-quota-num">{{assessRemain}}</text>
          <text class="assess-quota-of"> / {{assessLimit}} 次</text>
        </view>
        <text wx:else class="assess-quota-empty">本月已用完，下月自动重置</text>
      </view>
    </view>
  </view>
```

- [ ] **Step 2: 更新 assessment.wxss**

用以下内容完整替换 `miniprogram/pages/assessment/assessment.wxss`：

```css
.container { padding-bottom: 160rpx; }
.progress-bar { padding: 24rpx 32rpx 16rpx; background: #fff; }
.progress-label { font-size: 26rpx; color: var(--color-text-sub); margin-bottom: 12rpx; }
.progress-track { height: 8rpx; background: var(--color-primary-mid); border-radius: 4rpx; }
.progress-fill { height: 8rpx; background: var(--color-primary); border-radius: 4rpx; transition: width 0.3s; }
.child-info { margin: 16rpx 24rpx 0; padding: 20rpx 24rpx; font-size: 28rpx; color: var(--color-primary-dark); display: flex; align-items: center; justify-content: space-between; }
.child-info-text { flex: 1; }
.child-info-edit { font-size: 26rpx; color: var(--color-primary); padding: 6rpx 16rpx; border: 1rpx solid var(--color-primary); border-radius: 24rpx; flex-shrink: 0; }

/* 评估额度 banner */
.assess-quota-bar { margin: 12rpx 24rpx 0; padding: 20rpx 24rpx; }
.assess-quota-left { display: flex; align-items: center; gap: 16rpx; }
.assess-quota-icon { font-size: 36rpx; flex-shrink: 0; }
.assess-quota-label { font-size: 24rpx; color: var(--color-text-sub); display: block; margin-bottom: 4rpx; }
.assess-quota-detail { display: flex; align-items: baseline; gap: 4rpx; }
.assess-quota-num { color: var(--color-orange); font-weight: 800; font-size: 40rpx; line-height: 1; }
.assess-quota-of { font-size: 26rpx; color: var(--color-text-sub); }
.assess-quota-empty { font-size: 26rpx; color: #e57373; }

.dim-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20rpx; padding: 20rpx 24rpx; }
.dim-card { background: #fff; border-radius: 20rpx; padding: 32rpx 20rpx; text-align: center; border: 3rpx solid var(--color-border); position: relative; transition: all 0.2s; }
.dim-card--done { border-color: var(--color-primary); background: var(--color-primary-light); }
.dim-card--locked { opacity: 0.38; }
.dim-card--active-next { border-color: var(--color-primary-mid); box-shadow: 0 0 0 3rpx rgba(82,196,26,.25); }
.dim-check { position: absolute; top: 12rpx; right: 16rpx; font-size: 24rpx; }
.dim-lock { position: absolute; top: 12rpx; right: 16rpx; font-size: 22rpx; }
.dim-icon { font-size: 56rpx; margin-bottom: 12rpx; }
.dim-name { font-size: 28rpx; font-weight: 600; margin-bottom: 8rpx; }
.dim-score { font-size: 24rpx; color: var(--color-primary); }
.dim-score--pending { color: var(--color-text-sub); }
.dim-score--locked { color: var(--color-border); font-size: 22rpx; }

/* Phase badge */
.phase-badge { margin: 12rpx 24rpx 0; padding: 20rpx 24rpx; }
.phase-badge-text { font-size: 28rpx; font-weight: 600; color: var(--color-primary-dark); }
.phase-badge-text--child { color: #722ed1; }

/* Popup mode tag */
.popup-mode-tag { text-align: center; font-size: 24rpx; color: var(--color-primary-dark); background: var(--color-primary-light); border-radius: 24rpx; padding: 8rpx 24rpx; display: inline-block; margin: 0 auto 24rpx; width: fit-content; }
.bottom-btn { position: fixed; bottom: 0; left: 0; right: 0; padding: 24rpx 32rpx 48rpx; background: #fff; box-shadow: 0 -2rpx 12rpx rgba(0,0,0,.06); }
.popup-icon { font-size: 72rpx; text-align: center; margin-bottom: 16rpx; }
.popup-title { font-size: 36rpx; font-weight: 700; text-align: center; margin-bottom: 24rpx; }
.question-block { margin-bottom: 32rpx; }
.question-text { font-size: 30rpx; color: var(--color-text); line-height: 1.7; margin-bottom: 16rpx; font-weight: 500; }
.option-btn { display: block; padding: 24rpx 24rpx; border: 2rpx solid var(--color-border); border-radius: 16rpx; font-size: 30rpx; color: var(--color-text); margin-bottom: 12rpx; background: #fff; line-height: 1.6; }
.option-btn--selected { border-color: var(--color-primary); background: var(--color-primary-light); color: var(--color-primary-dark); }
```

- [ ] **Step 3: 在开发者工具预览评估页**

确认：
- 进入评估页，child-info 卡片下方显示"本月评估额度 **3** / 3 次"
- 题目文字和选项文字明显变大
- 完成一次评估提交后，额度变为 2

- [ ] **Step 4: Commit**

```bash
git add miniprogram/pages/assessment/assessment.wxml miniprogram/pages/assessment/assessment.wxss
git commit -m "feat: add prominent assessment quota banner and increase font sizes"
```

---

## Task 4：首页功能卡片加额度 badge

**Files:**
- Modify: `miniprogram/pages/home/home.js`
- Modify: `miniprogram/pages/home/home.wxml`
- Modify: `miniprogram/pages/home/home.wxss`

### 目标
在"能力评估"和"问答咨询"卡片右侧显示"剩余 N 次"badge，onShow 时拉取最新值。

- [ ] **Step 1: 更新 home.js 拉取额度**

用以下内容完整替换 `miniprogram/pages/home/home.js`：

```js
Page({
  data: {
    assessRemain: null,
    chatRemain: null,
  },

  onShow() {
    this._loadQuotas()
  },

  async _loadQuotas() {
    try {
      const [assessRes, chatRes] = await Promise.all([
        wx.cloud.callFunction({ name: 'assessment', data: { action: 'getQuota' } }),
        wx.cloud.callFunction({ name: 'chat', data: { action: 'getQuota' } }),
      ])
      const assessRemain = assessRes.result?.data?.remain ?? null
      const chatRemain = chatRes.result?.data?.remain ?? null
      this.setData({ assessRemain, chatRemain })
    } catch {
      // 拉取失败时不显示 badge，不影响主流程
    }
  },

  goAssessment() { wx.switchTab({ url: '/pages/assessment/assessment' }) },
  goPlan() { wx.switchTab({ url: '/pages/plan/plan' }) },
  goChat() { wx.switchTab({ url: '/pages/chat/chat' }) },
  openWenwenlab() {
    wx.setClipboardData({
      data: 'https://wenwenlab.com',
      success: () => wx.showToast({ title: '网址已复制', icon: 'success' }),
    })
  },
})
```

- [ ] **Step 2: 更新 home.wxml 加 badge**

找到"能力评估"卡片（约第 11-22 行），将：

```xml
  <!-- 能力评估卡片（橙） -->
  <view class="menu-card" bindtap="goAssessment">
    <view class="card-accent" style="background:var(--color-orange)"></view>
    <view class="menu-icon-wrap" style="background:var(--color-orange-light)">
      <text class="menu-icon-emoji">📋</text>
    </view>
    <view class="menu-info">
      <view class="menu-name">能力评估</view>
      <view class="menu-desc">评估孩子8个维度发展水平</view>
    </view>
    <view class="menu-arrow">›</view>
  </view>
```

替换为：

```xml
  <!-- 能力评估卡片（橙） -->
  <view class="menu-card" bindtap="goAssessment">
    <view class="card-accent" style="background:var(--color-orange)"></view>
    <view class="menu-icon-wrap" style="background:var(--color-orange-light)">
      <text class="menu-icon-emoji">📋</text>
    </view>
    <view class="menu-info">
      <view class="menu-name">能力评估</view>
      <view class="menu-desc">评估孩子8个维度发展水平</view>
    </view>
    <view wx:if="{{assessRemain !== null}}" class="quota-badge {{assessRemain === 0 ? 'quota-badge--empty' : ''}}">
      <text>剩余</text>
      <text class="quota-badge-num">{{assessRemain}}</text>
      <text>次</text>
    </view>
    <view wx:else class="menu-arrow">›</view>
  </view>
```

找到"问答咨询"卡片（约第 36-47 行），将：

```xml
  <!-- 问答咨询卡片（紫） -->
  <view class="menu-card" bindtap="goChat">
    <view class="card-accent" style="background:var(--color-purple)"></view>
    <view class="menu-icon-wrap" style="background:var(--color-purple-light)">
      <text class="menu-icon-emoji">💬</text>
    </view>
    <view class="menu-info">
      <view class="menu-name">问答咨询</view>
      <view class="menu-desc">随时解答入学疑问</view>
    </view>
    <view class="menu-arrow">›</view>
  </view>
```

替换为：

```xml
  <!-- 问答咨询卡片（紫） -->
  <view class="menu-card" bindtap="goChat">
    <view class="card-accent" style="background:var(--color-purple)"></view>
    <view class="menu-icon-wrap" style="background:var(--color-purple-light)">
      <text class="menu-icon-emoji">💬</text>
    </view>
    <view class="menu-info">
      <view class="menu-name">问答咨询</view>
      <view class="menu-desc">随时解答入学疑问</view>
    </view>
    <view wx:if="{{chatRemain !== null}}" class="quota-badge quota-badge--purple {{chatRemain === 0 ? 'quota-badge--empty' : ''}}">
      <text>剩余</text>
      <text class="quota-badge-num">{{chatRemain}}</text>
      <text>次</text>
    </view>
    <view wx:else class="menu-arrow">›</view>
  </view>
```

- [ ] **Step 3: 更新 home.wxss 加 badge 样式**

在 `miniprogram/pages/home/home.wxss` 的 `.menu-arrow` 规则后面追加以下样式：

```css
/* 额度 badge */
.quota-badge {
  flex-shrink: 0;
  background: var(--color-orange-light);
  border: 2rpx solid var(--color-orange);
  border-radius: 28rpx;
  padding: 8rpx 18rpx;
  display: flex;
  align-items: baseline;
  gap: 4rpx;
  font-size: 22rpx;
  color: var(--color-orange);
  font-weight: 600;
  margin-right: 4rpx;
}
.quota-badge--purple {
  background: var(--color-purple-light);
  border-color: var(--color-purple);
  color: var(--color-purple);
}
.quota-badge--empty {
  background: #fce4e4;
  border-color: #e57373;
  color: #e57373;
}
.quota-badge-num {
  font-size: 30rpx;
  font-weight: 800;
}
```

- [ ] **Step 4: 在开发者工具预览首页**

确认：
- 首页"能力评估"卡片右侧显示橙色"剩余 3 次"badge
- "问答咨询"卡片右侧显示紫色"剩余 5 次"badge
- 额度为 0 时 badge 变红

- [ ] **Step 5: Commit**

```bash
git add miniprogram/pages/home/home.js miniprogram/pages/home/home.wxml miniprogram/pages/home/home.wxss
git commit -m "feat: show monthly quota badges on home page cards"
```

---

## Task 5：全局字体基准上调

**Files:**
- Modify: `miniprogram/app.wxss`

### 目标
将全局 `font-size` 从 `30rpx` 提升到 `32rpx`，并提升部分 CSS 变量。

- [ ] **Step 1: 更新 app.wxss**

打开 `miniprogram/app.wxss`，找到 `page { ... }` 块，将 `font-size: 30rpx;` 改为 `font-size: 32rpx;`，并将 `--font-title: 36rpx;` 改为 `--font-title: 40rpx;`：

完整替换 `page { ... }` 块为：

```css
page {
  --color-primary: #4CAF50;
  --color-primary-light: #F1F8E9;
  --color-primary-mid: #C8E6C9;
  --color-primary-dark: #388E3C;
  --color-orange: #FF8C42;
  --color-orange-light: #FFF3EB;
  --color-yellow: #FFD166;
  --color-yellow-light: #FFFBEB;
  --color-purple: #9B5DE5;
  --color-purple-light: #F3EBFF;
  --color-text: #333333;
  --color-text-sub: #888888;
  --color-border: #f0f0f0;
  --radius-card: 32rpx;
  --radius-btn: 40rpx;
  --font-title: 40rpx;

  background-color: #f5f5f5;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: var(--color-text);
  font-size: 32rpx;
  line-height: 1.7;
}
```

- [ ] **Step 2: 在开发者工具预览各页面**

切换首页、评估页、聊天页、计划页，确认整体字体大小舒适，没有布局溢出。

- [ ] **Step 3: Commit**

```bash
git add miniprogram/app.wxss
git commit -m "style: increase global base font size from 30rpx to 32rpx"
```

---

## Task 6：端到端验证 + 截图确认

- [ ] **Step 1: 截图各页面**

使用微信开发者工具的截图功能（或 `mp_screenshot`），检查：

| 页面 | 检查项 |
|------|--------|
| 首页 | 两个 badge 显示正确额度 |
| 评估页 | 额度 banner 在 child-info 下方显示 |
| 聊天页 | quota-bar 数字醒目，发送后实时减少 |
| 聊天页 | 点击 FAQ 标签后额度也减少 |
| 聊天页 | 切走再切回，显示正确值（不回到 5） |

- [ ] **Step 2: 创建 PR**

```bash
cd /Users/robertzf/cc_workspace/kindergarten_to_school
git push origin feat/wechat-miniprogram
```

然后在 GitHub 创建 PR，标题：`feat: 次数显示优化、Bug 修复、字体放大`。

---

## 自我审查

**Spec 覆盖检查：**
- ✅ 每月 3 次评估 / 5 次对话明确标识 → Task 2/3/4
- ✅ 使用后次数实时调整 → Task 1（Bug 修复）+ Task 2（onShow 刷新）
- ✅ FAQ 预设问题不减次数 Bug → Task 1 修复
- ✅ 输入框提问不减次数 Bug → Task 1 修复
- ✅ 字体整体放大 → Task 2/3/5

**Placeholder 检查：** 无 TBD / TODO。

**类型一致性：** `assessRemain`、`chatRemain` 命名在 home.js/wxml 中一致；`remain` 在 chat.js 中一致；`assessRemain`/`assessLimit` 在 assessment.js 中已有，新 wxml 引用与之一致。
