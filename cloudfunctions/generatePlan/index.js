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

  const level = assessmentResult.overall_level || '良好'
  const strengths = (assessmentResult.strengths || [])
  const weaknesses = (assessmentResult.areas_to_improve || [])
  const hasChildData = assessmentResult.hasChildAssessment && (assessmentResult.childComparison || []).length > 0
  const comparisonNote = hasChildData
    ? `\n家长与孩子认知差异维度：${assessmentResult.childComparison.map(c => `${c.dimension}（家长${c.parentScore}分，孩子${c.childScore}分）`).join('；')}\n请在计划中针对这些差异维度加入亲子共练内容，帮助双方建立共识。`
    : ''

  const levelGuide = level === '优秀'
    ? '孩子整体发展良好，计划应以"拓展深度"为主：在优势维度增加进阶挑战，用有趣的项目制活动维持积极性；弱项仅需轻量巩固，避免过度训练消磨兴趣。'
    : level === '需加强关注'
    ? '孩子部分能力尚需加强，计划应以"补短板"为核心：针对每个弱项设计具体可操作的每日微练习（5-10分钟），从孩子能做到的最简单版本开始建立信心，同时保护已有优势。'
    : '孩子整体处于良好水平，计划应"补弱同时稳强"：弱项给出针对性的每日练习（重点安排在早晨或精力好的时段），优势维度通过亲子游戏方式维持；整体节奏不能过紧，保留充足玩耍时间。'

  const systemPrompt = `你是幼小衔接规划专家，为5-6岁大班儿童制定入学准备计划。

【核心要求】
1. 计划必须完全基于孩子的实际评估结果，不能生成对所有孩子都差不多的通用方案
2. ${levelGuide}
3. 每项 daily_activities 必须明确说明"这个活动针对哪个弱项/优势"，让家长知道为什么做
4. weekly_goals 按4周递进，第1周最简单，第4周有一定挑战
5. parent_tips 至少3条，专门针对该孩子弱项给出家庭执行的具体操作细节（不是泛泛而谈）
6. 回答语言温暖实用，避免教育机构式的生硬说教

返回严格 JSON，字段：
{"duration":"3个月","weekly_goals":["第1周目标","第2周目标","第3周目标","第4周目标"],"daily_activities":[{"time":"时段","activity":"具体活动","goal":"针对目标","duration_min":10}],"resources":["推荐资源"],"parent_tips":["针对性建议"],"evaluation_criteria":["验收标准"]}

知识库参考：
${KNOWLEDGE_BASE}${hometownTip}`

  const userPrompt = `请为以下孩子生成${duration}幼小衔接计划：

【孩子信息】
姓名：${childProfile.name || '孩子'}，年龄：${childProfile.age || 5.5}岁
整体水平：${level}

【优势维度】（已掌握较好，计划中以游戏化方式维持）
${strengths.length ? strengths.map(s => `· ${s}`).join('\n') : '暂无明显优势，需全面均衡提升'}

【需重点加强的维度】（计划的主要发力点，每项都要有对应的具体活动）
${weaknesses.length ? weaknesses.map(w => `· ${w}`).join('\n') : '整体均衡，无明显短板'}
${comparisonNote}
请严格按照"优势维度轻维护、弱项维度重练习"的原则制定计划，确保弱项每周有具体可执行的活动安排。`

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
    return { code: 0, data: getDefaultPlan(duration, assessmentResult?.areas_to_improve), fallback: true }
  }
}
