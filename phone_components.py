"""
手机模拟器组件
提供微信小程序风格的界面渲染
"""

from typing import List, Dict, Any

# Tab 配置
TABS = [
    ("🏠", "首页", "🏠 首页"),
    ("📋", "评估", "📋 能力评估"),
    ("📅", "计划", "📅 生成计划"),
    ("💬", "问答", "💬 问答咨询"),
]

def render_phone_frame(nav_title: str, content: str, active_tab: int = 0, show_back: bool = False) -> str:
    """渲染手机框架

    Args:
        nav_title: 导航栏标题
        content: 页面内容 HTML
        active_tab: 当前激活的 tab (0-3)
        show_back: 是否显示返回按钮
    """
    from datetime import datetime

    time_str = datetime.now().strftime("%H:%M")
    back_icon = "←" if show_back else ""

    tab_html = ""
    for i, (icon, name, _) in enumerate(TABS):
        active_class = "active" if i == active_tab else ""
        tab_html += f'<div class="mini-tab-item {active_class}"><span class="tab-icon">{icon}</span><span>{name}</span></div>'

    # 使用字符串拼接而不是 format，避免花括号问题
    html = f'''<div class="phone-container">
    <div class="phone-notch"></div>
    <div class="phone-screen">
        <div class="mini-status-bar">
            <span>{time_str}</span>
            <span>🔋 85%</span>
        </div>
        <div class="mini-nav-bar">
            <span class="nav-back">{back_icon}</span>
            <span>{nav_title}</span>
        </div>
        <div class="mini-content">
            {content}
        </div>
        <div class="mini-tab-bar">
            {tab_html}
        </div>
    </div>
</div>'''

    return html


# 首页内容模板
HOME_CONTENT = """
<div class="mini-card" style="text-align: center; padding: 20px;">
    <div style="font-size: 48px; margin-bottom: 12px;">🎒</div>
    <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 8px;">小桥</div>
    <div style="font-size: 13px; color: #999;">幼小衔接规划助手</div>
</div>

<div class="mini-card">
    <div class="mini-card-title">🎯 核心功能</div>
    <div class="mini-card-content">
        <div class="mini-list-item" onclick="startAssessment()">
            <span style="font-size: 20px; margin-right: 10px;">📋</span>
            <div>
                <div style="font-weight: 500;">能力评估</div>
                <div style="font-size: 12px; color: #999;">评估孩子五大能力发展</div>
            </div>
        </div>
        <div class="mini-list-item">
            <span style="font-size: 20px; margin-right: 10px;">🎮</span>
            <div>
                <div style="font-weight: 500;">互动评估</div>
                <div style="font-size: 12px; color: #999;">趣味游戏测真实能力</div>
            </div>
        </div>
        <div class="mini-list-item">
            <span style="font-size: 20px; margin-right: 10px;">📅</span>
            <div>
                <div style="font-weight: 500;">个性化计划</div>
                <div style="font-size: 12px; color: #999;">AI 生成衔接计划</div>
            </div>
        </div>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">💡 使用指南</div>
    <div class="mini-card-content">
        <p>1. 完成能力评估</p>
        <p>2. 可选互动游戏评估</p>
        <p>3. 生成个性化计划</p>
        <p>4. 有问题随时咨询</p>
    </div>
</div>

<button class="mini-btn" onclick="startAssessment()">开始评估 →</button>
"""

# 评估页内容模板
def get_assessment_content(page: int, total_pages: int, form_data: dict) -> str:
    """生成评估页内容"""
    progress = page / total_pages * 100

    content = f"""
<div class="mini-card">
    <div class="mini-card-title">能力评估</div>
    <div class="mini-progress">
        <div class="mini-progress-bar" style="width: {progress}%"></div>
    </div>
    <div style="text-align: center; font-size: 12px; color: #999;">
        第 {page} / {total_pages} 页
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">👶 基本信息</div>
    <input type="text" class="mini-input" placeholder="请输入孩子姓名" value="{form_data.get('name', '')}">
    <div style="display: flex; gap: 10px;">
        <input type="number" class="mini-input" placeholder="年龄" value="{form_data.get('age', 5.5)}" style="width: 50%;">
    </div>
</div>
"""
    return content


# 评估结果内容模板
def get_result_content(profile: dict, result: dict) -> str:
    """生成评估结果内容"""
    level = result.get('overall_level', '良好')
    level_class = 'mini-tag' if level == '优秀' else 'mini-tag-warning' if level == '良好' else 'mini-tag-danger'

    content = f"""
<div class="mini-card" style="text-align: center;">
    <div style="font-size: 16px; color: #666;">{profile.get('name', '小朋友')}的评估报告</div>
    <div class="mini-score">{level}</div>
    <span class="{level_class}">整体水平</span>
</div>

<div class="mini-card">
    <div class="mini-card-title">✨ 优势</div>
    <div class="mini-card-content">
"""
    for s in result.get('strengths', ['暂无']):
        content += f"<p>• {s}</p>"

    content += """
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">📌 需加强</div>
    <div class="mini-card-content">
"""
    for a in result.get('areas_to_improve', ['暂无']):
        content += f"<p>• {a}</p>"

    content += """
    </div>
</div>

<button class="mini-btn">生成个性化计划 →</button>
"""
    return content


# 计划内容模板
def get_plan_content(profile: dict, plan: dict) -> str:
    """生成计划内容"""
    content = f"""
<div class="mini-card">
    <div class="mini-card-title">📅 个性化计划</div>
    <div style="font-size: 13px; color: #666;">
        为 {profile.get('name', '小朋友')} 定制
    </div>
</div>
"""

    if plan:
        weekly_goals = plan.get('weekly_goals', [])
        if weekly_goals:
            content += """
<div class="mini-card">
    <div class="mini-card-title">🎯 每周目标</div>
    <div class="mini-card-content">
"""
            for i, goal in enumerate(weekly_goals[:4], 1):
                content += f"<p>{i}. {goal}</p>"
            content += "    </div>\n</div>"

        daily_activities = plan.get('daily_activities', [])
        if daily_activities:
            content += """
<div class="mini-card">
    <div class="mini-card-title">📋 每日活动</div>
    <div class="mini-card-content">
"""
            for act in daily_activities[:5]:
                time = act.get('time', '')
                activity = act.get('activity', '')
                content += f"<p><strong>{time}</strong> - {activity}</p>"
            content += "    </div>\n</div>"
    else:
        content += """
<div class="mini-card">
    <div class="mini-card-content" style="text-align: center; color: #999;">
        点击下方按钮生成计划
    </div>
</div>
<button class="mini-btn">生成个性化计划</button>
"""

    return content


# 问答内容模板
QA_CONTENT = """
<div class="mini-card">
    <div class="mini-card-title">💬 常见问题</div>
    <div class="mini-card-content">
        <div class="mini-list-item">
            <span>要不要提前学小学内容？</span>
            <span style="color: #999;">→</span>
        </div>
        <div class="mini-list-item">
            <span>孩子注意力不集中怎么办？</span>
            <span style="color: #999;">→</span>
        </div>
        <div class="mini-list-item">
            <span>如何培养时间观念？</span>
            <span style="color: #999;">→</span>
        </div>
        <div class="mini-list-item">
            <span>孩子不想去小学怎么办？</span>
            <span style="color: #999;">→</span>
        </div>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">📝 我要提问</div>
    <textarea class="mini-input" placeholder="请输入你的问题..." style="height: 80px; resize: none;"></textarea>
    <button class="mini-btn">获取回答</button>
</div>
"""

# 互动评估内容模板
def get_game_content(set_num: int, question_num: int, question: dict, total_sets: int = 3) -> str:
    """生成互动评估内容"""
    progress = ((set_num - 1) * 5 + question_num) / (total_sets * 5) * 100

    content = f"""
<div class="mini-card" style="text-align: center;">
    <div style="font-size: 48px;">🎮</div>
    <div style="font-size: 16px; font-weight: bold;">互动评估</div>
</div>

<div class="mini-card">
    <div class="mini-progress">
        <div class="mini-progress-bar" style="width: {progress}%"></div>
    </div>
    <div style="text-align: center; font-size: 12px; color: #999;">
        第 {set_num} 套 · 第 {question_num + 1} 题
    </div>
</div>

<div class="mini-card">
    <div style="font-size: 12px; color: #4CAF50; margin-bottom: 8px;">
        {question.get('dimension', '')}
    </div>
    <div class="mini-card-content" style="font-size: 14px; line-height: 1.6;">
        {question.get('question', '')}
    </div>
</div>
"""

    if 'display' in question:
        content += f"""
<div class="mini-card" style="text-align: center; font-size: 32px;">
    {question['display']}
</div>
"""

    options = question.get('options', [])
    for i, opt in enumerate(options):
        content += f"""
<div class="mini-list-item" style="cursor: pointer;">
    <span style="margin-right: 10px;">{i + 1}.</span>
    <span>{opt}</span>
</div>
"""

    content += """
<button class="mini-btn" style="margin-top: 20px;">下一题 →</button>
"""

    return content


# ========== 新增：手机模式专用模板函数 ==========

def get_phone_assessment_page(page: int, total_pages: int, form_data: dict) -> str:
    """生成手机模式的评估页面内容"""
    progress = page / total_pages * 100

    content = f"""
<div class="mini-card">
    <div class="mini-card-title">📋 能力评估</div>
    <div class="mini-progress">
        <div class="mini-progress-bar" style="width: {progress}%"></div>
    </div>
    <div style="text-align: center; font-size: 12px; color: #999;">
        第 {page} / {total_pages} 页
    </div>
</div>
"""

    # 第一页：基本信息 + 语言能力（部分）
    if page == 1:
        content += f"""
<div class="mini-card">
    <div class="mini-card-title">👶 基本信息</div>
    <input type="text" class="mini-input" placeholder="请输入孩子姓名" value="{form_data.get('name', '')}">
    <input type="number" class="mini-input" placeholder="年龄" value="{form_data.get('age', 5.5)}" style="width: 50%;">
</div>

<div class="mini-card">
    <div class="mini-card-title">📚 语言能力</div>
    <div style="font-size: 13px; color: #666; margin-bottom: 8px;">👂 倾听理解能力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 只能听懂简单词语</p>
        <p>2. 能听懂简单指令</p>
        <p>3. 能听懂日常对话 ✓</p>
        <p>4. 能听懂复杂指令</p>
        <p>5. 准确执行各种指令</p>
    </div>
</div>
"""

    # 第二页：语言能力续 + 数学能力
    elif page == 2:
        content += f"""
<div class="mini-card">
    <div class="mini-card-title">📚 语言能力（续）</div>
    <div style="font-size: 13px; color: #666; margin-bottom: 8px;">📖 阅读习惯</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 不太愿意听故事</p>
        <p>2. 愿意听故事但注意力短</p>
        <p>3. 喜欢听故事 ✓</p>
        <p>4. 有阅读兴趣</p>
        <p>5. 非常喜欢阅读</p>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">🔢 数学能力</div>
    <div style="font-size: 13px; color: #666; margin-bottom: 8px;">🔢 数数能力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 能数到10但常跳数</p>
        <p>2. 能数到10基本手口一致</p>
        <p>3. 能数到20 ✓</p>
        <p>4. 能数到20以上</p>
        <p>5. 能数到100</p>
    </div>
</div>
"""

    # 第三页：数学能力续 + 社交自理
    elif page == 3:
        content += """
<div class="mini-card">
    <div class="mini-card-title">🔢 数学能力（续）</div>
    <div style="font-size: 13px; color: #666; margin-bottom: 8px;">➕ 计算能力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 不太理解加减</p>
        <p>2. 能数实物简单加减</p>
        <p>3. 能做5以内加减 ✓</p>
        <p>4. 能做10以内加减</p>
        <p>5. 能做20以内加减</p>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">👫 社交能力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 较害羞不愿交往</p>
        <p>2. 愿意玩但不会加入</p>
        <p>3. 能与同伴一起玩 ✓</p>
        <p>4. 能主动交往合作</p>
        <p>5. 社交能力强</p>
    </div>
</div>
"""

    # 第四页：自理运动
    elif page == 4:
        content += """
<div class="mini-card">
    <div class="mini-card-title">🧹 自理能力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 依赖大人较多</p>
        <p>2. 能做简单事情</p>
        <p>3. 基本能自己穿脱衣服 ✓</p>
        <p>4. 能自己整理书包</p>
        <p>5. 自理能力强</p>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">🏃 运动能力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>选择最符合的描述：</p>
        <p>1. 发展较慢</p>
        <p>2. 基本运动，精细动作稍弱</p>
        <p>3. 运动能力发展正常 ✓</p>
        <p>4. 运动能力强</p>
        <p>5. 运动能力突出</p>
    </div>
</div>
"""

    # 第五页：新增维度
    elif page == 5:
        content += """
<div class="mini-card">
    <div class="mini-card-title">🎯 专注力</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>孩子能专注多长时间？</p>
        <p>1. 不到5分钟</p>
        <p>2. 5-10分钟</p>
        <p>3. 10-15分钟 ✓</p>
        <p>4. 15-20分钟</p>
        <p>5. 20分钟以上</p>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">😊 情绪管理</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>孩子情绪控制能力？</p>
        <p>1. 经常哭闹发脾气</p>
        <p>2. 情绪不太稳定</p>
        <p>3. 基本能表达情绪 ✓</p>
        <p>4. 能较好控制情绪</p>
        <p>5. 情绪稳定能自我调节</p>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">⏰ 时间观念</div>
    <div class="mini-card-content" style="font-size: 12px;">
        <p>孩子对时间的理解？</p>
        <p>1. 没有时间概念</p>
        <p>2. 知道早晚但不太守时</p>
        <p>3. 知道快慢基本按时 ✓</p>
        <p>4. 会看钟表守时</p>
        <p>5. 时间观念强</p>
    </div>
</div>
"""

    content += f"""
<button class="mini-btn">{'提交评估' if page == total_pages else '下一页 →'}</button>
"""

    return content


def get_phone_game_intro() -> str:
    """生成手机模式的互动评估介绍页"""
    return """
<div class="mini-card" style="text-align: center;">
    <div style="font-size: 64px;">🎮</div>
    <div style="font-size: 18px; font-weight: bold; margin: 12px 0;">孩子互动评估</div>
    <div style="font-size: 13px; color: #666;">
        让孩子独立完成三套趣味游戏<br>
        AI 将综合分析能力发展
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">📌 家长须知</div>
    <div class="mini-card-content">
        <p>• 请让孩子独立完成</p>
        <p>• 家长不要提示或帮助</p>
        <p>• 每套题目约 5-8 分钟</p>
        <p>• 共三套，完成后 AI 评估</p>
    </div>
</div>

<div class="mini-card">
    <div class="mini-card-title">🎯 评估内容</div>
    <div class="mini-card-content">
        <p><strong>第一套：</strong>小兔子的一天</p>
        <p><strong>第二套：</strong>魔法城堡探险</p>
        <p><strong>第三套：</strong>动物运动会</p>
    </div>
</div>

<button class="mini-btn">开始游戏 →</button>
"""


def get_phone_game_question(set_num: int, set_name: str, question_num: int,
                            question: dict, selected_idx: int = -1) -> str:
    """生成手机模式的互动评估题目页"""
    total_questions = 15
    current_question = (set_num - 1) * 5 + question_num + 1
    progress = current_question / total_questions * 100

    content = f"""
<div class="mini-card">
    <div style="font-size: 14px; color: #4CAF50; font-weight: bold;">{set_name}</div>
    <div class="mini-progress" style="margin: 8px 0;">
        <div class="mini-progress-bar" style="width: {progress}%"></div>
    </div>
    <div style="text-align: center; font-size: 12px; color: #999;">
        第 {current_question} / {total_questions} 题
    </div>
</div>

<div class="mini-card">
    <div style="font-size: 12px; color: #4CAF50; margin-bottom: 8px;">
        📝 {question.get('dimension', '')}
    </div>
    <div style="font-size: 14px; line-height: 1.6;">
        {question.get('question', '')}
    </div>
</div>
"""

    if 'display' in question:
        content += f"""
<div class="mini-card" style="text-align: center; font-size: 36px; padding: 15px;">
    {question['display']}
</div>
"""

    if 'sub_question' in question:
        content += f"""
<div class="mini-card" style="background: #e8f5e9; padding: 10px;">
    <div style="font-size: 12px; color: #4CAF50;">💡 {question['sub_question']}</div>
</div>
"""

    content += """<div class="mini-card" style="padding: 0;">"""

    options = question.get('options', [])
    for i, opt in enumerate(options):
        selected_class = " background: #e8f5e9;" if i == selected_idx else ""
        check_mark = " ✓" if i == selected_idx else ""
        content += f"""
<div class="mini-list-item" style="cursor: pointer;{selected_class}">
    <span style="margin-right: 10px; color: #4CAF50; font-weight: bold;">{i + 1}.</span>
    <span>{opt}{check_mark}</span>
</div>
"""

    content += "</div>"

    if selected_idx >= 0:
        content += """<button class="mini-btn" style="margin-top: 15px;">下一题 →</button>"""

    return content


def get_phone_game_result(ai_result: dict = None, child_name: str = "小朋友") -> str:
    """生成手机模式的互动评估结果页"""
    content = f"""
<div class="mini-card" style="text-align: center;">
    <div style="font-size: 64px;">🎉</div>
    <div style="font-size: 18px; font-weight: bold; margin: 12px 0;">太棒了！全部完成！</div>
    <div style="font-size: 13px; color: #666;">
        {child_name}完成了所有游戏
    </div>
</div>
"""

    if ai_result:
        if 'scores' in ai_result:
            content += """<div class="mini-card"><div class="mini-card-title">📊 能力得分</div><div style="display: flex; flex-wrap: wrap; gap: 8px;">"""
            for dim, score in ai_result['scores'].items():
                color = "#4CAF50" if score >= 4 else "#FF9800" if score >= 3 else "#F44336"
                content += f"""<div style="background: #f5f5f5; padding: 8px 12px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 11px; color: #666;">{dim}</div>
                    <div style="font-size: 16px; font-weight: bold; color: {color};">{score}/5</div>
                </div>"""
            content += "</div></div>"

        if 'overall_analysis' in ai_result:
            content += f"""<div class="mini-card"><div class="mini-card-title">🔍 整体分析</div><div class="mini-card-content">{ai_result['overall_analysis']}</div></div>"""

        if 'strengths' in ai_result and ai_result['strengths']:
            content += """<div class="mini-card"><div class="mini-card-title">✨ 优势领域</div><div class="mini-card-content">"""
            for s in ai_result['strengths']:
                content += f"<p>• {s}</p>"
            content += "</div></div>"

        if 'message_to_parents' in ai_result:
            content += f"""<div class="mini-card" style="background: #e8f5e9;"><div class="mini-card-title">💝 给家长的寄语</div><div class="mini-card-content">{ai_result['message_to_parents']}</div></div>"""
    else:
        content += """
<div class="mini-card">
    <div class="mini-card-content" style="text-align: center; color: #666;">
        点击下方按钮生成 AI 评估报告
    </div>
</div>
<button class="mini-btn">📊 生成 AI 评估报告</button>
"""

    return content


def get_phone_plan_content(profile: dict, plan: dict) -> str:
    """生成手机模式的计划页面"""
    content = f"""
<div class="mini-card">
    <div class="mini-card-title">📅 个性化计划</div>
    <div style="font-size: 13px; color: #666;">
        为 {profile.get('name', '小朋友')} 定制
    </div>
</div>
"""

    if plan:
        weekly_goals = plan.get('weekly_goals', [])
        if weekly_goals:
            content += """<div class="mini-card"><div class="mini-card-title">🎯 每周目标</div><div class="mini-card-content">"""
            for i, goal in enumerate(weekly_goals[:4], 1):
                content += f"<p>{i}. {goal}</p>"
            content += "</div></div>"

        daily_activities = plan.get('daily_activities', [])
        if daily_activities:
            content += """<div class="mini-card"><div class="mini-card-title">📋 每日活动</div><div class="mini-card-content">"""
            for act in daily_activities[:5]:
                time = act.get('time', '')
                activity = act.get('activity', '')
                content += f"<p><strong>{time}</strong> - {activity}</p>"
            content += "</div></div>"
    else:
        content += """
<div class="mini-card">
    <div class="mini-card-content" style="text-align: center; color: #999; padding: 20px;">
        点击下方按钮生成计划
    </div>
</div>
<button class="mini-btn">生成个性化计划</button>
"""

    return content


def get_phone_qa_content(chat_history: List[Dict] = None) -> str:
    """生成手机模式的问答页面"""
    content = """<div class="mini-card"><div class="mini-card-title">💬 常见问题</div><div class="mini-card-content"><div class="mini-list-item" style="padding: 10px; border-bottom: 1px solid #f0f0f0;"><span>要不要提前学小学内容？</span><span style="color: #4CAF50;">→</span></div><div class="mini-list-item" style="padding: 10px; border-bottom: 1px solid #f0f0f0;"><span>孩子注意力不集中怎么办？</span><span style="color: #4CAF50;">→</span></div><div class="mini-list-item" style="padding: 10px; border-bottom: 1px solid #f0f0f0;"><span>如何培养时间观念？</span><span style="color: #4CAF50;">→</span></div><div class="mini-list-item" style="padding: 10px;"><span>孩子不想去小学怎么办？</span><span style="color: #4CAF50;">→</span></div></div></div><div class="mini-card"><div class="mini-card-title">📝 我要提问</div><div class="mini-card-content" style="text-align: center; color: #999;">请在下方输入框提问</div></div>"""

    if chat_history:
        content += """<div class="mini-card"><div class="mini-card-title">📜 对话记录</div><div class="mini-card-content">"""
        for item in chat_history[-3:]:
            q_short = item['question'][:30] if len(item['question']) > 30 else item['question']
            a_short = item['answer'][:50] if len(item['answer']) > 50 else item['answer']
            content += f"""<div style="background: #f5f5f5; padding: 8px; border-radius: 8px; margin-bottom: 8px;"><div style="font-size: 12px; color: #666;">问：{q_short}</div><div style="font-size: 12px; color: #333; margin-top: 4px;">答：{a_short}</div></div>"""
        content += "</div></div>"

    return content
