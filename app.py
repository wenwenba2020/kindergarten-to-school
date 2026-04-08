"""
幼小衔接规划Agent - Web界面
使用 Streamlit 构建
"""

import os
import logging
from datetime import datetime
from io import BytesIO

from dotenv import load_dotenv
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from assessment import calculate_assessment

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


# ==================== 错误提示配置 ====================
ERROR_MESSAGES = {
    "no_api_key": """
**未检测到有效的 API Key**

请按以下步骤配置：
1. 复制 `.env.example` 为 `.env`
2. 填入你的 `OPENAI_API_KEY`
3. 重启应用

💡 如果没有 API Key，应用会使用示例计划和本地问答功能。
""",
    "llm_connection_error": """
**LLM 连接失败**

可能的原因：
- API Key 无效或已过期
- 网络连接问题
- API 服务暂时不可用

建议：
1. 检查 `.env` 中的 API Key 是否正确
2. 检查网络连接
3. 稍后重试
""",
    "plan_generation_error": """
**计划生成失败**

建议：
1. 刷新页面后重试
2. 检查 API Key 是否有效
3. 使用本地示例计划作为参考
""",
    "chat_error": """
**问答服务暂时不可用**

建议：
1. 尝试使用常见问题快速入口
2. 稍后重试
""",
}


def show_error(error_type: str, exception: Exception = None):
    """显示友好的错误提示"""
    msg = ERROR_MESSAGES.get(error_type, "发生未知错误，请稍后重试。")
    st.error(msg)
    if exception and os.getenv("DEBUG"):
        st.exception(exception)


# ==================== 辅助函数 ====================
def llm_enabled() -> bool:
    return bool(
        os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_AUTH_TOKEN")
        or os.getenv("ANTHROPIC_API_KEY")
    )


@st.cache_resource
def get_agent(cache_buster: float):
    from kindergarten_agent_full import KindergartenAgent

    try:
        return KindergartenAgent()
    except ValueError as e:
        logger.error(f"Agent 初始化失败: {e}")
        return None
    except Exception as e:
        logger.error(f"Agent 初始化异常: {e}")
        return None


def set_menu(target: str) -> None:
    st.session_state["menu"] = target


def scored_radio(prompt, options, index=2, key=None):
    scores = list(range(1, len(options) + 1))
    return st.radio(
        prompt,
        scores,
        index=index,
        horizontal=True,
        format_func=lambda x: options[x - 1],
        key=key,
    )


def create_radar_chart(profile: dict) -> go.Figure:
    """创建八维能力雷达图"""
    language = profile.get("language", {})
    math = profile.get("math", {})

    # 计算各维度平均分
    lang_avg = sum([
        language.get("listening", 3),
        language.get("expression", 3),
        language.get("reading", 3),
        language.get("writing_interest", 3)
    ]) / 4

    math_avg = sum([
        math.get("counting", 3),
        math.get("operation", 3),
        math.get("shapes", 3),
        math.get("space", 3)
    ]) / 4

    categories = ['语言能力', '数学能力', '社交能力', '自理能力', '运动能力', '专注力', '情绪管理', '时间观念']
    values = [
        lang_avg,
        math_avg,
        profile.get("social", 3),
        profile.get("self_care", 3),
        profile.get("motor", 3),
        profile.get("focus", 3),
        profile.get("emotion", 3),
        profile.get("time_awareness", 3)
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # 闭合
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(76, 175, 80, 0.3)',
        line=dict(color='#4CAF50', width=2),
        name='能力得分',
        marker=dict(size=8, color='#4CAF50')
    ))

    # 添加基准线（满分）
    fig.add_trace(go.Scatterpolar(
        r=[5] * 9,
        theta=categories + [categories[0]],
        line=dict(color='rgba(200, 200, 200, 0.5)', width=1, dash='dash'),
        name='满分基准',
        showlegend=False
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['1', '2', '3', '4', '5']
            ),
            bgcolor='#f8f9fa'
        ),
        showlegend=False,
        title=dict(
            text='八维能力雷达图',
            font=dict(size=16, color='#2c3e50')
        ),
        height=400,
        margin=dict(l=40, r=40, t=50, b=30)
    )

    return fig


def create_bar_chart(profile: dict) -> go.Figure:
    """创建各维度详细得分柱状图"""
    language = profile.get("language", {})
    math = profile.get("math", {})

    # 所有子维度（包含新增维度）
    labels = [
        '倾听理解', '表达交流', '阅读习惯', '书写兴趣',
        '计数能力', '运算能力', '图形认知', '空间方位',
        '社交能力', '自理能力', '运动能力',
        '专注力', '情绪管理', '时间观念'
    ]

    values = [
        language.get("listening", 3),
        language.get("expression", 3),
        language.get("reading", 3),
        language.get("writing_interest", 3),
        math.get("counting", 3),
        math.get("operation", 3),
        math.get("shapes", 3),
        math.get("space", 3),
        profile.get("social", 3),
        profile.get("self_care", 3),
        profile.get("motor", 3),
        profile.get("focus", 3),
        profile.get("emotion", 3),
        profile.get("time_awareness", 3)
    ]

    # 颜色分类
    colors = (
        ['#2196F3'] * 4 +  # 语言
        ['#FF9800'] * 4 +  # 数学
        ['#4CAF50', '#9C27B0', '#F44336'] +  # 社交、自理、运动
        ['#00BCD4', '#E91E63', '#795548']  # 专注力、情绪、时间
    )

    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=values,
            textposition='outside',
            textfont=dict(size=11)
        )
    ])

    fig.update_layout(
        title=dict(
            text='各维度详细得分',
            font=dict(size=16, color='#2c3e50')
        ),
        yaxis=dict(
            range=[0, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            title='得分'
        ),
        xaxis=dict(tickangle=45),
        height=380,
        margin=dict(l=40, r=40, t=50, b=100),
        plot_bgcolor='#f8f9fa',
        showlegend=False
    )

    # 添加参考线
    fig.add_hline(y=3, line_dash="dash", line_color="gray",
                  annotation_text="中等", annotation_position="right")
    fig.add_hline(y=4, line_dash="dash", line_color="green",
                  annotation_text="良好", annotation_position="right")

    return fig


def generate_pdf_report(profile: dict, result: dict) -> bytes:
    """生成 PDF 报告（使用 HTML 转 PDF）"""
    import base64

    language = profile.get("language", {})
    math = profile.get("math", {})

    # 计算各维度平均分
    lang_avg = sum([language.get(k, 3) for k in ["listening", "expression", "reading", "writing_interest"]]) / 4
    math_avg = sum([math.get(k, 3) for k in ["counting", "operation", "shapes", "space"]]) / 4

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>幼小衔接评估报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; padding: 40px; color: #333; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; }}
        .header h1 {{ color: #2c3e50; margin-bottom: 5px; }}
        .header .subtitle {{ color: #7f8c8d; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ background: #f5f5f5; padding: 10px 15px; border-left: 4px solid #4CAF50; font-size: 16px; font-weight: bold; margin-bottom: 15px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        .info-item {{ padding: 10px; background: #fafafa; border-radius: 5px; }}
        .info-label {{ color: #666; font-size: 12px; }}
        .info-value {{ font-size: 16px; font-weight: bold; color: #2c3e50; }}
        .score-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .score-table th, .score-table td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
        .score-table th {{ background: #4CAF50; color: white; }}
        .score-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .level-excellent {{ color: #4CAF50; font-weight: bold; }}
        .level-good {{ color: #FF9800; font-weight: bold; }}
        .level-attention {{ color: #F44336; font-weight: bold; }}
        .list-item {{ padding: 8px 0; border-bottom: 1px dashed #eee; }}
        .footer {{ margin-top: 40px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎒 幼小衔接能力评估报告</h1>
        <div class="subtitle">基于《3-6岁儿童学习与发展指南》</div>
    </div>

    <div class="section">
        <div class="section-title">📋 基本信息</div>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">孩子姓名</div>
                <div class="info-value">{profile.get('name', '未填写')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">年龄</div>
                <div class="info-value">{profile.get('age', 5.5)} 岁</div>
            </div>
            <div class="info-item">
                <div class="info-label">评估日期</div>
                <div class="info-value">{datetime.now().strftime('%Y年%m月%d日')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">整体水平</div>
                <div class="info-value {'level-excellent' if result.get('overall_level')=='优秀' else 'level-good' if result.get('overall_level')=='良好' else 'level-attention'}">{result.get('overall_level', '未评估')}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">📊 能力得分详情</div>
        <table class="score-table">
            <tr>
                <th>评估维度</th>
                <th>子项目</th>
                <th>得分</th>
                <th>等级</th>
            </tr>
            <tr>
                <td rowspan="4">语言能力<br>（平均 {lang_avg:.1f}分）</td>
                <td>倾听理解</td>
                <td>{language.get('listening', 3)}</td>
                <td>{'优秀' if language.get('listening', 3) >= 4 else '良好' if language.get('listening', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>表达交流</td>
                <td>{language.get('expression', 3)}</td>
                <td>{'优秀' if language.get('expression', 3) >= 4 else '良好' if language.get('expression', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>阅读习惯</td>
                <td>{language.get('reading', 3)}</td>
                <td>{'优秀' if language.get('reading', 3) >= 4 else '良好' if language.get('reading', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>书写兴趣</td>
                <td>{language.get('writing_interest', 3)}</td>
                <td>{'优秀' if language.get('writing_interest', 3) >= 4 else '良好' if language.get('writing_interest', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td rowspan="4">数学能力<br>（平均 {math_avg:.1f}分）</td>
                <td>计数能力</td>
                <td>{math.get('counting', 3)}</td>
                <td>{'优秀' if math.get('counting', 3) >= 4 else '良好' if math.get('counting', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>运算能力</td>
                <td>{math.get('operation', 3)}</td>
                <td>{'优秀' if math.get('operation', 3) >= 4 else '良好' if math.get('operation', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>图形认知</td>
                <td>{math.get('shapes', 3)}</td>
                <td>{'优秀' if math.get('shapes', 3) >= 4 else '良好' if math.get('shapes', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>空间方位</td>
                <td>{math.get('space', 3)}</td>
                <td>{'优秀' if math.get('space', 3) >= 4 else '良好' if math.get('space', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>社交能力</td>
                <td>-</td>
                <td>{profile.get('social', 3)}</td>
                <td>{'优秀' if profile.get('social', 3) >= 4 else '良好' if profile.get('social', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>自理能力</td>
                <td>-</td>
                <td>{profile.get('self_care', 3)}</td>
                <td>{'优秀' if profile.get('self_care', 3) >= 4 else '良好' if profile.get('self_care', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>运动能力</td>
                <td>-</td>
                <td>{profile.get('motor', 3)}</td>
                <td>{'优秀' if profile.get('motor', 3) >= 4 else '良好' if profile.get('motor', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>专注力</td>
                <td>-</td>
                <td>{profile.get('focus', 3)}</td>
                <td>{'优秀' if profile.get('focus', 3) >= 4 else '良好' if profile.get('focus', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>情绪管理</td>
                <td>-</td>
                <td>{profile.get('emotion', 3)}</td>
                <td>{'优秀' if profile.get('emotion', 3) >= 4 else '良好' if profile.get('emotion', 3) >= 3 else '需加强'}</td>
            </tr>
            <tr>
                <td>时间观念</td>
                <td>-</td>
                <td>{profile.get('time_awareness', 3)}</td>
                <td>{'优秀' if profile.get('time_awareness', 3) >= 4 else '良好' if profile.get('time_awareness', 3) >= 3 else '需加强'}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">✨ 优势领域</div>
        {''.join([f'<div class="list-item">• {s}</div>' for s in result.get('strengths', ['暂无明显优势'])])}
    </div>

    <div class="section">
        <div class="section-title">📌 需要加强</div>
        {''.join([f'<div class="list-item">• {a}</div>' for a in result.get('areas_to_improve', ['暂无明显不足'])])}
    </div>

    <div class="section">
        <div class="section-title">💡 发展建议</div>
        {''.join([f'<div class="list-item">• {r}</div>' for r in result.get('recommendations', [])])}
    </div>

    <div class="footer">
        <p>本报告由"小桥"幼小衔接规划助手生成</p>
        <p>依据：教育部《3-6岁儿童学习与发展指南》</p>
    </div>
</body>
</html>
"""

    # 使用 weasyprint 或返回 HTML 供浏览器打印
    # 这里返回 HTML，让用户通过浏览器打印为 PDF
    return html_content.encode('utf-8')


def get_pdf_download_link(html_content: bytes, filename: str) -> str:
    """生成 PDF 下载链接（实际上是 HTML 打印）"""
    b64 = base64.b64encode(html_content).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" target="_blank">📥 点击下载评估报告（HTML格式，可打印为PDF）</a>'


import base64


def render_plan(plan: dict) -> None:
    if not isinstance(plan, dict):
        st.markdown(str(plan))
        return

    if "raw" in plan:
        st.markdown(plan["raw"])
        return

    duration = plan.get("duration")
    if duration:
        st.markdown(f"**周期：** {duration}")

    weekly_goals = plan.get("weekly_goals", [])
    if weekly_goals:
        st.markdown("### 每周重点目标")
        for item in weekly_goals:
            st.markdown(f"- {item}")

    daily_activities = plan.get("daily_activities", [])
    if daily_activities:
        st.markdown("### 每日推荐活动")
        st.table(daily_activities)

    resources = plan.get("resources", [])
    if resources:
        st.markdown("### 推荐资源")
        for item in resources:
            st.markdown(f"- {item}")

    parent_tips = plan.get("parent_tips", [])
    if parent_tips:
        st.markdown("### 家长注意事项")
        for item in parent_tips:
            st.markdown(f"- {item}")

    evaluation = plan.get("evaluation_criteria", [])
    if evaluation:
        st.markdown("### 评估标准")
        for item in evaluation:
            st.markdown(f"- {item}")


# ==================== 本地问答配置 ====================
import json
from pathlib import Path

def load_fallback_qa() -> dict:
    """从配置文件加载本地问答"""
    config_path = Path(__file__).parent / "fallback_qa.json"
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"加载本地问答配置失败: {e}")
    return {"questions": [], "default_answer": "这个问题建议咨询专业教育人士或查看当地教育部门官方指南。"}


FALLBACK_QA_CONFIG = load_fallback_qa()


def local_answer(question: str) -> str:
    """本地问答匹配"""
    question_lower = question.lower()
    for item in FALLBACK_QA_CONFIG.get("questions", []):
        for keyword in item.get("keywords", []):
            if keyword in question_lower:
                return item.get("answer", "")
    return FALLBACK_QA_CONFIG.get("default_answer", "这个问题建议咨询专业教育人士或查看当地教育部门官方指南。")

# 页面配置
st.set_page_config(
    page_title="小桥 - 幼小衔接规划助手",
    page_icon="🎒",
    layout="wide"
)

# ==================== 手机模拟器配置 ====================
# 微信小程序设计规格：
# - 设计稿宽度: 750rpx
# - iPhone 6/7/8 屏幕宽度: 375pt (750px物理像素)
# - 状态栏高度: 20pt (40px)
# - 导航栏高度: 44pt (88px)
# - Tab Bar 高度: 50pt (100px)
# - 底部安全区: 34pt (68px, iPhone X+)

PHONE_WIDTH = 375  # 屏幕宽度 px
PHONE_HEIGHT = 667  # iPhone 6/7/8 屏幕高度
STATUS_BAR_HEIGHT = 20
NAV_BAR_HEIGHT = 44
TAB_BAR_HEIGHT = 50

# 手机模拟器 CSS
PHONE_CSS = """
<style>
    /* 手机外框 */
    .phone-container {
        width: 375px;
        height: 750px;
        background: #1a1a1a;
        border-radius: 40px;
        padding: 12px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin: 0 auto;
        position: relative;
    }

    /* 手机刘海 */
    .phone-notch {
        width: 150px;
        height: 28px;
        background: #1a1a1a;
        border-radius: 0 0 20px 20px;
        position: absolute;
        top: 12px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 100;
    }

    /* 手机屏幕 */
    .phone-screen {
        width: 100%;
        height: 100%;
        background: #ffffff;
        border-radius: 30px;
        overflow: hidden;
        position: relative;
    }

    /* 状态栏 */
    .mini-status-bar {
        height: 20px;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 16px;
        font-size: 12px;
        color: white;
    }

    /* 导航栏 */
    .mini-nav-bar {
        height: 44px;
        background: #4CAF50;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 17px;
        font-weight: 500;
        position: relative;
    }

    .mini-nav-bar .nav-back {
        position: absolute;
        left: 12px;
        font-size: 24px;
        cursor: pointer;
    }

    /* 内容区域 */
    .mini-content {
        height: calc(100% - 114px);
        overflow-y: auto;
        overflow-x: hidden;
        background: #f5f5f5;
        padding: 12px;
        box-sizing: border-box;
    }

    /* 底部 Tab Bar */
    .mini-tab-bar {
        height: 50px;
        background: #ffffff;
        display: flex;
        border-top: 1px solid #eee;
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
    }

    .mini-tab-item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        color: #999;
        cursor: pointer;
        transition: color 0.2s;
    }

    .mini-tab-item.active {
        color: #4CAF50;
    }

    .mini-tab-item .tab-icon {
        font-size: 22px;
        margin-bottom: 2px;
    }

    /* 小程序卡片样式 */
    .mini-card {
        background: white;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .mini-card-title {
        font-size: 15px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }

    .mini-card-content {
        font-size: 13px;
        color: #666;
        line-height: 1.6;
    }

    /* 小程序按钮 */
    .mini-btn {
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 22px;
        padding: 10px 24px;
        font-size: 15px;
        width: 100%;
        margin-top: 10px;
        cursor: pointer;
    }

    .mini-btn-outline {
        background: white;
        color: #4CAF50;
        border: 1px solid #4CAF50;
    }

    /* 小程序输入框 */
    .mini-input {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 10px;
        box-sizing: border-box;
    }

    /* 小程序列表项 */
    .mini-list-item {
        padding: 12px;
        background: white;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
    }

    .mini-list-item:last-child {
        border-bottom: none;
    }

    /* 进度条 */
    .mini-progress {
        height: 6px;
        background: #e0e0e0;
        border-radius: 3px;
        overflow: hidden;
        margin: 8px 0;
    }

    .mini-progress-bar {
        height: 100%;
        background: #4CAF50;
        border-radius: 3px;
        transition: width 0.3s;
    }

    /* 标签 */
    .mini-tag {
        display: inline-block;
        padding: 2px 8px;
        background: #e8f5e9;
        color: #4CAF50;
        border-radius: 4px;
        font-size: 11px;
        margin-right: 6px;
    }

    .mini-tag-warning {
        background: #fff3e0;
        color: #ff9800;
    }

    .mini-tag-danger {
        background: #ffebee;
        color: #f44336;
    }

    /* 分数展示 */
    .mini-score {
        font-size: 28px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
    }

    /* 隐藏 Streamlit 默认样式 */
    .phone-mode .block-container {
        padding-top: 0 !important;
    }

    .phone-mode header {
        display: none;
    }

    .phone-mode .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
"""

# 自定义CSS（保留原有样式用于非手机模式）
DESKTOP_CSS = """
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .feature-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 15px;
        border-radius: 5px;
    }
    .header-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 10px;
    }
    .header-subtitle {
        font-size: 1.2em;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
"""

# 初始化显示模式
if 'phone_mode' not in st.session_state:
    st.session_state.phone_mode = True  # 默认手机模式

# 应用对应模式的CSS
if st.session_state.phone_mode:
    st.markdown(PHONE_CSS, unsafe_allow_html=True)
else:
    st.markdown(DESKTOP_CSS, unsafe_allow_html=True)

# ==================== 本地存储功能 ====================
import base64
import json

def encode_data(data: dict) -> str:
    """将数据编码为 URL 安全的字符串"""
    json_str = json.dumps(data, ensure_ascii=False)
    return base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')

def decode_data(encoded: str) -> dict:
    """从 URL 字符串解码数据"""
    try:
        json_str = base64.urlsafe_b64decode(encoded.encode('ascii')).decode('utf-8')
        return json.loads(json_str)
    except Exception:
        return None

def get_share_url(data: dict) -> str:
    """生成分享链接"""
    encoded = encode_data(data)
    # 使用 st.experimental_get_query_params 获取当前 URL
    return f"?data={encoded}"

def load_from_url():
    """从 URL 参数加载数据"""
    try:
        params = st.query_params
        if 'data' in params:
            data = decode_data(params['data'])
            if data:
                return data
    except Exception:
        pass
    return None

# 初始化会话状态
if 'profile' not in st.session_state:
    # 尝试从 URL 加载
    url_data = load_from_url()
    st.session_state.profile = url_data.get('profile') if url_data else None
if 'assessment_result' not in st.session_state:
    url_data = load_from_url()
    st.session_state.assessment_result = url_data.get('assessment_result') if url_data else None
if 'plan' not in st.session_state:
    st.session_state.plan = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_loaded' not in st.session_state:
    st.session_state.agent_loaded = False

# 预加载 Agent（后台运行）
if llm_enabled() and not st.session_state.agent_loaded:
    try:
        with st.spinner("正在初始化 AI 服务..."):
            agent = get_agent(0)  # 预加载
            if agent:
                st.session_state.agent_loaded = True
    except Exception as e:
        logger.warning(f"Agent 预加载失败: {e}")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("🎒 小桥助手")
    st.markdown("---")

    # 显示模式切换
    st.markdown("### 📱 显示模式")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 手机模式", use_container_width=True, type="primary" if st.session_state.phone_mode else "secondary"):
            st.session_state.phone_mode = True
            st.rerun()
    with col2:
        if st.button("💻 桌面模式", use_container_width=True, type="primary" if not st.session_state.phone_mode else "secondary"):
            st.session_state.phone_mode = False
            st.rerun()

    st.markdown("---")

    menu_options = ["🏠 首页", "📋 能力评估", "🎮 孩子互动评估", "📅 生成计划", "💬 问答咨询"]
    current_index = menu_options.index(st.session_state.get('menu', "🏠 首页")) if st.session_state.get('menu', "🏠 首页") in menu_options else 0

    menu = st.radio(
        "功能菜单",
        menu_options,
        index=current_index,
        key="menu",
    )

    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    1. 先进行**能力评估**
    2. 可选**孩子互动评估**
    3. 根据评估结果**生成计划**
    4. 有问题可以**问答咨询**
    """)

    st.markdown("---")
    st.markdown("### 🔌 LLM 状态")
    if llm_enabled():
        st.success("已启用个性化计划与问答")
    else:
        st.warning("未检测到 API Key，将显示示例计划与本地问答")

# ==================== 首页 ====================
if menu == "🏠 首页":
    if st.session_state.phone_mode:
        # 手机模式：显示手机模拟器
        from datetime import datetime
        from phone_components import HOME_CONTENT, render_phone_frame

        phone_html = render_phone_frame(
            nav_title="小桥助手",
            content=HOME_CONTENT,
            active_tab=0
        )

        # 居中显示手机
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(phone_html, unsafe_allow_html=True)

        # 底部操作按钮（隐藏在手机内容中点击）
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 开始评估", use_container_width=True):
                set_menu("📋 能力评估")
                st.rerun()
        with col2:
            if st.button("🎮 互动评估", use_container_width=True):
                set_menu("🎮 孩子互动评估")
                st.rerun()
    else:
        # 桌面模式：原有布局
        st.markdown('<p class="header-title">🎒 幼小衔接规划助手</p>', unsafe_allow_html=True)
        st.markdown('<p class="header-subtitle">帮助孩子顺利过渡到小学生活</p>', unsafe_allow_html=True)

        # 核心功能介绍
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>📋 能力评估</h3>
                <p>根据《3-6岁儿童学习与发展指南》，评估孩子语言、数学、社交等各方面发展水平</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>📅 个性化计划</h3>
                <p>根据评估结果，生成针对性的幼小衔接计划，每日活动推荐</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>💬 专家问答</h3>
                <p>解答关于入学准备、能力培养等方面的疑问</p>
            </div>
            """, unsafe_allow_html=True)

        # 快速评估入口
        st.markdown("### 🚀 快速开始")
        st.button(
            "开始能力评估 →",
            use_container_width=True,
            on_click=set_menu,
            args=("📋 能力评估",),
        )

# ==================== 能力评估 ====================
elif menu == "📋 能力评估":
    if st.session_state.phone_mode:
        # 手机模式
        from phone_components import render_phone_frame, get_phone_assessment_page

        # 分页控制
        if 'assessment_page' not in st.session_state:
            st.session_state.assessment_page = 1

        # 表单数据初始化
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                "name": "", "age": 5.5,
                "lang_listening": 3, "lang_expression": 3, "lang_reading": 3, "lang_writing": 3,
                "math_counting": 3, "math_operation": 3, "math_shapes": 3, "math_space": 3,
                "social": 3, "self_care": 3, "motor": 3,
                "focus": 3, "emotion": 3, "time_awareness": 3,
                "interests": [], "concerns": []
            }

        total_pages = 5
        page = st.session_state.assessment_page

        # 生成手机页面内容
        phone_content = get_phone_assessment_page(page, total_pages, st.session_state.form_data)
        phone_html = render_phone_frame(nav_title="能力评估", content=phone_content, active_tab=1)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(phone_html, unsafe_allow_html=True)

        # 页面导航按钮
        st.markdown("---")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

        with nav_col1:
            if page > 1:
                if st.button("⬅️ 上一页", use_container_width=True):
                    st.session_state.assessment_page -= 1
                    st.rerun()

        with nav_col3:
            if page < total_pages:
                if st.button("下一页 ➡️", use_container_width=True):
                    if page == 1 and not st.session_state.form_data.get("name", "").strip():
                        st.error("请输入孩子姓名")
                    else:
                        st.session_state.assessment_page += 1
                        st.rerun()
            else:
                if st.button("✅ 提交评估", use_container_width=True, type="primary"):
                    name = st.session_state.form_data.get("name", "").strip()
                    if not name:
                        st.error("请输入孩子姓名")
                    else:
                        st.session_state.profile = {
                            "name": name,
                            "age": st.session_state.form_data.get("age", 5.5),
                            "language": {
                                "listening": st.session_state.form_data.get("lang_listening", 3),
                                "expression": st.session_state.form_data.get("lang_expression", 3),
                                "reading": st.session_state.form_data.get("lang_reading", 3),
                                "writing_interest": st.session_state.form_data.get("lang_writing", 3)
                            },
                            "math": {
                                "counting": st.session_state.form_data.get("math_counting", 3),
                                "operation": st.session_state.form_data.get("math_operation", 3),
                                "shapes": st.session_state.form_data.get("math_shapes", 3),
                                "space": st.session_state.form_data.get("math_space", 3)
                            },
                            "social": st.session_state.form_data.get("social", 3),
                            "self_care": st.session_state.form_data.get("self_care", 3),
                            "motor": st.session_state.form_data.get("motor", 3),
                            "focus": st.session_state.form_data.get("focus", 3),
                            "emotion": st.session_state.form_data.get("emotion", 3),
                            "time_awareness": st.session_state.form_data.get("time_awareness", 3),
                            "interests": st.session_state.form_data.get("interests", []),
                            "concerns": st.session_state.form_data.get("concerns", [])
                        }
                        st.session_state.assessment_result = calculate_assessment(st.session_state.profile)
                        st.session_state.assessment_page = 1
                        st.success("评估完成！")

        # 显示评估结果
        if st.session_state.assessment_result and st.session_state.profile:
            st.markdown("---")
            result = st.session_state.assessment_result
            profile = st.session_state.profile

            st.markdown(f"## 📊 {profile['name']}的评估报告")
            level_colors = {"优秀": "🟢", "良好": "🟡", "需加强关注": "🔴"}
            st.info(f"{level_colors.get(result['overall_level'], '')} 整体水平: {result['overall_level']}")

            # 可视化
            col1, col2 = st.columns(2)
            with col1:
                radar_fig = create_radar_chart(profile)
                st.plotly_chart(radar_fig, use_container_width=True)
            with col2:
                bar_fig = create_bar_chart(profile)
                st.plotly_chart(bar_fig, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if result['strengths']:
                    st.markdown("### ✨ 优势")
                    for s in result['strengths']:
                        st.markdown(f"- {s}")
            with col2:
                if result['areas_to_improve']:
                    st.markdown("### 📌 需加强")
                    for a in result['areas_to_improve']:
                        st.markdown(f"- {a}")

            # PDF导出
            st.markdown("---")
            html_report = generate_pdf_report(profile, result)
            st.download_button(
                label="📥 下载评估报告",
                data=html_report,
                file_name=f"评估报告_{profile['name']}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

            st.button("📅 去生成计划 →", use_container_width=True, on_click=set_menu, args=("📅 生成计划",))
    else:
        # 桌面模式（原有代码）
        st.title("📋 孩子能力评估")
        st.markdown("请根据孩子的日常表现选择最符合的选项")

    # 分页控制
    if 'assessment_page' not in st.session_state:
        st.session_state.assessment_page = 1

    # 表单数据初始化
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            "name": "",
            "age": 5.5,
            "lang_listening": 3,
            "lang_expression": 3,
            "lang_reading": 3,
            "lang_writing": 3,
            "math_counting": 3,
            "math_operation": 3,
            "math_shapes": 3,
            "math_space": 3,
            "social": 3,
            "self_care": 3,
            "motor": 3,
            # 新增评估维度
            "focus": 3,  # 专注力
            "emotion": 3,  # 情绪管理
            "time_awareness": 3,  # 时间观念
            "interests": [],
            "concerns": []
        }

    # 页面验证错误信息
    if 'page_error' not in st.session_state:
        st.session_state.page_error = ""

    # 总页数（扩展为5页）
    total_pages = 5

    # 进度条
    progress = st.session_state.assessment_page / total_pages
    st.progress(progress)
    st.markdown(f"<p style='text-align: center;'>第 {st.session_state.assessment_page} / {total_pages} 页</p>", unsafe_allow_html=True)

    # 显示页面错误
    if st.session_state.page_error:
        st.error(st.session_state.page_error)
        st.session_state.page_error = ""

    # 页面内容
    page = st.session_state.assessment_page

    # 第一页：基本信息 + 语言能力
    if page == 1:
        st.markdown("### 👶 基本信息")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "孩子姓名 *",
                placeholder="请输入姓名",
                value=st.session_state.form_data["name"],
                key="name_input_page1"
            )
        with col2:
            age = st.number_input(
                "年龄",
                min_value=5.0,
                max_value=6.5,
                value=st.session_state.form_data["age"],
                step=0.5,
                key="age_input_page1"
            )

        st.markdown("---")
        st.markdown("### 📚 语言能力")

        st.markdown("**👂 倾听理解** - 孩子能否听懂并按要求做事？")
        lang_listening = scored_radio(
            "选择最符合的描述：",
            [
                "只能听懂简单的词语和指令，需要反复提醒",
                "能听懂简单指令，但复杂指令需要重复或简化",
                "能听懂日常对话和简单指令，基本能按要求做事",
                "能听懂较复杂的指令，按要求做事较主动",
                "能很好理解对话内容，准确执行各种指令",
            ],
            index=st.session_state.form_data["lang_listening"] - 1,
            key="lang_listening_page1",
        )

        st.markdown("**🗣️ 表达交流** - 孩子能否清楚表达自己的想法？")
        lang_expression = scored_radio(
            "选择最符合的描述：",
            [
                "较少主动表达，说话较短或不清楚",
                "能说简单句子，但不太连贯",
                "能基本清楚表达自己的想法，但有时需要引导",
                "能较流畅地表达，讲述事情较完整",
                "能流畅、完整地讲述事情，词汇丰富",
            ],
            index=st.session_state.form_data["lang_expression"] - 1,
            key="lang_expression_page1",
        )

        # 实时保存第一页数据
        st.session_state.form_data["name"] = name
        st.session_state.form_data["age"] = age
        st.session_state.form_data["lang_listening"] = lang_listening
        st.session_state.form_data["lang_expression"] = lang_expression

    # 第二页：语言能力续 + 数学能力
    elif page == 2:
        st.markdown("### 📚 语言能力（续）")

        st.markdown("**📖 阅读习惯** - 孩子对阅读的兴趣和表现如何？")
        lang_reading = scored_radio(
            "选择最符合的描述：",
            [
                "不太愿意听故事或看书",
                "愿意听故事，但注意力较短",
                "喜欢听故事，能安静听一会儿",
                "有阅读兴趣，能自己翻看图书",
                "非常喜欢阅读，能专注阅读15分钟以上",
            ],
            index=st.session_state.form_data["lang_reading"] - 1,
            key="lang_reading_page2",
        )

        st.markdown("**✍️ 书写兴趣** - 孩子对写字、画画的态度？")
        lang_writing = scored_radio(
            "选择最符合的描述：",
            [
                "不太愿意拿笔或涂画",
                "愿意涂画但握笔姿势不正确",
                "愿意模仿写简单笔画，姿势基本正确",
                "能正确握笔，写自己的名字",
                "对书写很有兴趣，姿势正确，字迹清楚",
            ],
            index=st.session_state.form_data["lang_writing"] - 1,
            key="lang_writing_page2",
        )

        st.markdown("---")
        st.markdown("### 🔢 数学能力")

        st.markdown("**🔢 数数能力** - 孩子数数和点数的能力？")
        math_counting = scored_radio(
            "选择最符合的描述：",
            [
                "能数到10，但经常跳数或漏数",
                "能数到10，基本手口一致",
                "能数到20，手口基本一致",
                "能数到20以上，理解数的含义",
                "能数到100，理解数的组成和顺序",
            ],
            index=st.session_state.form_data["math_counting"] - 1,
            key="math_counting_page2",
        )

        # 实时保存第二页数据
        st.session_state.form_data["lang_reading"] = lang_reading
        st.session_state.form_data["lang_writing"] = lang_writing
        st.session_state.form_data["math_counting"] = math_counting

    # 第三页：数学能力续 + 社交自理
    elif page == 3:
        st.markdown("### 🔢 数学能力（续）")

        st.markdown("**➕ 计算能力** - 孩子进行简单加减的能力？")
        math_operation = scored_radio(
            "选择最符合的描述：",
            [
                "不太理解数量的增加和减少",
                "能通过数实物进行简单加减",
                "能做5以内加减法",
                "能做10以内加减法",
                "能做20以内加减法，理解运算含义",
            ],
            index=st.session_state.form_data["math_operation"] - 1,
            key="math_operation_page3",
        )

        st.markdown("**🔺 图形认知** - 孩子认识图形的能力？")
        math_shapes = scored_radio(
            "选择最符合的描述：",
            [
                "能认识圆形",
                "能认识圆形、三角形",
                "能认识正方形、长方形、三角形、圆形",
                "能说出图形特点并进行简单分类",
                "能认识立体图形（正方体、球体等）",
            ],
            index=st.session_state.form_data["math_shapes"] - 1,
            key="math_shapes_page3",
        )

        st.markdown("**🧭 空间方位** - 孩子对方位和空间的理解？")
        math_space = scored_radio(
            "选择最符合的描述：",
            [
                "不太理解上下、前后",
                "能理解上下、前后",
                "基本能区分上下、前后、左右",
                "能准确区分并表达方位",
                "能理解更复杂的空间关系",
            ],
            index=st.session_state.form_data["math_space"] - 1,
            key="math_space_page3",
        )

        st.markdown("---")
        st.markdown("### 👫 社交能力")
        st.markdown("孩子与同伴交往的表现？")
        social = scored_radio(
            "选择最符合的描述：",
            [
                "较害羞，不太愿意与同伴玩耍",
                "愿意与同伴玩，但不知道怎么加入",
                "能与同伴一起玩，但有时会有冲突",
                "能主动与同伴交往，合作游戏",
                "社交能力强，有很多好朋友",
            ],
            index=st.session_state.form_data["social"] - 1,
            key="social_page3",
        )

        # 实时保存第三页数据
        st.session_state.form_data["math_operation"] = math_operation
        st.session_state.form_data["math_shapes"] = math_shapes
        st.session_state.form_data["math_space"] = math_space
        st.session_state.form_data["social"] = social

    # 第四页：自理运动
    elif page == 4:
        st.markdown("### 🧹 自理能力")
        st.markdown("孩子独立做事的能力？")
        self_care = scored_radio(
            "选择最符合的描述：",
            [
                "依赖大人较多，需要帮助",
                "能做简单事情，如收拾玩具",
                "基本能自己穿脱衣服",
                "能自己整理书包，如厕",
                "自理能力强，基本不需要大人帮忙",
            ],
            index=st.session_state.form_data["self_care"] - 1,
            key="self_care_page4",
        )

        st.markdown("### 🏃 运动能力")
        st.markdown("孩子的运动和动手能力？")
        motor = scored_radio(
            "选择最符合的描述：",
            [
                "大运动和精细动作发展较慢",
                "能进行基本运动，精细动作稍弱",
                "运动能力发展正常",
                "运动能力强，精细动作好",
                "运动能力突出，动手能力强",
            ],
            index=st.session_state.form_data["motor"] - 1,
            key="motor_page4",
        )

        # 实时保存第四页数据
        st.session_state.form_data["self_care"] = self_care
        st.session_state.form_data["motor"] = motor

    # 第五页：新增维度 + 其他信息
    elif page == 5:
        st.markdown("### 🎯 专注力")
        st.markdown("孩子能专注做一件事多长时间？")
        focus = scored_radio(
            "选择最符合的描述：",
            [
                "很难专注，经常分心，不到5分钟",
                "能专注5-10分钟，但容易被干扰",
                "能专注10-15分钟完成任务",
                "能专注15-20分钟，抗干扰能力较好",
                "专注力强，能坚持20分钟以上",
            ],
            index=st.session_state.form_data["focus"] - 1,
            key="focus_page5",
        )

        st.markdown("### 😊 情绪管理")
        st.markdown("孩子情绪控制和表达能力？")
        emotion = scored_radio(
            "选择最符合的描述：",
            [
                "情绪波动大，经常哭闹发脾气",
                "情绪不太稳定，偶尔失控",
                "基本能表达情绪，有时需要引导",
                "能较好控制情绪，用语言表达",
                "情绪稳定，能自我调节",
            ],
            index=st.session_state.form_data["emotion"] - 1,
            key="emotion_page5",
        )

        st.markdown("### ⏰ 时间观念")
        st.markdown("孩子对时间的理解和遵守？")
        time_awareness = scored_radio(
            "选择最符合的描述：",
            [
                "没有时间概念，很难按时做事",
                "知道早上晚上，但不太守时",
                "知道快了慢了，基本能按时完成",
                "会看钟表，能遵守时间约定",
                "时间观念强，能自己规划时间",
            ],
            index=st.session_state.form_data["time_awareness"] - 1,
            key="time_awareness_page5",
        )

        st.markdown("---")
        st.markdown("### 📝 其他信息")
        col1, col2 = st.columns(2)
        with col1:
            interests = st.multiselect(
                "兴趣爱好",
                ["画画", "拼图", "积木", "阅读", "运动", "音乐", "科学小实验"],
                default=st.session_state.form_data["interests"],
                key="interests_page5"
            )
        with col2:
            concerns = st.multiselect(
                "家长担忧的问题",
                ["语言表达", "数学基础", "自理能力", "社交能力", "专注力", "入学焦虑", "情绪管理"],
                default=st.session_state.form_data["concerns"],
                key="concerns_page5"
            )

        # 实时保存第五页数据
        st.session_state.form_data["focus"] = focus
        st.session_state.form_data["emotion"] = emotion
        st.session_state.form_data["time_awareness"] = time_awareness
        st.session_state.form_data["interests"] = interests
        st.session_state.form_data["concerns"] = concerns

    # 导航按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if page > 1:
            if st.button("⬅️ 上一页", use_container_width=True):
                st.session_state.assessment_page -= 1
                st.rerun()

    with col2:
        if page == total_pages:
            if st.button("✅ 提交评估", use_container_width=True, type="primary"):
                # 验证姓名
                name = st.session_state.form_data.get("name", "").strip()
                if not name:
                    st.session_state.page_error = "请输入孩子姓名"
                    st.rerun()
                else:
                    # 保存评估数据
                    st.session_state.profile = {
                        "name": name,
                        "age": st.session_state.form_data.get("age", 5.5),
                        "language": {
                            "listening": st.session_state.form_data.get("lang_listening", 3),
                            "expression": st.session_state.form_data.get("lang_expression", 3),
                            "reading": st.session_state.form_data.get("lang_reading", 3),
                            "writing_interest": st.session_state.form_data.get("lang_writing", 3)
                        },
                        "math": {
                            "counting": st.session_state.form_data.get("math_counting", 3),
                            "operation": st.session_state.form_data.get("math_operation", 3),
                            "shapes": st.session_state.form_data.get("math_shapes", 3),
                            "space": st.session_state.form_data.get("math_space", 3)
                        },
                        "social": st.session_state.form_data.get("social", 3),
                        "self_care": st.session_state.form_data.get("self_care", 3),
                        "motor": st.session_state.form_data.get("motor", 3),
                        # 新增维度
                        "focus": st.session_state.form_data.get("focus", 3),
                        "emotion": st.session_state.form_data.get("emotion", 3),
                        "time_awareness": st.session_state.form_data.get("time_awareness", 3),
                        "interests": st.session_state.form_data.get("interests", []),
                        "concerns": st.session_state.form_data.get("concerns", [])
                    }
                    st.session_state.assessment_result = calculate_assessment(st.session_state.profile)
                    st.session_state.plan = None
                    st.session_state.assessment_page = 1  # 重置页码
                    # 清空表单数据
                    st.session_state.form_data = {
                        "name": "",
                        "age": 5.5,
                        "lang_listening": 3,
                        "lang_expression": 3,
                        "lang_reading": 3,
                        "lang_writing": 3,
                        "math_counting": 3,
                        "math_operation": 3,
                        "math_shapes": 3,
                        "math_space": 3,
                        "social": 3,
                        "self_care": 3,
                        "motor": 3,
                        "focus": 3,
                        "emotion": 3,
                        "time_awareness": 3,
                        "interests": [],
                        "concerns": []
                    }
                    st.success("评估完成！")

    with col3:
        if page < total_pages:
            if st.button("下一页 ➡️", use_container_width=True):
                # 第一页验证：必须填写姓名
                if page == 1:
                    name = st.session_state.form_data.get("name", "").strip()
                    if not name:
                        st.session_state.page_error = "请输入孩子姓名后继续"
                        st.rerun()
                st.session_state.assessment_page += 1
                st.rerun()

    # 显示评估结果
    if st.session_state.assessment_result and st.session_state.profile:
        st.markdown("---")
        result = st.session_state.assessment_result
        profile = st.session_state.profile

        st.markdown(f"## 📊 {profile['name']}的评估报告")

        # 整体评价
        level_colors = {"优秀": "🟢", "良好": "🟡", "需加强关注": "🔴"}
        st.info(f"{level_colors.get(result['overall_level'], '')} 整体水平: {result['overall_level']}")

        # ========== 成长可视化 ==========
        st.markdown("### 📈 能力可视化")

        # 雷达图和柱状图并排显示
        col1, col2 = st.columns(2)
        with col1:
            radar_fig = create_radar_chart(profile)
            st.plotly_chart(radar_fig, use_container_width=True)

        with col2:
            bar_fig = create_bar_chart(profile)
            st.plotly_chart(bar_fig, use_container_width=True)

        # 使用列布局展示结果
        col1, col2 = st.columns(2)
        with col1:
            if result['strengths']:
                st.markdown("### ✨ 优势")
                for s in result['strengths']:
                    st.markdown(f"- {s}")

        with col2:
            if result['areas_to_improve']:
                st.markdown("### 📌 需加强")
                for a in result['areas_to_improve']:
                    st.markdown(f"- {a}")

        if result['recommendations']:
            st.markdown("### 💡 建议")
            for r in result['recommendations']:
                st.markdown(f"- {r}")

        # ========== PDF 导出功能 ==========
        st.markdown("---")
        st.markdown("### 📥 导出报告")
        html_report = generate_pdf_report(profile, result)
        st.download_button(
            label="📥 下载评估报告（HTML格式，可打印为PDF）",
            data=html_report,
            file_name=f"幼小衔接评估报告_{profile['name']}_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )
        st.caption("💡 提示：下载后用浏览器打开，按 Ctrl+P 可打印为 PDF 文件")

        # 分享功能
        st.markdown("---")
        st.markdown("### 🔗 分享评估结果")
        share_data = {
            "profile": profile,
            "assessment_result": result
        }
        share_url = get_share_url(share_data)
        st.code(share_url, language=None)
        st.caption("复制上方链接分享给家人或老师，他们可以直接查看评估结果。")

        st.markdown("---")
        st.button(
            "根据评估结果生成计划 →",
            use_container_width=True,
            on_click=set_menu,
            args=("📅 生成计划",),
        )

# ==================== 孩子互动评估 ====================
elif menu == "🎮 孩子互动评估":
    if st.session_state.phone_mode:
        # 手机模式
        from phone_components import render_phone_frame, get_phone_game_intro, get_phone_game_question, get_phone_game_result

        # 初始化游戏状态
        if 'game_set' not in st.session_state:
            st.session_state.game_set = 1
            st.session_state.game_question = 0
            st.session_state.game_answers = {}
            st.session_state.game_completed = False
            st.session_state.ai_assessment = None

        # 三套题目定义
        GAME_SETS = {
            1: {"name": "🌟 小兔子的一天", "questions": [
                {"dimension": "语言-倾听理解", "question": "🐰 小兔子要出门了！妈妈说：「小兔子，请先穿上鞋子，再拿上书包，然后去门口等妈妈。」妈妈让小兔子按什么顺序做事？", "options": ["先拿书包再穿鞋", "先穿鞋再拿书包", "直接去门口等"], "correct": 1},
                {"dimension": "数学-计数能力", "question": "🐰 小兔子来到菜园，看到一排胡萝卜。请数一数有几根？", "display": "🥕 🥕 🥕 🥕 🥕 🥕 🥕", "options": ["5根", "6根", "7根", "8根"], "correct": 2},
                {"dimension": "社交-分享合作", "question": "🐰 小兔子遇到小松鼠，小松鼠说：「我饿了，能给我一根胡萝卜吗？」如果你是小兔子，你会怎么做？", "options": ["不理小松鼠", "给小松鼠一根胡萝卜", "把胡萝卜藏起来", "跑掉"], "correct": 1},
                {"dimension": "自理-生活技能", "question": "🐰 小兔子回到家，要自己整理书包。你觉得应该先放哪个？", "options": ["玩具小汽车", "故事书", "脏手帕", "糖果"], "correct": 1},
                {"dimension": "专注力", "question": "🐰 小兔子要做作业了。如果周围有小鸟在叫、风吹窗户的声音，你觉得小兔子应该怎么做？", "options": ["去看小鸟", "去关窗户再回来做作业", "不做了出去玩", "继续专心做作业"], "correct": 3}
            ]},
            2: {"name": "🌈 魔法城堡探险", "questions": [
                {"dimension": "数学-逻辑推理", "question": "🏰 城堡门口有一串魔法珠子：🔴 🔵 🔴 🔵 🔴 ❓ 猜猜问号位置应该是什么颜色？", "options": ["🔴 红色", "🔵 蓝色", "🟢 绿色", "🟡 黄色"], "correct": 1},
                {"dimension": "语言-表达能力", "question": "🏰 魔法城堡里有一幅画：小狗在追蝴蝶，蝴蝶飞在花丛上面。你能完整说出这幅画里发生了什么吗？", "display": "🐕🦋🌸🌸🌸", "options": ["只说了词语", "说了简单句子", "较完整描述", "完整详细描述"], "correct": 3},
                {"dimension": "情绪管理", "question": "🏰 小魔法师做魔法实验失败了，瓶子「砰」的一声爆炸了，弄得满脸都是彩色粉末。你现在的心情是？", "options": ["大哭大叫", "有点难过但继续试", "无所谓", "觉得好笑，下次小心点"], "correct": 3},
                {"dimension": "时间观念", "question": "🏰 城堡的钟显示下午3点，魔法课4点开始。还有多少时间准备？", "options": ["30分钟", "1小时", "2小时", "不知道"], "correct": 1},
                {"dimension": "运动能力", "question": "🏰 要进入城堡密室，需要走一条窄窄的独木桥。应该怎么走？", "options": ["跑过去最快", "慢慢走保持平衡", "爬过去", "不敢走"], "correct": 1}
            ]},
            3: {"name": "🎪 动物运动会", "questions": [
                {"dimension": "数学-运算", "question": "🎪 运动会上，小猴跳了3次，又跳了2次。一共跳了多少次？", "options": ["4次", "5次", "6次", "不知道"], "correct": 1},
                {"dimension": "数学-空间方位", "question": "🎪 小熊站在中间，小猫在小熊的左边，小狗在小熊的右边。小猫的右边是谁？", "display": "🐱 🐻 🐕", "options": ["小狗", "小熊", "小猫", "不知道"], "correct": 1},
                {"dimension": "社交-解决冲突", "question": "🎪 两个小朋友都想玩跷跷板，但跷跷板只能两个人玩。应该怎么办？", "options": ["抢着玩", "轮流玩每人玩一会儿", "都不玩了", "打架决定"], "correct": 1},
                {"dimension": "自理-物品整理", "question": "🎪 运动结束了，哪些东西应该放进书包？", "options": ["汗湿的毛巾和脏鞋子", "水瓶和外套", "地上的树叶", "别人的玩具"], "correct": 1},
                {"dimension": "专注力-任务完成", "question": "🎪 小乌龟要完成一个拼图，已经拼了很久还没完成。这时好朋友叫它去玩，小乌龟应该？", "options": ["马上去玩", "不开心地继续拼", "拼完再去", "把拼图弄乱"], "correct": 2}
            ]}
        }

        current_set = GAME_SETS[st.session_state.game_set]
        child_name = st.session_state.profile.get('name', '小朋友') if st.session_state.profile else '小朋友'

        if not st.session_state.game_completed:
            if st.session_state.game_question < len(current_set['questions']):
                q = current_set['questions'][st.session_state.game_question]
                phone_content = get_phone_game_question(
                    st.session_state.game_set,
                    current_set['name'],
                    st.session_state.game_question,
                    q,
                    st.session_state.get('selected_option', -1)
                )
            else:
                phone_content = get_phone_game_intro()

            phone_html = render_phone_frame(nav_title="互动评估", content=phone_content, active_tab=1, show_back=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(phone_html, unsafe_allow_html=True)

            # 选项按钮
            if st.session_state.game_question < len(current_set['questions']):
                q = current_set['questions'][st.session_state.game_question]
                st.markdown("**请让孩子选择答案：**")
                options_with_num = [f"{i+1}. {opt}" for i, opt in enumerate(q['options'])]
                selected = st.radio("孩子的选择：", options_with_num, key=f"q_{st.session_state.game_set}_{st.session_state.game_question}")

                if st.button("下一题 ➡️", use_container_width=True, type="primary"):
                    set_key = f"set{st.session_state.game_set}"
                    if set_key not in st.session_state.game_answers:
                        st.session_state.game_answers[set_key] = []
                    selected_idx = options_with_num.index(selected)
                    st.session_state.game_answers[set_key].append({
                        "dimension": q['dimension'],
                        "selected": q['options'][selected_idx],
                        "selected_idx": selected_idx,
                        "correct_idx": q['correct'],
                        "is_correct": selected_idx == q['correct']
                    })
                    st.session_state.game_question += 1
                    if st.session_state.game_question >= len(current_set['questions']):
                        if st.session_state.game_set < 3:
                            st.session_state.game_set += 1
                            st.session_state.game_question = 0
                        else:
                            st.session_state.game_completed = True
                    st.rerun()
        else:
            # 游戏完成
            phone_content = get_phone_game_result(st.session_state.ai_assessment, child_name)
            phone_html = render_phone_frame(nav_title="评估结果", content=phone_content, active_tab=1, show_back=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(phone_html, unsafe_allow_html=True)

            if not st.session_state.ai_assessment and llm_enabled():
                if st.button("📊 生成 AI 评估报告", use_container_width=True, type="primary"):
                    with st.spinner("AI 正在分析..."):
                        try:
                            agent = get_agent(0)
                            if agent:
                                answers_summary = []
                                for set_num in range(1, 4):
                                    set_key = f"set{set_num}"
                                    if set_key in st.session_state.game_answers:
                                        answers_summary.extend(st.session_state.game_answers[set_key])

                                prompt = f"""请对以下幼小衔接能力互动评估结果进行专业分析：
                                ## 孩子基本信息
                                - 姓名：{child_name}
                                - 年龄：{st.session_state.profile.get('age', 5.5) if st.session_state.profile else 5.5}岁

                                ## 孩子的作答记录
                                """
                                for i, ans in enumerate(answers_summary):
                                    prompt += f"\n第{i+1}题【{ans['dimension']}】：选择「{ans['selected']}」，{'✓正确' if ans['is_correct'] else '✗错误'}"

                                prompt += "\n请输出JSON格式：{\"scores\": {...}, \"overall_analysis\": \"...\", \"strengths\": [...], \"areas_to_improve\": [...], \"recommendations\": [...], \"message_to_parents\": \"...\"}"

                                import json, re
                                response = agent.llm.invoke(prompt)
                                json_match = re.search(r'\{.*\}', response.content, re.S)
                                if json_match:
                                    st.session_state.ai_assessment = json.loads(json_match.group())
                                    st.success("AI 评估完成！")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"AI 评估失败：{e}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 重新评估", use_container_width=True):
                    st.session_state.game_set = 1
                    st.session_state.game_question = 0
                    st.session_state.game_answers = {}
                    st.session_state.game_completed = False
                    st.session_state.ai_assessment = None
                    st.rerun()
            with col2:
                st.button("📋 去家长评估", use_container_width=True, on_click=set_menu, args=("📋 能力评估",))
    else:
        # 桌面模式
        st.title("🎮 孩子互动评估")
        st.markdown("""
        **让孩子独立完成三套趣味游戏，AI 将综合分析孩子的能力发展情况！**

        📌 **家长须知：**
        - 请让孩子独立完成，家长不要提示或帮助
        - 每套题目约 5-8 分钟，共三套
        - 完成后 AI 将生成详细的能力评估报告
        """)

    # 初始化游戏状态
    if 'game_set' not in st.session_state:
        st.session_state.game_set = 1
        st.session_state.game_question = 0
        st.session_state.game_answers = {}
        st.session_state.game_completed = False
        st.session_state.ai_assessment = None

    # 三套题目定义
    GAME_SETS = {
        1: {
            "name": "🌟 第一套：小兔子的一天",
            "theme": "跟着小兔子完成各种任务",
            "questions": [
                {
                    "type": "story",
                    "dimension": "语言-倾听理解",
                    "question": "🐰 小兔子要出门了！妈妈说：「小兔子，请先穿上鞋子，再拿上书包，然后去门口等妈妈。」",
                    "sub_question": "妈妈让小兔子按什么顺序做事？",
                    "options": ["先拿书包再穿鞋", "先穿鞋再拿书包", "直接去门口等"],
                    "correct": 1,
                },
                {
                    "type": "count",
                    "dimension": "数学-计数能力",
                    "question": "🐰 小兔子来到菜园，看到一排胡萝卜。请数一数有几根？",
                    "display": "🥕 🥕 🥕 🥕 🥕 🥕 🥕",
                    "count": 7,
                    "options": ["5根", "6根", "7根", "8根"],
                    "correct": 2
                },
                {
                    "type": "social",
                    "dimension": "社交-分享合作",
                    "question": "🐰 小兔子遇到小松鼠，小松鼠说：「我饿了，能给我一根胡萝卜吗？」如果你是小兔子，你会怎么做？",
                    "options": ["不理小松鼠，自己吃", "给小松鼠一根胡萝卜", "把胡萝卜藏起来", "跑掉"],
                    "correct": 1,
                    "evaluation": ["自私行为", "友善分享", "防御行为", "逃避行为"]
                },
                {
                    "type": "selfcare",
                    "dimension": "自理-生活技能",
                    "question": "🐰 小兔子回到家，要自己整理书包。书包里应该放这些东西，你觉得先放哪个最合适？",
                    "options": ["玩具小汽车", "故事书", "脏手帕", "糖果"],
                    "correct": 1,
                },
                {
                    "type": "focus",
                    "dimension": "专注力",
                    "question": "🐰 小兔子要做作业了。如果周围有小鸟在叫、风吹窗户的声音，你觉得小兔子应该怎么做？",
                    "options": ["去看小鸟", "去关窗户再回来做作业", "不做了出去玩", "继续专心做作业"],
                    "correct": 3,
                }
            ]
        },
        2: {
            "name": "🌈 第二套：魔法城堡探险",
            "theme": "进入魔法城堡，完成各种挑战",
            "questions": [
                {
                    "type": "pattern",
                    "dimension": "数学-逻辑推理",
                    "question": "🏰 城堡门口有一串魔法珠子：🔴 🔵 🔴 🔵 🔴 ❓ 猜猜问号位置应该是什么颜色？",
                    "options": ["🔴 红色", "🔵 蓝色", "🟢 绿色", "🟡 黄色"],
                    "correct": 1,
                },
                {
                    "type": "language",
                    "dimension": "语言-表达能力",
                    "question": "🏰 魔法城堡里有一幅画：小狗在追蝴蝶，蝴蝶飞在花丛上面。",
                    "display": "🐕🦋🌸🌸🌸",
                    "sub_question": "你能完整说出这幅画里发生了什么吗？（家长记录孩子的描述程度）",
                    "options": [
                        "只说了「小狗」或「蝴蝶」等词语",
                        "说了简单的句子，如「小狗跑」",
                        "较完整描述：「小狗在追蝴蝶」",
                        "完整详细：「小狗在追蝴蝶，蝴蝶在花丛上飞」"
                    ],
                    "correct": 3
                },
                {
                    "type": "emotion",
                    "dimension": "情绪管理",
                    "question": "🏰 小魔法师做魔法实验失败了，瓶子「砰」的一声爆炸了，弄得满脸都是彩色粉末。如果你是小魔法师，你现在的心情是？",
                    "options": ["大哭大叫", "有点难过但继续试", "无所谓", "觉得好笑，下次小心点"],
                    "correct": 3,
                },
                {
                    "type": "time",
                    "dimension": "时间观念",
                    "question": "🏰 城堡的钟显示现在是下午 3 点，魔法课 4 点开始。小魔法师还有多少时间准备？",
                    "options": ["30分钟", "1小时", "2小时", "不知道"],
                    "correct": 1
                },
                {
                    "type": "motor",
                    "dimension": "运动能力",
                    "question": "🏰 要进入城堡密室，需要走一条窄窄的独木桥。小魔法师应该怎么走？",
                    "options": ["跑过去最快", "慢慢走，保持平衡", "爬过去", "不敢走"],
                    "correct": 1,
                }
            ]
        },
        3: {
            "name": "🎪 第三套：动物运动会",
            "theme": "参加动物运动会，展示各种能力",
            "questions": [
                {
                    "type": "math",
                    "dimension": "数学-运算",
                    "question": "🎪 运动会上，小猴跳了3次，又跳了2次。小猴一共跳了多少次？",
                    "options": ["4次", "5次", "6次", "不知道"],
                    "correct": 1
                },
                {
                    "type": "space",
                    "dimension": "数学-空间方位",
                    "question": "🎪 小熊站在中间，小猫在小熊的左边，小狗在小熊的右边。小猫的右边是谁？",
                    "display": "🐱 🐻 🐕",
                    "options": ["小狗", "小熊", "小猫", "不知道"],
                    "correct": 1
                },
                {
                    "type": "social2",
                    "dimension": "社交-解决冲突",
                    "question": "🎪 两个小朋友都想玩跷跷板，但跷跷板只能两个人玩。他们应该怎么办？",
                    "options": ["抢着玩，谁抢到谁玩", "轮流玩，每人玩一会儿", "都不玩了", "打架决定"],
                    "correct": 1,
                },
                {
                    "type": "selfcare2",
                    "dimension": "自理-物品整理",
                    "question": "🎪 运动结束了，小动物们要把东西放回原位。下面哪些东西应该放进书包？",
                    "options": ["汗湿的毛巾和脏鞋子", "水瓶和外套", "地上的树叶", "别人的玩具"],
                    "correct": 1,
                },
                {
                    "type": "attention",
                    "dimension": "专注力-任务完成",
                    "question": "🎪 小乌龟要完成一个拼图，已经拼了很久还没完成。这时好朋友叫它去玩，小乌龟应该？",
                    "options": ["马上放下拼图去玩", "说不去了，继续拼但很不开心", "说「等我拼完再去」，然后专心完成拼图", "把拼图弄乱不玩了"],
                    "correct": 2,
                }
            ]
        }
    }

    # 获取当前套题信息
    current_set = GAME_SETS[st.session_state.game_set]
    total_sets = len(GAME_SETS)

    # 显示进度
    st.markdown(f"### {current_set['name']}")
    st.caption(f"主题：{current_set['theme']}")

    progress = (st.session_state.game_set - 1) * 5 + st.session_state.game_question
    total_questions = total_sets * 5
    st.progress(progress / total_questions)
    st.markdown(f"<p style='text-align: center;'>总进度：第 {st.session_state.game_set} 套 / 共 {total_sets} 套 · 第 {st.session_state.game_question + 1} 题 / 每套 5 题</p>", unsafe_allow_html=True)

    st.markdown("---")

    # 游戏未完成时显示题目
    if not st.session_state.game_completed:
        if st.session_state.game_question < len(current_set['questions']):
            q = current_set['questions'][st.session_state.game_question]

            st.markdown(f"**第 {st.session_state.game_question + 1} 题**（测试：{q['dimension']}）")
            st.markdown(f"### {q['question']}")

            if 'display' in q:
                st.markdown(f"<div style='font-size: 50px; text-align: center; padding: 20px; background: #f5f5f5; border-radius: 15px; margin: 15px 0;'>{q['display']}</div>", unsafe_allow_html=True)

            if 'sub_question' in q:
                st.info(f"💡 {q['sub_question']}")

            st.markdown("**请让孩子选择答案：**")
            options_with_num = [f"{i+1}. {opt}" for i, opt in enumerate(q['options'])]
            selected = st.radio("孩子的选择：", options_with_num, key=f"q_{st.session_state.game_set}_{st.session_state.game_question}")
            selected_idx = options_with_num.index(selected)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("下一题 ➡️", use_container_width=True, type="primary"):
                    set_key = f"set{st.session_state.game_set}"
                    if set_key not in st.session_state.game_answers:
                        st.session_state.game_answers[set_key] = []

                    answer_record = {
                        "dimension": q['dimension'],
                        "question": q['question'][:50],
                        "selected": q['options'][selected_idx],
                        "selected_idx": selected_idx,
                        "correct_idx": q['correct'],
                        "is_correct": selected_idx == q['correct'],
                        "evaluation": q.get('evaluation', [""] * len(q['options']))[selected_idx] if 'evaluation' in q else ""
                    }
                    st.session_state.game_answers[set_key].append(answer_record)

                    st.session_state.game_question += 1

                    if st.session_state.game_question >= len(current_set['questions']):
                        if st.session_state.game_set < total_sets:
                            st.session_state.game_set += 1
                            st.session_state.game_question = 0
                        else:
                            st.session_state.game_completed = True

                    st.rerun()
        else:
            st.session_state.game_completed = True
            st.rerun()

    # 游戏完成，显示 AI 评估
    else:
        st.markdown("## 🎉 太棒了！所有游戏已完成！")

        # 准备 AI 评估数据
        answers_summary = []
        for set_num in range(1, 4):
            set_key = f"set{set_num}"
            if set_key in st.session_state.game_answers:
                answers_summary.extend(st.session_state.game_answers[set_key])

        child_name = st.session_state.profile.get('name', '小朋友') if st.session_state.profile else '小朋友'
        child_age = st.session_state.profile.get('age', 5.5) if st.session_state.profile else 5.5

        # 构建 AI 提示词
        prompt = f"""请对以下幼小衔接能力互动评估结果进行专业分析：

## 孩子基本信息
- 姓名：{child_name}
- 年龄：{child_age}岁

## 评估背景
这是一套针对5-6岁儿童的幼小衔接能力互动评估游戏，共三套题目（15题）：
1. 第一套「小兔子的一天」：通过生活场景测试倾听理解、计数、社交分享、自理、专注力
2. 第二套「魔法城堡探险」：通过冒险场景测试逻辑推理、表达、情绪管理、时间观念、运动能力
3. 第三套「动物运动会」：通过运动场景测试运算、空间方位、冲突解决、整理、任务坚持

## 孩子的作答记录
"""
        for i, ans in enumerate(answers_summary):
            prompt += f"\n第{i+1}题【{ans['dimension']}】：选择「{ans['selected']}」，{'✓正确' if ans['is_correct'] else '✗错误'}"
            if ans.get('evaluation'):
                prompt += f"，行为评价：{ans['evaluation']}"

        prompt += """

## 请分析并输出JSON格式结果：
{
  "scores": {"语言能力": 4, "数学能力": 3, "社交能力": 4, "自理能力": 3, "运动能力": 4, "专注力": 3, "情绪管理": 4, "时间观念": 3},
  "overall_analysis": "整体分析...",
  "strengths": ["优势1", "优势2"],
  "areas_to_improve": ["需加强1"],
  "recommendations": ["建议1", "建议2"],
  "message_to_parents": "给家长的寄语..."
}
"""

        if llm_enabled():
            if st.button("📊 生成 AI 评估报告", use_container_width=True, type="primary"):
                with st.spinner("AI 正在分析孩子的表现..."):
                    try:
                        agent = get_agent(0)
                        if agent:
                            import json
                            import re
                            response = agent.llm.invoke(prompt)
                            raw_content = response.content

                            if isinstance(raw_content, str):
                                json_match = re.search(r'\{.*\}', raw_content, re.S)
                                if json_match:
                                    ai_result = json.loads(json_match.group())
                                    st.session_state.ai_assessment = ai_result
                                    st.success("AI 评估完成！")
                                    st.rerun()
                    except Exception as e:
                        st.error(f"AI 评估失败：{e}")
        else:
            st.warning("未配置 LLM API Key，无法进行 AI 评估。")

        # 显示 AI 结果
        if st.session_state.ai_assessment:
            result = st.session_state.ai_assessment
            st.markdown("---")
            st.markdown("## 📋 AI 评估报告")

            if 'scores' in result:
                st.markdown("### 📊 能力得分")
                cols = st.columns(4)
                for i, (dim, score) in enumerate(result['scores'].items()):
                    with cols[i % 4]:
                        color = "🟢" if score >= 4 else "🟡" if score >= 3 else "🔴"
                        st.metric(dim, f"{color} {score}/5")

            for section, title in [('overall_analysis', '🔍 整体分析'), ('strengths', '✨ 优势领域'), ('areas_to_improve', '📌 需要加强'), ('recommendations', '💡 训练建议')]:
                if section in result and result[section]:
                    st.markdown(f"### {title}")
                    content = result[section]
                    if isinstance(content, list):
                        for item in content:
                            st.markdown(f"- {item}")
                    else:
                        st.info(content) if '分析' in title else st.success(content)

            if 'message_to_parents' in result:
                st.markdown("### 💝 给家长的寄语")
                st.success(result['message_to_parents'])

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 重新评估", use_container_width=True):
                st.session_state.game_set = 1
                st.session_state.game_question = 0
                st.session_state.game_answers = {}
                st.session_state.game_completed = False
                st.session_state.ai_assessment = None
                st.rerun()
        with col2:
            st.button(
                "📋 去家长评估 →",
                use_container_width=True,
                on_click=set_menu,
                args=("📋 能力评估",),
            )

# ==================== 生成计划 ====================
elif menu == "📅 生成计划":
    if st.session_state.phone_mode:
        # 手机模式
        from phone_components import render_phone_frame, get_phone_plan_content

        if not st.session_state.profile:
            phone_content = """<div class="mini-card" style="text-align: center;"><div style="font-size: 48px;">📋</div><div style="font-size: 16px; color: #666; margin-top: 12px;">请先完成能力评估</div></div>"""
            phone_html = render_phone_frame(nav_title="生成计划", content=phone_content, active_tab=2)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(phone_html, unsafe_allow_html=True)
            st.markdown("---")
            if st.button("📋 去评估", use_container_width=True):
                set_menu("📋 能力评估")
                st.rerun()
        else:
            phone_content = get_phone_plan_content(st.session_state.profile, st.session_state.plan)
            phone_html = render_phone_frame(nav_title="生成计划", content=phone_content, active_tab=2)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(phone_html, unsafe_allow_html=True)

            # 生成计划按钮
            st.markdown("---")
            if not st.session_state.plan:
                if st.button("生成个性化计划", use_container_width=True, type="primary"):
                    if llm_enabled():
                        with st.spinner("正在生成..."):
                            try:
                                agent = get_agent(os.path.getmtime("kindergarten_agent_full.py"))
                                if agent:
                                    child_profile = agent.build_profile(st.session_state.profile)
                                    st.session_state.plan = agent.generate_plan(child_profile)
                                    st.success("计划生成成功！")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"生成失败：{e}")
                    else:
                        st.session_state.plan = {
                            "weekly_goals": ["培养阅读习惯", "锻炼自理能力", "加强数学思维", "提升专注力"],
                            "daily_activities": [
                                {"time": "早上", "activity": "亲子阅读15分钟"},
                                {"time": "下午", "activity": "益智游戏30分钟"},
                                {"time": "傍晚", "activity": "户外运动30分钟"},
                                {"time": "睡前", "activity": "整理书包"}
                            ]
                        }
                        st.success("示例计划已生成！")
                        st.rerun()

            # 显示详细计划
            if st.session_state.plan:
                render_plan(st.session_state.plan)

                st.markdown("""
                <div class="info-box">
                    <h4>📌 家长注意事项</h4>
                    <ul>
                        <li>每天坚持，形成习惯</li>
                        <li>多鼓励、少批评</li>
                        <li>保持耐心，循序渐进</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                st.button("💬 有问题去咨询 →", use_container_width=True, on_click=set_menu, args=("💬 问答咨询",))
    else:
        # 桌面模式
        st.title("📅 幼小衔接计划")

        if not st.session_state.profile:
            st.warning("请先完成能力评估")
            st.button(
                "去评估 →",
                on_click=set_menu,
                args=("📋 能力评估",),
            )
        else:
            st.markdown(f"### 👶 {st.session_state.profile['name']}的个性化计划")

            if llm_enabled():
                if st.button("生成个性化计划", use_container_width=True, type="primary"):
                    with st.spinner("正在生成个性化计划，请稍候..."):
                        try:
                            agent = get_agent(os.path.getmtime("kindergarten_agent_full.py"))
                            if agent is None:
                                show_error("llm_connection_error")
                            else:
                                child_profile = agent.build_profile(st.session_state.profile)
                                st.session_state.plan = agent.generate_plan(child_profile)
                                st.success("计划生成成功！")
                        except Exception as exc:
                            logger.error(f"计划生成失败: {exc}")
                            show_error("plan_generation_error", exc)

                if st.session_state.plan:
                    render_plan(st.session_state.plan)
                else:
                    st.info("点击上方按钮生成个性化计划。")
            else:
                st.warning("未检测到 OPENAI_API_KEY，显示示例计划。")
                st.markdown("""
                ### 第一周：习惯养成
                | 时间 | 活动 | 目标 |
                |------|------|------|
                | 早晨 | 亲子阅读15分钟 | 语言发展 |
                | 下午 | 益智游戏 | 数学思维 |
                | 傍晚 | 户外运动30分钟 | 体能发展 |
                | 睡前 | 整理书包 | 自理能力 |

                ### 第二周：能力提升
                | 时间 | 活动 | 目标 |
                |------|------|------|
                | 早晨 | 讲述昨天的事情 | 语言表达 |
                | 下午 | 简单加减法游戏 | 数学运算 |
                | 傍晚 | 与同伴游戏 | 社交能力 |
                | 睡前 | 整理衣物 | 自理能力 |

                ### 第三周：综合训练
                ### 第四周：巩固强化
                """)

            st.markdown("""
            <div class="info-box">
                <h4>📌 家长注意事项</h4>
                <ul>
                    <li>每天坚持，形成习惯</li>
                    <li>多鼓励、少批评</li>
                    <li>保持耐心，循序渐进</li>
                    <li>定期回顾调整</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.button(
                "有更多问题？去问答咨询 →",
                use_container_width=True,
                on_click=set_menu,
                args=("💬 问答咨询",),
            )

# ==================== 问答咨询 ====================
elif menu == "💬 问答咨询":
    if st.session_state.phone_mode:
        # 手机模式
        from phone_components import render_phone_frame, get_phone_qa_content

        phone_content = get_phone_qa_content(st.session_state.get('chat_history', []))
        phone_html = render_phone_frame(nav_title="问答咨询", content=phone_content, active_tab=3)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(phone_html, unsafe_allow_html=True)

        # 常见问题按钮
        st.markdown("---")
        st.markdown("### 常见问题")
        common_questions = [
            "要不要提前学小学内容？",
            "孩子不想去小学怎么办？",
            "孩子注意力不集中怎么办？",
            "如何培养时间观念？"
        ]
        cols = st.columns(2)
        for i, q in enumerate(common_questions):
            with cols[i % 2]:
                if st.button(q, key=f"phone_q_{i}"):
                    st.session_state['current_question'] = q

        # 问答输入
        st.markdown("### 提问")
        default_value = st.session_state.get('current_question', "")
        question = st.text_area("请输入你的问题", value=default_value, height=80)

        if st.button("获取回答", use_container_width=True, type="primary"):
            if question:
                with st.spinner("正在思考..."):
                    if llm_enabled():
                        try:
                            agent = get_agent(os.path.getmtime("kindergarten_agent_full.py"))
                            if agent:
                                answer = agent.chat(question)
                            else:
                                answer = local_answer(question)
                        except Exception as e:
                            answer = local_answer(question)
                    else:
                        answer = local_answer(question)

                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []
                    st.session_state.chat_history.append({"question": question, "answer": answer})
                    st.session_state['current_question'] = ""

                st.markdown("### 💡 回答")
                st.markdown(answer)

        # 显示对话历史
        if st.session_state.get('chat_history'):
            st.markdown("---")
            st.markdown("### 📜 对话历史")
            for item in reversed(st.session_state.chat_history[-3:]):
                with st.expander(f"Q: {item['question'][:25]}..."):
                    st.markdown(f"**问：** {item['question']}")
                    st.markdown(f"**答：** {item['answer']}")
    else:
        # 桌面模式
        st.title("💬 问答咨询")
        st.markdown("有什么关于幼小衔接的问题，欢迎提问")

        # 常见问题快速入口
        st.markdown("### 常见问题")
        common_questions = [
            "要不要提前学小学内容？",
            "孩子不想去小学怎么办？",
            "孩子注意力不集中怎么办？",
            "如何培养时间观念？",
            "需要提前学拼音吗？"
        ]

        cols = st.columns(2)
        for i, q in enumerate(common_questions):
            with cols[i % 2]:
                if st.button(q, key=f"q_{i}"):
                    st.session_state['current_question'] = q

        # 问答输入
        st.markdown("---")
        st.markdown("### 提问")

        if 'current_question' in st.session_state:
            default_value = st.session_state['current_question']
        else:
            default_value = ""

        question = st.text_area("请输入你的问题", value=default_value, height=100)

        if st.button("获取回答", use_container_width=True):
            if question:
                with st.spinner("正在思考，请稍候..."):
                    if llm_enabled():
                        try:
                            agent = get_agent(os.path.getmtime("kindergarten_agent_full.py"))
                            if agent is None:
                                show_error("llm_connection_error")
                                answer = local_answer(question)
                            else:
                                answer = agent.chat(question)
                                # 保存对话历史
                                if 'chat_history' not in st.session_state:
                                    st.session_state.chat_history = []
                                st.session_state.chat_history.append({
                                    "question": question,
                                    "answer": answer
                                })
                        except Exception as exc:
                            logger.error(f"问答失败: {exc}")
                            show_error("chat_error", exc)
                            answer = local_answer(question)
                    else:
                        answer = local_answer(question)

                    st.markdown("### 💡 回答")
                    st.markdown(answer)

        # 显示对话历史
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 📜 对话历史")
            for i, item in enumerate(reversed(st.session_state.chat_history[-5:])):  # 只显示最近5条
                with st.expander(f"Q: {item['question'][:30]}...", expanded=(i == 0)):
                    st.markdown(f"**问：** {item['question']}")
                    st.markdown(f"**答：** {item['answer']}")

if __name__ == "__main__":
    pass
