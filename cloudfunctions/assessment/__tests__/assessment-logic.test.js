const { calculateAssessment } = require('../assessment-logic')

const baseProfile = {
  language: { listening: 3, expression: 3, reading: 3, writing_interest: 3 },
  math: { counting: 3, operation: 3, shapes: 3, space: 3 },
  social: 3, self_care: 3, motor: 3,
  focus: 3, emotion: 3, time_awareness: 3,
}

test('全3分返回良好', () => {
  const result = calculateAssessment(baseProfile)
  expect(result.overall_level).toBe('良好')
  expect(result.strengths).toBeInstanceOf(Array)
  expect(result.areas_to_improve).toBeInstanceOf(Array)
  expect(result.recommendations).toBeInstanceOf(Array)
})

test('全5分返回优秀', () => {
  const highProfile = {
    language: { listening: 5, expression: 5, reading: 5, writing_interest: 5 },
    math: { counting: 5, operation: 5, shapes: 5, space: 5 },
    social: 5, self_care: 5, motor: 5,
    focus: 5, emotion: 5, time_awareness: 5,
  }
  const result = calculateAssessment(highProfile)
  expect(result.overall_level).toBe('优秀')
  expect(result.strengths.length).toBeGreaterThan(0)
  expect(result.areas_to_improve).toHaveLength(0)
})

test('全1分返回需加强关注并有建议', () => {
  const lowProfile = {
    language: { listening: 1, expression: 1, reading: 1, writing_interest: 1 },
    math: { counting: 1, operation: 1, shapes: 1, space: 1 },
    social: 1, self_care: 1, motor: 1,
    focus: 1, emotion: 1, time_awareness: 1,
  }
  const result = calculateAssessment(lowProfile)
  expect(result.overall_level).toBe('需加强关注')
  expect(result.areas_to_improve.length).toBeGreaterThan(0)
  expect(result.recommendations.length).toBeGreaterThan(0)
})

test('缺失字段使用默认值3，不崩溃', () => {
  expect(() => calculateAssessment({})).not.toThrow()
})

test('分数超出范围自动截断', () => {
  const profile = { ...baseProfile, social: 10 }
  const result = calculateAssessment(profile)
  expect(result.overall_level).toBeDefined()
})

test('语言得分>=4时有倾听优势', () => {
  const profile = { ...baseProfile, language: { listening: 4, expression: 4, reading: 4, writing_interest: 4 } }
  const result = calculateAssessment(profile)
  expect(result.strengths.some(s => s.includes('倾听'))).toBe(true)
})
