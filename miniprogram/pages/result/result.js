const LEVEL_EMOJI = { '优秀': '🌟', '良好': '👍', '需加强关注': '💪' }

Page({
  data: { result: null, levelEmoji: '', loading: false },

  onLoad() {
    const result = wx.getStorageSync('lastAssessmentResult')
    if (result) {
      this.setData({ result, levelEmoji: LEVEL_EMOJI[result.overall_level] || '📊' })
    }
  },

  async generatePlan() {
    this.setData({ loading: true })
    wx.showLoading({ title: '正在生成计划...' })
    try {
      const app = getApp()
      const child = app.globalData.currentChild
      const result = this.data.result
      const res = await wx.cloud.callFunction({
        name: 'generatePlan',
        data: { childProfile: { ...child, interests: [], concerns: [] }, assessmentResult: result, duration: '3个月' },
      })
      if (res.result.code !== 0) throw new Error(res.result.message)
      const plan = res.result.data
      const db = wx.cloud.database()
      await db.collection('plans').add({ data: { childId: child?._id || '', ...plan, currentWeek: 1, createdAt: db.serverDate() } })
      wx.setStorageSync('lastPlan', plan)
      wx.switchTab({ url: '/pages/plan/plan' })
    } catch (err) {
      wx.showToast({ title: '生成失败，请重试', icon: 'none' })
      console.error(err)
    } finally {
      wx.hideLoading()
      this.setData({ loading: false })
    }
  },

  goBack() { wx.navigateBack() },
})
