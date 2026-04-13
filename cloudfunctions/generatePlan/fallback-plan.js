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
