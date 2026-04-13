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
