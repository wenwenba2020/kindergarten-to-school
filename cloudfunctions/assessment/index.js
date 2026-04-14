'use strict'
const cloud = require('wx-server-sdk')
const { calculateAssessment } = require('./assessment-logic')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

exports.main = async (event) => {
  const { scores, childScores } = event
  if (!scores) return { code: 400, message: '缺少 scores 参数' }
  try {
    const result = calculateAssessment(scores, childScores || null)
    return { code: 0, data: result }
  } catch (err) {
    return { code: 500, message: err.message }
  }
}
