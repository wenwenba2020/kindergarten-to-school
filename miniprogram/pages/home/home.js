Page({
  data: {
    assessRemain: null,
    chatRemain: null,
  },

  onShow() {
    this._loadQuotas()
  },

  async _loadQuotas() {
    try {
      const [assessRes, chatRes] = await Promise.all([
        wx.cloud.callFunction({ name: 'assessment', data: { action: 'getQuota' } }),
        wx.cloud.callFunction({ name: 'chat', data: { action: 'getQuota' } }),
      ])
      const assessRemain = assessRes.result?.data?.remain ?? null
      const chatRemain = chatRes.result?.data?.remain ?? null
      this.setData({ assessRemain, chatRemain })
    } catch {
      // 拉取失败时不显示 badge，不影响主流程
    }
  },

  goAssessment() { wx.switchTab({ url: '/pages/assessment/assessment' }) },
  goPlan() { wx.switchTab({ url: '/pages/plan/plan' }) },
  goChat() { wx.switchTab({ url: '/pages/chat/chat' }) },
  openWenwenlab() {
    wx.setClipboardData({
      data: 'https://wenwenlab.com',
      success: () => wx.showToast({ title: '网址已复制', icon: 'success' }),
    })
  },
})
