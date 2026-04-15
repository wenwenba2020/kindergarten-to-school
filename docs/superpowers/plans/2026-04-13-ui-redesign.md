# UI 改版实施计划：KA Kids 风格

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将"小桥"微信小程序改版为 Khan Academy Kids 风格：活泼圆润的多色系设计，含紧凑标题栏首页、彩色功能卡片、ComfyUI 生成的 tabBar 插画图标。

**Architecture:** 仅改动样式层（app.wxss、home.wxml/wxss、app.json）和图片资源，不触碰任何 JS 业务逻辑。图标生成用独立 Python 脚本调用本地 ComfyUI API，生成后直接覆盖 miniprogram/images/ 中的占位图。

**Tech Stack:** 微信小程序 WXML/WXSS、ComfyUI REST API（http://100.90.137.80:8188）、Python 3 + Pillow（图标下载+灰度处理）

---

## 文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `miniprogram/app.wxss` | 修改 | 新增颜色变量，更新全局字体/圆角 |
| `miniprogram/app.json` | 修改 | tabBar selectedColor、backgroundColor |
| `miniprogram/pages/home/home.wxml` | 修改 | Hero 区结构简化，卡片加彩色竖条 |
| `miniprogram/pages/home/home.wxss` | 修改 | 全部样式重写 |
| `miniprogram/images/tab-*.png` | 替换 | 8个图标（4彩色选中 + 4灰度默认） |
| `scripts/gen_icons.py` | 新建 | ComfyUI 图标生成脚本（项目根目录） |

---

## Task 1：更新全局样式变量（app.wxss + app.json）

**Files:**
- Modify: `miniprogram/app.wxss`
- Modify: `miniprogram/app.json`

- [ ] **Step 1: 更新 app.wxss**

将 `miniprogram/app.wxss` 完整替换为：

```css
/* miniprogram/app.wxss */
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
  --font-title: 36rpx;

  background-color: #f5f5f5;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: var(--color-text);
  font-size: 30rpx;
  line-height: 1.7;
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
  font-weight: 700;
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

- [ ] **Step 2: 更新 app.json tabBar 颜色**

在 `miniprogram/app.json` 中，将 tabBar 部分的 `color`、`selectedColor`、`backgroundColor` 改为：

```json
"tabBar": {
  "color": "#aaaaaa",
  "selectedColor": "#FF8C42",
  "backgroundColor": "#FFFDF5",
  "borderStyle": "white",
  "list": [
    {
      "pagePath": "pages/home/home",
      "text": "首页",
      "iconPath": "images/tab-home.png",
      "selectedIconPath": "images/tab-home-active.png"
    },
    {
      "pagePath": "pages/assessment/assessment",
      "text": "评估",
      "iconPath": "images/tab-assess.png",
      "selectedIconPath": "images/tab-assess-active.png"
    },
    {
      "pagePath": "pages/plan/plan",
      "text": "计划",
      "iconPath": "images/tab-plan.png",
      "selectedIconPath": "images/tab-plan-active.png"
    },
    {
      "pagePath": "pages/chat/chat",
      "text": "问答",
      "iconPath": "images/tab-chat.png",
      "selectedIconPath": "images/tab-chat-active.png"
    }
  ]
}
```

- [ ] **Step 3: 在开发者工具模拟器中确认无报错**

在微信开发者工具控制台查看，不应有 WXSS 解析错误。

- [ ] **Step 4: Commit**

```bash
git add miniprogram/app.wxss miniprogram/app.json
git commit -m "style: update global color system and tabBar theme to KA Kids palette"
```

---

## Task 2：重写首页 WXML 结构

**Files:**
- Modify: `miniprogram/pages/home/home.wxml`

- [ ] **Step 1: 替换 home.wxml 为新结构**

将 `miniprogram/pages/home/home.wxml` 完整替换为：

```xml
<view class="container">
  <!-- 紧凑标题栏 -->
  <view class="hero">
    <view class="hero-title">幼小衔接家长助手</view>
  </view>

  <view class="section-title">开始探索</view>

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

  <!-- 个性化计划卡片（黄） -->
  <view class="menu-card" bindtap="goPlan">
    <view class="card-accent" style="background:var(--color-yellow)"></view>
    <view class="menu-icon-wrap" style="background:var(--color-yellow-light)">
      <text class="menu-icon-emoji">📅</text>
    </view>
    <view class="menu-info">
      <view class="menu-name">个性化计划</view>
      <view class="menu-desc">AI 定制幼小衔接方案</view>
    </view>
    <view class="menu-arrow">›</view>
  </view>

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

  <!-- 使用步骤 -->
  <view class="guide">
    <view class="guide-title">使用步骤</view>
    <view class="guide-step">
      <view class="step-badge">1</view>
      <text class="step-text">填写孩子基本信息</text>
    </view>
    <view class="guide-step">
      <view class="step-badge">2</view>
      <text class="step-text">完成 8 项能力评估</text>
    </view>
    <view class="guide-step">
      <view class="step-badge">3</view>
      <text class="step-text">生成个性化计划</text>
    </view>
    <view class="guide-step">
      <view class="step-badge">4</view>
      <text class="step-text">有问题随时咨询</text>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 截图确认结构渲染（无 CSS 时先看骨架）**

用 MCP 工具截图：`mcp__weapp-dev__mp_screenshot`（需先 ensureConnection with wsEndpoint ws://localhost:9420）

- [ ] **Step 3: Commit**

```bash
git add miniprogram/pages/home/home.wxml
git commit -m "feat: redesign home page structure - compact hero, colorful accent cards"
```

---

## Task 3：重写首页 WXSS 样式

**Files:**
- Modify: `miniprogram/pages/home/home.wxss`

- [ ] **Step 1: 替换 home.wxss 为新样式**

将 `miniprogram/pages/home/home.wxss` 完整替换为：

```css
/* pages/home/home.wxss */
.container {
  padding: 0 0 140rpx;
}

/* 紧凑标题栏 */
.hero {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  padding: 40rpx 40rpx;
  text-align: center;
}

.hero-title {
  font-size: 34rpx;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 2rpx;
}

/* 区块标题 */
.section-title {
  font-size: 26rpx;
  font-weight: 800;
  color: var(--color-text-sub);
  padding: 36rpx 32rpx 16rpx;
  text-transform: uppercase;
  letter-spacing: 3rpx;
}

/* 功能卡片 */
.menu-card {
  display: flex;
  align-items: center;
  background: #fff;
  margin: 0 24rpx 20rpx;
  border-radius: var(--radius-card);
  padding: 28rpx 24rpx 28rpx 0;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* 左侧彩色竖条 */
.card-accent {
  width: 8rpx;
  height: 80rpx;
  border-radius: 0 4rpx 4rpx 0;
  margin-right: 20rpx;
  flex-shrink: 0;
}

/* icon 圆形色块 */
.menu-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.menu-icon-emoji {
  font-size: 40rpx;
  line-height: 1;
}

.menu-info {
  flex: 1;
}

.menu-name {
  font-size: 32rpx;
  font-weight: 800;
  margin-bottom: 6rpx;
  color: var(--color-text);
}

.menu-desc {
  font-size: 24rpx;
  color: var(--color-text-sub);
}

.menu-arrow {
  font-size: 44rpx;
  color: #ccc;
  line-height: 1;
}

/* 使用步骤 */
.guide {
  margin: 8rpx 24rpx 0;
  border-radius: var(--radius-card);
  padding: 32rpx 28rpx;
  background: #FFF9E6;
}

.guide-title {
  font-size: 28rpx;
  font-weight: 800;
  color: var(--color-orange);
  margin-bottom: 20rpx;
}

.guide-step {
  display: flex;
  align-items: center;
  padding: 8rpx 0;
}

.step-badge {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: var(--color-orange);
  color: #fff;
  font-size: 22rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.step-text {
  font-size: 26rpx;
  color: var(--color-text);
}
```

- [ ] **Step 2: 截图确认首页样式**

用 `mcp__weapp-dev__mp_screenshot`（连接参数 wsEndpoint: ws://localhost:9420）截图，确认：
- hero 区为绿色紧凑横幅，文字"幼小衔接家长助手"
- 三张卡片各有彩色左竖条（橙/黄/紫）和对应色背景的圆形图标
- 使用步骤区背景暖黄，序号为橙色圆形徽章

- [ ] **Step 3: Commit**

```bash
git add miniprogram/pages/home/home.wxss
git commit -m "style: apply KA Kids visual style to home page - colorful cards, compact hero"
```

---

## Task 4：生成 tabBar 图标（ComfyUI）

**Files:**
- Create: `scripts/gen_icons.py`
- Replace: `miniprogram/images/tab-home-active.png`
- Replace: `miniprogram/images/tab-assess-active.png`
- Replace: `miniprogram/images/tab-plan-active.png`
- Replace: `miniprogram/images/tab-chat-active.png`
- Replace: `miniprogram/images/tab-home.png`
- Replace: `miniprogram/images/tab-assess.png`
- Replace: `miniprogram/images/tab-plan.png`
- Replace: `miniprogram/images/tab-chat.png`

- [ ] **Step 1: 确认 ComfyUI 可用模型名称**

运行以下命令查看模型名称（用于 workflow 中的 ckpt_name）：

```bash
curl -s "http://100.90.137.80:8188/object_info/CheckpointLoaderSimple" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ckpts = d['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0]
print('Available checkpoints:', ckpts)
"
```

记录输出中包含 "turbo" 的模型名称，用于 Step 2。若列表为空，改用：

```bash
curl -s "http://100.90.137.80:8188/models/checkpoints"
```

- [ ] **Step 2: 创建图标生成脚本 scripts/gen_icons.py**

在项目根目录创建 `scripts/gen_icons.py`：

```python
#!/usr/bin/env python3
"""
生成小程序 tabBar 图标，通过 ComfyUI API（z-image-turbo 模型）
用法: python3 scripts/gen_icons.py [--ckpt MODEL_NAME]
"""
import argparse
import json
import os
import time
import urllib.request
import urllib.error

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install Pillow")
    raise

# === 配置 ===
COMFY_URL = "http://100.90.137.80:8188"
OUTPUT_DIR = "miniprogram/images"
ICON_SIZE = 81  # 微信 tabBar 最佳尺寸

ICONS = [
    {
        "name": "tab-home",
        "prompt": "cute flat icon, tiny house with green roof and round chimney, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
    {
        "name": "tab-assess",
        "prompt": "cute flat icon, clipboard with orange star sticker on it, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
    {
        "name": "tab-plan",
        "prompt": "cute flat icon, calendar page with yellow sun drawing on it, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
    {
        "name": "tab-chat",
        "prompt": "cute flat icon, round speech bubble with purple heart inside, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
]


def build_workflow(prompt_text: str, ckpt_name: str, seed: int) -> dict:
    return {
        "prompt": {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": ckpt_name},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["1", 1],
                    "text": prompt_text,
                },
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["1", 1],
                    "text": "blurry, ugly, text, watermark, complex background, 3D, realistic photo",
                },
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {"batch_size": 1, "height": 512, "width": 512},
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": 1.5,
                    "denoise": 1,
                    "latent_image": ["4", 0],
                    "model": ["1", 0],
                    "negative": ["3", 0],
                    "positive": ["2", 0],
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "seed": seed,
                    "steps": 6,
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "tabicon",
                    "images": ["6", 0],
                },
            },
        }
    }


def post_prompt(workflow: dict) -> str:
    data = json.dumps(workflow).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 120) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=10) as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"ComfyUI did not finish in {timeout}s")


def download_image(filename: str, subfolder: str = "") -> bytes:
    url = f"{COMFY_URL}/view?filename={filename}&subfolder={subfolder}&type=output"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def save_icon(img_bytes: bytes, out_path: str):
    from io import BytesIO
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    # 填充白色背景（微信 tabBar 不支持透明）
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    bg = bg.convert("RGB")
    bg = bg.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    bg.save(out_path, "PNG", optimize=True)
    size_kb = os.path.getsize(out_path) / 1024
    print(f"  Saved: {out_path} ({size_kb:.1f} KB)")
    if size_kb > 40:
        print(f"  WARNING: file > 40KB, WeChat may reject it")


def make_grayscale(color_path: str, gray_path: str):
    img = Image.open(color_path).convert("RGB")
    gray = img.convert("L").convert("RGB")
    gray.save(gray_path, "PNG", optimize=True)
    print(f"  Gray: {gray_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", default="z-image-turbo.safetensors",
                        help="ComfyUI checkpoint name (exact filename)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, icon in enumerate(ICONS):
        print(f"\n[{i+1}/{len(ICONS)}] Generating {icon['name']}...")
        workflow = build_workflow(icon["prompt"], args.ckpt, seed=42 + i * 100)

        prompt_id = post_prompt(workflow)
        print(f"  prompt_id: {prompt_id}, waiting...")

        history = wait_for_completion(prompt_id)
        outputs = history["outputs"]

        # 找到 SaveImage 节点的输出
        img_info = None
        for node_id, node_out in outputs.items():
            if "images" in node_out:
                img_info = node_out["images"][0]
                break

        if not img_info:
            print(f"  ERROR: no image output found")
            continue

        img_bytes = download_image(img_info["filename"], img_info.get("subfolder", ""))

        active_path = os.path.join(OUTPUT_DIR, f"{icon['name']}-active.png")
        default_path = os.path.join(OUTPUT_DIR, f"{icon['name']}.png")

        save_icon(img_bytes, active_path)
        make_grayscale(active_path, default_path)

    print("\nDone! All icons saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 安装 Pillow（如未安装）**

```bash
pip3 install Pillow
```

- [ ] **Step 4: 查询实际 checkpoint 名称并运行**

先运行 Step 1 的命令确认模型名。若模型名为 `z-image-turbo.safetensors`（默认），直接运行：

```bash
cd /Users/robertzf/cc_workspace/kindergarten_to_school
python3 scripts/gen_icons.py
```

若模型名不同（如 `turbo_v2.safetensors`），指定：

```bash
python3 scripts/gen_icons.py --ckpt "实际模型名.safetensors"
```

预期输出：
```
[1/4] Generating tab-home...
  prompt_id: xxxx, waiting...
  Saved: miniprogram/images/tab-home-active.png (12.3 KB)
  Gray: miniprogram/images/tab-home.png
...
Done! All icons saved to miniprogram/images
```

- [ ] **Step 5: 截图确认 tabBar 图标显示**

用 `mcp__weapp-dev__mp_screenshot` 截图，确认 tabBar 显示新图标。
若图标未更新，在微信开发者工具点击"编译"刷新。

- [ ] **Step 6: Commit**

```bash
git add scripts/gen_icons.py miniprogram/images/
git commit -m "feat: add ComfyUI icon generation script and update tabBar icons"
```

---

## Task 5：整体验证

- [ ] **Step 1: 截图首页**

连接 DevTools（wsEndpoint: ws://localhost:9420），截图确认：
- hero 为绿色紧凑横幅，文字"幼小衔接家长助手"
- 三张卡片有彩色左竖条和圆形 icon 背景
- 使用步骤区背景暖黄，橙色数字徽章

- [ ] **Step 2: 切换各 tab，逐一截图确认**

用 `mcp__weapp-dev__mp_navigate` 跳转各页面，确认：
- tabBar 图标彩色/灰色切换正常
- 各页面布局不受全局字体/圆角变化影响（内页未改动）
- 无 WXSS 报错

- [ ] **Step 3: 最终 Commit**

```bash
git add -A
git commit -m "chore: final verification pass - KA Kids UI redesign complete"
```

---

## 注意事项

1. **ComfyUI 模型名必须精确**：`ckpt_name` 需与服务器上的实际文件名完全一致（含扩展名），否则 ComfyUI 返回错误。先跑 Step 1 确认。
2. **tabBar 图标白底**：微信 tabBar 不支持透明背景图，脚本已自动填充白色底。
3. **图标大小限制**：单个图标 ≤ 40KB，512px 生成后缩至 81px 通常 10-20KB，无问题。
4. **热重载**：修改 WXSS/WXML 后开发者工具自动重编译；替换 PNG 图片后需手动点击"编译"。
5. **内页样式**：`assessment/result/plan/chat` 页面样式未改动，但全局 `font-size` 从 28rpx → 30rpx 会略微影响布局，截图时注意检查。
