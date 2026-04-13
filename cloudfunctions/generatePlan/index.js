'use strict'
const cloud = require('wx-server-sdk')
const { KNOWLEDGE_BASE } = require('./knowledge-base')
const { getDefaultPlan } = require('./fallback-plan')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const SILICONFLOW_BASE_URL = 'https://api.siliconflow.cn/v1'
const MODEL = 'Pro/deepseek-ai/DeepSeek-V3'

async function callLLM(apiKey, systemPrompt, userPrompt) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 60000)
  let resp
  try {
    resp = await fetch(`${SILICONFLOW_BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.7,
        response_format: { type: 'json_object' },
      }),
      signal: controller.signal,
    })
  } catch (err) {
    clearTimeout(timer)
    throw err
  }
  clearTimeout(timer)
  if (!resp.ok) throw new Error(`LLM API error: ${resp.status}`)
  const data = await resp.json()
  const content = data?.choices?.[0]?.message?.content
  if (!content) throw new Error(`Unexpected LLM response: ${JSON.stringify(data).slice(0, 200)}`)
  return content
}

exports.main = async (event) => {
  const { childProfile, assessmentResult, duration = '3个月' } = event
  if (!childProfile || !assessmentResult) {
    return { code: 400, message: '缺少 childProfile 或 assessmentResult' }
  }

  const apiKey = process.env.SILICONFLOW_API_KEY
  const hometownTip = childProfile.hometown
    ? `\n请结合${childProfile.hometown}当地幼小衔接政策和小学入学要求，给出针对性建议。`
    : ''

  const systemPrompt = `你是"小桥"——幼小衔接规划专家。请根据孩子信息生成个性化计划。
请严格返回 JSON 格式，结构如下：
{"duration":"3个月","weekly_goals":["目标1","目标2","目标3","目标4"],"daily_activities":[{"time":"早晨","activity":"活动内容","goal":"活动目标"}],"resources":["资源1"],"parent_tips":["建议1"],"evaluation_criteria":["标准1"]}

知识库参考：
${KNOWLEDGE_BASE}${hometownTip}`

  const userPrompt = `请为以下孩子生成${duration}的幼小衔接计划：
姓名：${childProfile.name || '孩子'}
年龄：${childProfile.age || 5.5}岁
整体水平：${assessmentResult.overall_level}
优势：${(assessmentResult.strengths || []).join('、') || '暂无'}
需加强：${(assessmentResult.areas_to_improve || []).join('、') || '暂无'}
兴趣爱好：${(childProfile.interests || []).join('、') || '暂无'}
家长担忧：${(childProfile.concerns || []).join('、') || '暂无'}`

  try {
    if (!apiKey) throw new Error('未配置 SILICONFLOW_API_KEY')
    const raw = await callLLM(apiKey, systemPrompt, userPrompt)
    const plan = typeof raw === 'string' ? JSON.parse(raw) : raw
    if (!plan.weekly_goals || !plan.daily_activities) {
      throw new Error('LLM response missing required fields')
    }
    return { code: 0, data: plan }
  } catch (err) {
    console.error('generatePlan error:', err.message)
    return { code: 0, data: getDefaultPlan(duration), fallback: true }
  }
}
