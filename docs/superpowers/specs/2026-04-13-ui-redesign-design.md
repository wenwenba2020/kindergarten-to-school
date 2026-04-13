# UI 改版设计方案：KA Kids 风格

**日期：** 2026-04-13  
**项目：** 小桥 微信小程序  
**分支：** feat/wechat-miniprogram

---

## 背景

当前设计风格偏素，与面向家长+儿童的幼小衔接主题不够匹配。目标参考 Khan Academy Kids 的设计语言：圆润大字体 + 鲜艳撞色 + 插画卡片风格，整体活泼友好。

---

## 一、全局色彩系统（app.wxss）

### 新色板

| CSS 变量 | 值 | 用途 |
|----------|-----|------|
| `--color-primary` | `#4CAF50` | 首页/导航绿 |
| `--color-orange` | `#FF8C42` | 评估功能专属色、tabBar 选中色 |
| `--color-yellow` | `#FFD166` | 计划功能专属色 |
| `--color-purple` | `#9B5DE5` | 问答功能专属色 |
| `--color-primary-light` | `#F1F8E9` | 浅绿背景 |
| `--radius-card` | `32rpx` | 卡片圆角（从 16rpx 加大） |
| `--font-title` | `36rpx` | 标题字号 |

### 全局排版
- 全局 `font-size`：从 28rpx → 30rpx
- 标题 `font-weight`：800
- 行高：1.7

### tabBar
- `selectedColor`：`#FF8C42`（橙）
- `backgroundColor`：`#FFFDF5`（暖白）
- `borderStyle`：`white`

---

## 二、首页改版（home.wxml + home.wxss）

### Hero 区
- **改前：** 绿色大横幅（🌱 emoji + "小桥" + "幼小衔接规划助手" 副标题），高约 240rpx
- **改后：** 紧凑彩色标题栏，高约 120rpx
  - 背景：绿色渐变（`#4CAF50` → `#66BB6A`）
  - 文字：**"幼小衔接家长助手"**，34rpx，白色，`font-weight: 800`，居中
  - 无 emoji，无副标题

### 功能卡片（三张）

| 卡片 | 专属色 | 视觉处理 |
|------|--------|---------|
| 能力评估 | 橙 `#FF8C42` | 白底卡片，左侧 8rpx 橙色竖条，icon 用橙色圆形色块 |
| 个性化计划 | 黄 `#FFD166` | 白底卡片，左侧 8rpx 黄色竖条，icon 用黄色圆形色块 |
| 问答咨询 | 紫 `#9B5DE5` | 白底卡片，左侧 8rpx 紫色竖条，icon 用紫色圆形色块 |

卡片圆角 32rpx，icon 替换为对应颜色圆形色块内的文字/符号（去掉直接 emoji）。

### 使用步骤区
- 背景：暖黄 `#FFF9E6`，圆角 32rpx
- 步骤序号：橙色圆形数字徽章（24rpx 直径）
- 标题文字加粗

---

## 三、TabBar 图标（ComfyUI 生成）

### 规格
- 尺寸：81×81px，PNG，白色背景（微信 tabBar 要求）
- 大小：≤ 40KB
- 生成服务：`http://100.90.137.80:8188/prompt`（POST，z-image-turbo 模型）

### 四个图标主题

| Tab | 文件 | Prompt 主题 |
|-----|------|------------|
| 首页 | `tab-home-active.png` | cute house with green roof, flat icon style |
| 评估 | `tab-assess-active.png` | cute clipboard with orange star, flat icon style |
| 计划 | `tab-plan-active.png` | cute calendar with yellow sun, flat icon style |
| 问答 | `tab-chat-active.png` | cute speech bubble with purple heart, flat icon style |

### 生成策略
1. 先生成4个彩色选中态图标
2. 灰色默认态：对彩色图标做代码去饱和处理（Python/PIL）
3. 写入 `miniprogram/images/` 覆盖现有占位图

### Prompt 模板
```
cute flat icon, {主题}, kawaii style, bold outline, 
white background, vibrant colors, simple shape, 
children app icon, no text, centered composition
```

---

## 四、改动文件清单

| 文件 | 改动 |
|------|------|
| `miniprogram/app.wxss` | 新增颜色变量，更新全局字体/圆角 |
| `miniprogram/app.json` | tabBar selectedColor、backgroundColor |
| `miniprogram/pages/home/home.wxml` | Hero 区文字、卡片结构 |
| `miniprogram/pages/home/home.wxss` | 全部样式重写 |
| `miniprogram/images/tab-*.png` | 8 个图标文件（4选中 + 4默认） |

---

## 五、不改动的内容

- 所有业务逻辑（JS 文件）
- 评估、结果、计划、问答内页样式（本次只改首页和全局）
- 云函数
- 路由和 tabBar 页面路径

---

## 六、成功标准

- [ ] 首页 hero 为紧凑标题栏，显示"幼小衔接家长助手"
- [ ] 三个功能卡片各有专属颜色左竖条
- [ ] tabBar 4 个图标为插画风，选中态彩色，默认态灰色
- [ ] 全局圆角、字体更新生效
- [ ] 微信开发者工具模拟器无报错
