'use strict'

const LANG_KEYS = ['listening', 'expression', 'reading', 'writing_interest']
const MATH_KEYS = ['counting', 'operation', 'shapes', 'space']

function score(value) {
  const n = parseInt(value, 10)
  if (isNaN(n)) return 3
  return Math.max(1, Math.min(5, n))
}

// Flatten nested scores structure into {dimensionKey: avgScore} map
function flattenScores(s) {
  const lang = s.language || {}
  const math = s.math || {}
  const langAvg = LANG_KEYS.map(k => score(lang[k] ?? 3)).reduce((a, b) => a + b, 0) / LANG_KEYS.length
  const mathAvg = MATH_KEYS.map(k => score(math[k] ?? 3)).reduce((a, b) => a + b, 0) / MATH_KEYS.length
  return {
    语言能力: Math.round(langAvg * 10) / 10,
    数学认知: Math.round(mathAvg * 10) / 10,
    社交能力: score(s.social ?? 3),
    自理能力: score(s.self_care ?? 3),
    运动协调: score(s.motor ?? 3),
    专注力: score(s.focus ?? 3),
    情绪管理: score(s.emotion ?? 3),
    时间观念: score(s.time_awareness ?? 3),
  }
}

// Compare parent vs child scores; return items with notable gaps (>=1.5)
function generateComparison(parentScores, childScores) {
  const parent = flattenScores(parentScores)
  const child = flattenScores(childScores)
  const result = []
  for (const dim of Object.keys(parent)) {
    const p = parent[dim]
    const c = child[dim]
    const gap = Math.round((p - c) * 10) / 10
    if (Math.abs(gap) >= 1.5) {
      let note
      if (gap >= 1.5) {
        note = '家长认为表现良好，但孩子自测结果偏低，建议多观察孩子的实际体验和感受'
      } else {
        note = '孩子自测结果高于家长评估，孩子对此方面信心较强，可多给予鼓励和发挥空间'
      }
      result.push({ dimension: dim, parentScore: p, childScore: c, gap, note })
    }
  }
  return result
}

function addFeedback(s, strengths, areas, recs, strengthMsg, areaMsg, tip) {
  if (s >= 4) strengths.push(strengthMsg)
  else if (s <= 2) { areas.push(areaMsg); recs.push(tip) }
}

function calculateAssessment(profile = {}, childProfile = null) {
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

  addFeedback(score(language.listening        ?? 3), strengths, areas_to_improve, recommendations,
    '倾听能力较好，能听懂指令', '倾听理解能力', '多与孩子交流复杂指令，锻炼理解能力')
  addFeedback(score(language.expression       ?? 3), strengths, areas_to_improve, recommendations,
    '语言表达清晰流畅', '语言表达能力', '每天15分钟亲子对话，鼓励孩子复述故事')
  addFeedback(score(language.reading          ?? 3), strengths, areas_to_improve, recommendations,
    '阅读兴趣浓厚', '阅读习惯', '建立固定阅读时间，选择孩子感兴趣的绘本')
  addFeedback(score(language.writing_interest ?? 3), strengths, areas_to_improve, recommendations,
    '对书写有兴趣，能进行简单书写', '书写兴趣与握笔习惯', '用描红、描写名字等方式增强书写兴趣')

  addFeedback(score(math.counting ?? 3), strengths, areas_to_improve, recommendations,
    '计数能力较强', '计数能力', '通过实物点数练习，20以内手口一致点数')
  addFeedback(score(math.operation ?? 3), strengths, areas_to_improve, recommendations,
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

  const result = { overall_level, strengths, areas_to_improve, recommendations }

  if (childProfile) {
    result.hasChildAssessment = true
    result.childComparison = generateComparison(profile, childProfile)
  } else {
    result.hasChildAssessment = false
    result.childComparison = []
  }

  return result
}

module.exports = { calculateAssessment }
