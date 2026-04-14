'use strict'
const cloud = require('wx-server-sdk')
const { calculateAssessment } = require('./assessment-logic')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const MONTHLY_LIMIT = 3

async function getAssessmentCount(db, openid) {
  const month = new Date().toISOString().slice(0, 7) // "2026-04"
  try {
    const res = await db.collection('assessment_quota').where({ openid, month }).get()
    return { count: res.data[0]?.count || 0, docId: res.data[0]?._id || null, month }
  } catch {
    return { count: 0, docId: null, month }
  }
}

async function incrementAssessmentCount(db, openid, docId, month) {
  try {
    if (docId) {
      await db.collection('assessment_quota').doc(docId).update({ data: { count: db.command.inc(1) } })
    } else {
      await db.collection('assessment_quota').add({ data: { openid, month, count: 1 } })
    }
  } catch (e) {
    console.error('incrementAssessmentCount error:', e.message)
  }
}

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const { scores, childScores, action } = event

  const db = cloud.database()

  // Query remaining reassessment count
  if (action === 'getQuota') {
    const { count } = await getAssessmentCount(db, OPENID)
    return { code: 0, data: { remain: Math.max(0, MONTHLY_LIMIT - count), limit: MONTHLY_LIMIT } }
  }

  if (!scores) return { code: 400, message: '缺少 scores 参数' }

  // Check monthly limit
  const { count, docId, month } = await getAssessmentCount(db, OPENID)
  if (count >= MONTHLY_LIMIT) {
    return {
      code: 429,
      message: `本月评估次数已用完（${MONTHLY_LIMIT}次/月），下月自动重置`,
      data: { remain: 0, limit: MONTHLY_LIMIT }
    }
  }

  try {
    const result = calculateAssessment(scores, childScores || null)
    await incrementAssessmentCount(db, OPENID, docId, month)
    const remain = MONTHLY_LIMIT - count - 1
    return { code: 0, data: { ...result, remain, limit: MONTHLY_LIMIT } }
  } catch (err) {
    return { code: 500, message: err.message }
  }
}
