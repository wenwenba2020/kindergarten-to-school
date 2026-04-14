// cloudfunctions/analyzeDeep/index.js
'use strict'
const cloud = require('wx-server-sdk')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const SILICONFLOW_API_KEY = process.env.SILICONFLOW_API_KEY
const SILICONFLOW_BASE_URL = 'https://api.siliconflow.cn/v1'
const MODEL = 'Pro/deepseek-ai/DeepSeek-V3'
const ANALYZE_QUOTA_LIMIT = 3  // max deep analyses per month per user
const MAX_ASSESSMENTS = 10     // cap on assessment history sent to LLM

// ── Input sanitization ───────────────────────────────────────────────────
function sanitizeInput(str, maxLen = 50) {
  if (typeof str !== 'string') return ''
  return str
    .replace(/[\n\r\t\0]/g, ' ')
    .replace(/[<>{}[\]`]/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim()
    .slice(0, maxLen)
}

// ── Quota ────────────────────────────────────────────────────────────────
async function consumeAnalyzeSlot(db, openid) {
  const month = new Date().toISOString().slice(0, 7)
  try {
    const updateRes = await db.collection('analyze_quota')
      .where({ openid, month, count: db.command.lt(ANALYZE_QUOTA_LIMIT) })
      .update({ data: { count: db.command.inc(1) } })

    if (updateRes.stats.updated > 0) {
      return { ok: true }
    }
    const existing = await db.collection('analyze_quota').where({ openid, month }).get()
    if (existing.data.length === 0) {
      await db.collection('analyze_quota').add({ data: { openid, month, count: 1 } })
      return { ok: true }
    }
    return { ok: false }
  } catch {
    try {
      await db.collection('analyze_quota').add({ data: { openid, month, count: 1 } })
      return { ok: true }
    } catch (e2) {
      console.error('analyzeDeep consumeSlot error')
      return { ok: true } // fail open
    }
  }
}

// ── Main handler ──────────────────────────────────────────────────────────
exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const { child, assessments } = event

  if (!Array.isArray(assessments) || assessments.length < 2) {
    return { code: 400, message: '需要至少2次评估记录才能进行深度分析' }
  }
  if (assessments.length > MAX_ASSESSMENTS) {
    return { code: 400, message: '评估记录过多，最多支持10次' }
  }

  // ── Quota ─────────────────────────────────────────────────────────────
  const db = cloud.database()
  const slot = await consumeAnalyzeSlot(db, OPENID)
  if (!slot.ok) {
    return { code: 429, message: `本月深度分析次数已用完（${ANALYZE_QUOTA_LIMIT}次/月）` }
  }

  // ── Sanitize user inputs ──────────────────────────────────────────────
  const childName = sanitizeInput(child?.name, 20)
  const childAge  = Number(child?.age) || 5.5
  const hometown  = sanitizeInput(child?.hometown, 30)

  const hometownTip = hometown
    ? `\n请结合${hometown}当地幼小衔接政策给出针对性升学建议。`
    : ''

  const systemPrompt = `你是幼小衔接深度分析专家。根据孩子多次评估数据，生成深度分析报告。只讨论儿童教育相关内容。
返回严格 JSON 格式：
{"growth_summary":"总体成长描述","dimension_trends":[{"dimension":"维度名","trend":"上升/稳定/下降","detail":"具体说明"}],"weak_spots_plan":[{"dimension":"弱项维度","daily_exercise":"每日练习内容"}],"estimated_weeks":8,"local_policy_tips":"当地政策建议"}${hometownTip}`

  // Build assessment summary — only numeric/known fields go in, no free text
  const assessmentSummary = assessments.slice(0, MAX_ASSESSMENTS).map((a, i) => {
    const s = a.scores || {}
    const lang = s.language || {}
    return `第${i + 1}次评估（${new Date(a.createdAt).toLocaleDateString('zh-CN')}）：
整体水平=${sanitizeInput(a.result?.overall_level, 10)}
语言均分=${((Number(lang.listening)||3)+(Number(lang.expression)||3)+(Number(lang.reading)||3)+(Number(lang.writing_interest)||3))/4}
数学均分=${((Number(s.math?.counting)||3)+(Number(s.math?.operation)||3)+(Number(s.math?.shapes)||3)+(Number(s.math?.space)||3))/4}
社交=${Number(s.social)||3} 自理=${Number(s.self_care)||3} 专注=${Number(s.focus)||3}`
  }).join('\n\n')

  const userPrompt = `孩子：${childName || '孩子'}，${childAge}岁\n\n${assessmentSummary}`

  try {
    if (!SILICONFLOW_API_KEY) throw new Error('API Key not configured')

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 60000)
    let resp
    try {
      resp = await fetch(`${SILICONFLOW_BASE_URL}/chat/completions`, {
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
        signal: controller.signal,
      })
    } finally {
      clearTimeout(timer)
    }

    if (!resp.ok) throw new Error(`upstream error: ${resp.status}`)
    const data = await resp.json()
    const content = data?.choices?.[0]?.message?.content
    if (!content) throw new Error('empty LLM response')

    const analysis = JSON.parse(content)
    return { code: 0, data: analysis }
  } catch (err) {
    console.error('analyzeDeep error:', err.message.slice(0, 100))
    return { code: 500, message: '深度分析暂时不可用，请稍后重试' }
  }
}
