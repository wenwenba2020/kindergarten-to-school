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
    return `第${i + 1}次评估（${new Date(a.createdAt).toLocaleDateString('zh-CN')}）：
整体水平=${a.result.overall_level}
语言均分=${((s.language?.listening ?? 3) + (s.language?.expression ?? 3) + (s.language?.reading ?? 3) + (s.language?.writing_interest ?? 3)) / 4}
数学均分=${((s.math?.counting ?? 3) + (s.math?.operation ?? 3) + (s.math?.shapes ?? 3) + (s.math?.space ?? 3)) / 4}
社交=${s.social ?? 3} 自理=${s.self_care ?? 3} 专注=${s.focus ?? 3}`
  }).join('\n\n')

  const userPrompt = `孩子：${child?.name || '孩子'}，${child?.age || 5.5}岁\n\n${assessmentSummary}`

  try {
    if (!SILICONFLOW_API_KEY) throw new Error('未配置 API Key')

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

    if (!resp.ok) throw new Error(`API error: ${resp.status}`)
    const data = await resp.json()
    const content = data?.choices?.[0]?.message?.content
    if (!content) throw new Error(`Unexpected API response: ${JSON.stringify(data).slice(0, 200)}`)

    const analysis = JSON.parse(content)
    return { code: 0, data: analysis }
  } catch (err) {
    console.error('analyzeDeep error:', err.message)
    return { code: 500, message: '深度分析暂时不可用，请稍后重试' }
  }
}
