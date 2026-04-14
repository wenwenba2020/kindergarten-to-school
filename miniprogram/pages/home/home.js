Page({
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
