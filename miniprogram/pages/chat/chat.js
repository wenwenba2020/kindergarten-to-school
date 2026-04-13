const FAQS = ['需要提前学拼音吗？', '孩子注意力不集中怎么办？', '如何培养时间观念？', '孩子不想去小学怎么办？']

Page({
  data: { faqs: FAQS, messages: [], inputMsg: '', thinking: false, scrollToId: '', msgCounter: 0 },

  onInput(e) { this.setData({ inputMsg: e.detail }) },

  sendFaq(e) {
    this.setData({ inputMsg: e.currentTarget.dataset.msg })
    this.sendMessage()
  },

  async sendMessage() {
    const text = this.data.inputMsg.trim()
    if (!text) return
    const userMsg = { id: this.data.msgCounter, role: 'user', content: text }
    const newCounter = this.data.msgCounter + 1
    const history = this.data.messages.slice(-6).map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
    this.setData({ messages: [...this.data.messages, userMsg], inputMsg: '', thinking: true, msgCounter: newCounter, scrollToId: `msg-${userMsg.id}` })
    try {
      const res = await wx.cloud.callFunction({ name: 'chat', data: { message: text, history } })
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
