Page({
  data: { hasAssessment: false, plan: null, activeTab: 0, currentWeek: 1, expandedWeek: null },

  onShow() {
    const hasAssessment = !!wx.getStorageSync('lastAssessmentResult')
    const plan = wx.getStorageSync('lastPlan') || null
    this.setData({ hasAssessment, plan: hasAssessment ? plan : null })
  },

  onTabChange(e) { this.setData({ activeTab: e.detail.index }) },

  toggleWeek(e) {
    const index = +e.currentTarget.dataset.index  // coerce to number
    this.setData({ expandedWeek: this.data.expandedWeek === index ? null : index })
  },

  goAssessment() { wx.switchTab({ url: '/pages/assessment/assessment' }) },

  showComingSoon() {
    wx.showToast({ title: '开发中，敬请期待', icon: 'none' })
  },
})
