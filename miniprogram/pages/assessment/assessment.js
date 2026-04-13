const DIMENSIONS = [
  { key: 'listening', name: '倾听理解', icon: '👂', desc: '孩子能否听懂老师的指令和故事内容，理解日常对话？', scoreKeys: ['language.listening'] },
  { key: 'expression', name: '语言表达', icon: '🗣️', desc: '孩子能否清楚地说出自己的想法，讲述一件事情？', scoreKeys: ['language.expression'] },
  { key: 'reading', name: '阅读习惯', icon: '📖', desc: '孩子是否喜欢阅读绘本，能否理解图书内容？', scoreKeys: ['language.reading'] },
  { key: 'writing', name: '书写兴趣', icon: '✏️', desc: '孩子是否对写字感兴趣，握笔姿势是否正确？', scoreKeys: ['language.writing_interest'] },
  { key: 'math', name: '数学能力', icon: '🔢', desc: '孩子能否数20以内的数，理解简单加减法，认识基本图形？', scoreKeys: ['math.counting', 'math.operation', 'math.shapes', 'math.space'] },
  { key: 'social', name: '社交能力', icon: '🤝', desc: '孩子能否与同龄人合作游戏，学会轮流和分享？', scoreKeys: ['social'] },
  { key: 'self_care', name: '自理能力', icon: '🧹', desc: '孩子能否独立穿衣、整理书包、自己如厕？', scoreKeys: ['self_care'] },
  { key: 'focus', name: '专注力', icon: '🎯', desc: '孩子能否持续专注15分钟以上完成一项任务？', scoreKeys: ['focus', 'motor', 'emotion', 'time_awareness'] },
]

Page({
  data: {
    dimensions: DIMENSIONS.map(d => ({ ...d, done: false, rating: 0 })),
    doneCount: 0,
    showPopup: false,
    currentDim: null,
    currentDimData: null,
    currentRating: 3,
    submitting: false,
    childName: '',
    childAge: '',
    showChildSetup: false,
    form: { name: '', age: '', hometown: '' },
    scores: {
      language: { listening: 3, expression: 3, reading: 3, writing_interest: 3 },
      math: { counting: 3, operation: 3, shapes: 3, space: 3 },
      social: 3, self_care: 3, motor: 3, focus: 3, emotion: 3, time_awareness: 3,
    },
  },

  onLoad() {
    const app = getApp()
    if (!app.globalData.currentChild) {
      this.setData({ showChildSetup: true })
    } else {
      const child = app.globalData.currentChild
      this.setData({ childName: child.name, childAge: child.age })
    }
  },

  onFormChange(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ [`form.${key}`]: e.detail })
  },

  async saveChildInfo() {
    const { name, age, hometown } = this.data.form
    if (!name) return wx.showToast({ title: '请输入孩子姓名', icon: 'none' })
    try {
      const child = { name, age: parseFloat(age) || 5.5, hometown }
      const db = wx.cloud.database()
      const res = await db.collection('children').add({ data: { ...child, createdAt: db.serverDate() } })
      child._id = res._id
      getApp().globalData.currentChild = child
      this.setData({ showChildSetup: false, childName: name, childAge: child.age })
    } catch (err) {
      wx.showToast({ title: '保存失败，请重试', icon: 'none' })
      console.error('saveChildInfo error:', err)
    }
  },

  openPopup(e) {
    const index = e.currentTarget.dataset.index
    const dim = this.data.dimensions[index]
    this.setData({ showPopup: true, currentDim: index, currentDimData: dim, currentRating: dim.rating || 3 })
  },

  closePopup() { this.setData({ showPopup: false }) },

  onRateChange(e) { this.setData({ currentRating: e.detail }) },

  confirmRating() {
    const { currentDim, currentRating, dimensions, scores } = this.data
    const dim = dimensions[currentDim]
    const rating = currentRating || 1
    const newScores = JSON.parse(JSON.stringify(scores))
    if (dim.key === 'listening') newScores.language.listening = rating
    else if (dim.key === 'expression') newScores.language.expression = rating
    else if (dim.key === 'reading') newScores.language.reading = rating
    else if (dim.key === 'writing') newScores.language.writing_interest = rating
    else if (dim.key === 'math') { newScores.math.counting = rating; newScores.math.operation = rating; newScores.math.shapes = rating; newScores.math.space = rating }
    else if (dim.key === 'social') newScores.social = rating
    else if (dim.key === 'self_care') newScores.self_care = rating
    else if (dim.key === 'focus') { newScores.focus = rating; newScores.motor = rating; newScores.emotion = rating; newScores.time_awareness = rating }
    const newDimensions = dimensions.map((d, i) => i === currentDim ? { ...d, done: true, rating } : d)
    const doneCount = newDimensions.filter(d => d.done).length
    this.setData({ dimensions: newDimensions, doneCount, showPopup: false, scores: newScores })
  },

  async submitAssessment() {
    this.setData({ submitting: true })
    wx.showLoading({ title: '正在评估...' })
    try {
      const res = await wx.cloud.callFunction({ name: 'assessment', data: { scores: this.data.scores } })
      if (res.result.code !== 0) throw new Error(res.result.message)
      const result = res.result.data
      const app = getApp()
      const child = app.globalData.currentChild
      const db = wx.cloud.database()
      const record = await db.collection('assessments').add({
        data: { childId: child?._id || '', scores: this.data.scores, result, createdAt: db.serverDate() },
      })
      wx.setStorageSync('lastAssessmentResult', result)
      wx.setStorageSync('lastAssessmentScores', this.data.scores)
      wx.navigateTo({ url: `/pages/result/result?assessmentId=${record._id}` })
    } catch (err) {
      wx.showToast({ title: '评估失败，请重试', icon: 'none' })
      console.error(err)
    } finally {
      wx.hideLoading()
      this.setData({ submitting: false })
    }
  },
})
