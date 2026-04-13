const DIMENSION_FAQS = {
  '语言能力': '怎么提升孩子的语言表达能力？',
  '数学认知': '有什么方法提高孩子的数学能力？',
  '社交能力': '孩子社交能力弱怎么帮助？',
  '自理能力': '如何培养孩子的自理习惯？',
  '专注力': '怎么训练孩子的专注力？',
  '阅读习惯': '如何帮孩子养成阅读习惯？',
  '运动协调': '有什么运动游戏提升孩子协调性？',
  '情绪管理': '孩子情绪不稳定怎么引导？',
}

function buildFaqs(areas_to_improve = []) {
  const faqs = areas_to_improve.slice(0, 4).map(dim => DIMENSION_FAQS[dim]).filter(Boolean)
  if (faqs.length === 0) return ['计划里的活动怎么执行？', '入学前还要注意什么？']
  return faqs
}

function buildChildContext() {
  const result = wx.getStorageSync('lastAssessmentResult')
  const plan = wx.getStorageSync('lastPlan')
  const child = getApp().globalData.currentChild
  if (!result) return null
  return {
    name: child?.name,
    age: child?.age,
    hometown: child?.hometown,
    overall_level: result.overall_level,
    strengths: result.strengths || [],
    areas_to_improve: result.areas_to_improve || [],
    weekly_goals: plan?.weekly_goals || [],
  }
}

Page({
  data: { hasAssessment: false, childContext: null, faqs: [], messages: [], inputMsg: '', thinking: false, scrollToId: '', msgCounter: 0 },

  onLoad() {
    this.refreshContext()
  },

  onShow() {
    this.refreshContext()
  },

  refreshContext() {
    const childContext = buildChildContext()
    const faqs = buildFaqs(childContext?.areas_to_improve)
    this.setData({ hasAssessment: !!childContext, childContext, faqs })
  },

  goAssessment() {
    wx.switchTab({ url: '/pages/assessment/assessment' })
  },

  onInput(e) { this.setData({ inputMsg: e.detail }) },

  sendFaq(e) {
    const msg = e.currentTarget.dataset.msg
    this.setData({ inputMsg: msg }, () => this.sendMessage())
  },

  async sendMessage() {
    const text = this.data.inputMsg.trim()
    if (!text) return
    const userMsg = { id: this.data.msgCounter, role: 'user', content: text }
    const newCounter = this.data.msgCounter + 1
    const history = this.data.messages.slice(-6).map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
    this.setData({ messages: [...this.data.messages, userMsg], inputMsg: '', thinking: true, msgCounter: newCounter, scrollToId: `msg-${userMsg.id}` })
    try {
      const res = await wx.cloud.callFunction({ name: 'chat', data: { message: text, history, childContext: this.data.childContext } })
      const reply = res.result.data?.reply || '暂时无法回答，请稍后再试。'
      const aiMsg = { id: newCounter, role: 'ai', content: reply }
      this.setData({ messages: [...this.data.messages, aiMsg], msgCounter: newCounter + 1, scrollToId: `msg-${aiMsg.id}` })
    } catch (err) {
      const aiMsg = { id: newCounter, role: 'ai', content: '网络异常，请检查连接后重试。' }
      this.setData({ messages: [...this.data.messages, aiMsg] })
    } finally {
      this.setData({ thinking: false })
    }
  },
})
