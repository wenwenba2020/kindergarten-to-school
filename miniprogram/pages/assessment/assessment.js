function formatAge(years, months) {
  const y = parseInt(years) || 0
  const m = parseInt(months) || 0
  if (m === 0) return `${y}岁`
  if (m === 6) return `${y}岁半`
  return `${y}岁${m}个月`
}

const DIMENSIONS = [
  {
    key: 'listening', name: '倾听理解', icon: '👂',
    scoreKeys: ['language.listening'],
    questions: [
      {
        text: '孩子能否理解并执行多步骤指令（如"先把书放好，再拿出画笔"）？',
        options: [
          { label: '能准确理解并完成多步骤指令', score: 5 },
          { label: '能理解单步指令，多步骤需重复说明', score: 3 },
          { label: '需反复解释才能理解简单指令', score: 1 },
        ]
      },
      {
        text: '孩子听完一个故事后，能否复述主要内容？',
        options: [
          { label: '能完整复述，说出角色和主要情节', score: 5 },
          { label: '能说出故事大意，细节有遗漏', score: 3 },
          { label: '只能说出故事里的一两个片段', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '老师说"先把书放好，再去排队"，你能做到吗？',
        options: [
          { label: '😊 每次都能做到', score: 5 },
          { label: '🤔 有时候做得到', score: 3 },
          { label: '😅 经常忘记步骤', score: 1 },
        ]
      },
      {
        text: '听完一个故事，你能说出里面发生了什么吗？',
        options: [
          { label: '😊 能说出很多内容', score: 5 },
          { label: '🤔 能说出一两件事', score: 3 },
          { label: '😅 记不太清楚', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'expression', name: '语言表达', icon: '🗣️',
    scoreKeys: ['language.expression'],
    questions: [
      {
        text: '孩子能否清楚地用一段话描述一件事（含时间、地点、经过）？',
        options: [
          { label: '能完整描述，表达条理清晰', score: 5 },
          { label: '能说出主要内容，但表达较零散', score: 3 },
          { label: '表达不清，需大人帮助补充', score: 1 },
        ]
      },
      {
        text: '孩子是否愿意在集体面前发言？',
        options: [
          { label: '积极举手发言，声音响亮自信', score: 5 },
          { label: '在熟悉的人面前能表达，不愿公开发言', score: 3 },
          { label: '很少主动开口，需大人引导', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你能把今天在幼儿园发生的事情讲给爸爸妈妈听吗？',
        options: [
          { label: '😊 能讲得很清楚', score: 5 },
          { label: '🤔 能讲一部分', score: 3 },
          { label: '😅 说不太清楚', score: 1 },
        ]
      },
      {
        text: '在小朋友面前，你喜欢讲话发言吗？',
        options: [
          { label: '😊 很喜欢，经常举手', score: 5 },
          { label: '🤔 有时候会', score: 3 },
          { label: '😅 不太喜欢，有点害羞', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'reading', name: '阅读习惯', icon: '📖',
    scoreKeys: ['language.reading'],
    questions: [
      {
        text: '孩子平时对阅读的兴趣如何？',
        options: [
          { label: '主动要求看书，每天阅读超过20分钟', score: 5 },
          { label: '喜欢听故事，但自主阅读时间较少', score: 3 },
          { label: '对书本兴趣不大，需督促才看', score: 1 },
        ]
      },
      {
        text: '孩子能否理解图书内容并发表看法？',
        options: [
          { label: '能预测故事情节，理解寓意，有自己的想法', score: 5 },
          { label: '能理解故事内容，但较少有自己的见解', score: 3 },
          { label: '注意力主要在图画，不太理解故事内容', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你喜欢看书或听故事吗？',
        options: [
          { label: '😊 非常喜欢，每天都要看', score: 5 },
          { label: '🤔 有时候喜欢', score: 3 },
          { label: '😅 不太喜欢', score: 1 },
        ]
      },
      {
        text: '看完一本书，你能说出书里的故事吗？',
        options: [
          { label: '😊 能说出很多内容', score: 5 },
          { label: '🤔 能说出一点点', score: 3 },
          { label: '😅 记不住', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'writing', name: '书写兴趣', icon: '✏️',
    scoreKeys: ['language.writing_interest'],
    questions: [
      {
        text: '孩子的握笔姿势和书写情况如何？',
        options: [
          { label: '握笔姿势正确，能认真描红，字形基本规范', score: 5 },
          { label: '握笔有些问题，能完成简单描红', score: 3 },
          { label: '不愿意写字，或握笔姿势很不规范', score: 1 },
        ]
      },
      {
        text: '孩子能认识多少汉字？',
        options: [
          { label: '认识自己名字及100个以上常见汉字', score: 5 },
          { label: '认识自己名字和部分汉字（20-50个）', score: 3 },
          { label: '基本不认识汉字', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你喜欢写字或画画吗？',
        options: [
          { label: '😊 很喜欢，经常自己写写画画', score: 5 },
          { label: '🤔 有时候喜欢', score: 3 },
          { label: '😅 不太喜欢', score: 1 },
        ]
      },
      {
        text: '你认识自己名字里的字吗？',
        options: [
          { label: '😊 认识，还认识很多其他字', score: 5 },
          { label: '🤔 认识自己的名字', score: 3 },
          { label: '😅 还不认识', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'math', name: '数学能力', icon: '🔢',
    scoreKeys: ['math.counting', 'math.operation', 'math.shapes', 'math.space'],
    questions: [
      {
        text: '孩子的数数和加减法掌握情况如何？',
        options: [
          { label: '能正确数20以内的数，掌握10以内加减法', score: 5 },
          { label: '能数到20，加减法需要借助手指', score: 3 },
          { label: '数到10有困难，加减法概念模糊', score: 1 },
        ]
      },
      {
        text: '孩子认识图形和空间方位的情况如何？',
        options: [
          { label: '认识常见几何图形，能准确区分上下左右前后', score: 5 },
          { label: '认识基本图形，方位概念有时混淆', score: 3 },
          { label: '图形和方位概念都比较模糊', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你能从1数到20吗？',
        options: [
          { label: '😊 能！还会做简单的加减法', score: 5 },
          { label: '🤔 能数到20，加减法要用手指', score: 3 },
          { label: '😅 数到10有点难', score: 1 },
        ]
      },
      {
        text: '你认识圆形、正方形和三角形吗？',
        options: [
          { label: '😊 都认识，还知道左边右边', score: 5 },
          { label: '🤔 认识这些形状', score: 3 },
          { label: '😅 有些搞不太清楚', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'social', name: '社交能力', icon: '🤝',
    scoreKeys: ['social'],
    questions: [
      {
        text: '孩子与同伴合作游戏的情况如何？',
        options: [
          { label: '主动合作，懂得轮流、分享和协商', score: 5 },
          { label: '能与熟悉的小朋友一起玩，偶有争抢', score: 3 },
          { label: '不喜欢与人合作，独自玩耍为主', score: 1 },
        ]
      },
      {
        text: '孩子遇到冲突或不如意时如何处理？',
        options: [
          { label: '用语言表达情绪，能尝试协商解决', score: 5 },
          { label: '会向大人求助', score: 3 },
          { label: '容易哭闹或动手', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你喜欢和小朋友一起玩吗？',
        options: [
          { label: '😊 很喜欢，经常和大家一起玩', score: 5 },
          { label: '🤔 和熟悉的小朋友一起玩', score: 3 },
          { label: '😅 更喜欢自己玩', score: 1 },
        ]
      },
      {
        text: '和小朋友闹矛盾了，你会怎么做？',
        options: [
          { label: '😊 好好说，一起想办法解决', score: 5 },
          { label: '🤔 找老师或爸爸妈妈帮忙', score: 3 },
          { label: '😅 哭或者不理他们', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'self_care', name: '自理能力', icon: '🧹',
    scoreKeys: ['self_care'],
    questions: [
      {
        text: '孩子日常自理的情况如何？',
        options: [
          { label: '能独立穿脱衣物（含系鞋带）、整理书包', score: 5 },
          { label: '能完成大部分自理，系鞋带等精细动作需帮助', score: 3 },
          { label: '大部分自理需要大人帮忙', score: 1 },
        ]
      },
      {
        text: '孩子整理物品的习惯如何？',
        options: [
          { label: '玩完会主动收拾，物品有固定摆放位置', score: 5 },
          { label: '需要提醒才会整理', score: 3 },
          { label: '不会主动整理，需大人代劳', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你能自己穿衣服、系鞋带吗？',
        options: [
          { label: '😊 都能自己做', score: 5 },
          { label: '🤔 穿衣服可以，系鞋带需要帮忙', score: 3 },
          { label: '😅 需要爸爸妈妈帮忙', score: 1 },
        ]
      },
      {
        text: '玩完玩具，你会自己收拾吗？',
        options: [
          { label: '😊 会！我知道玩具放哪里', score: 5 },
          { label: '🤔 爸爸妈妈叫我才收拾', score: 3 },
          { label: '😅 不太会收拾', score: 1 },
        ]
      }
    ]
  },
  {
    key: 'focus', name: '专注力', icon: '🎯',
    scoreKeys: ['focus', 'motor', 'emotion', 'time_awareness'],
    questions: [
      {
        text: '孩子能持续专注多长时间？',
        options: [
          { label: '能专注完成一件事超过15-20分钟', score: 5 },
          { label: '能专注10-15分钟，容易被外界分心', score: 3 },
          { label: '很难持续专注超过5分钟', score: 1 },
        ]
      },
      {
        text: '孩子能否按时独立完成分配的任务？',
        options: [
          { label: '能在规定时间内独立完成（如拼图、画画）', score: 5 },
          { label: '需要提醒和鼓励才能坚持完成', score: 3 },
          { label: '经常放弃，难以完成需要一定时间的任务', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '做拼图或画画的时候，你能坚持多久？',
        options: [
          { label: '😊 能一直做到完成', score: 5 },
          { label: '🤔 做一会儿，容易被其他东西吸引', score: 3 },
          { label: '😅 做一点就不想做了', score: 1 },
        ]
      },
      {
        text: '老师让你完成一件事，你能做完吗？',
        options: [
          { label: '😊 每次都能做完', score: 5 },
          { label: '🤔 有时候能做完', score: 3 },
          { label: '😅 经常做不完', score: 1 },
        ]
      }
    ]
  },
]

function buildDimensions(childMode) {
  return DIMENSIONS.map((d, i) => ({
    ...d,
    done: false,
    rating: 0,
    locked: i > 0,
    questions: childMode ? d.childQuestions : d.questions,
  }))
}

Page({
  data: {
    dimensions: buildDimensions(false),
    doneCount: 0,
    childMode: false,
    showPopup: false,
    currentDim: null,
    currentDimData: null,
    currentQuestions: [],
    currentAnswers: [],
    submitting: false,
    childName: '',
    childAgeDisplay: '',
    showChildSetup: false,
    form: { name: '', ageYears: '', ageMonths: '', hometown: '' },
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
      const years = child.ageYears !== undefined ? child.ageYears : Math.floor(child.age || 5)
      const months = child.ageMonths !== undefined ? child.ageMonths : Math.round(((child.age || 5) - Math.floor(child.age || 5)) * 12)
      this.setData({ childName: child.name, childAgeDisplay: formatAge(years, months) })
    }
  },

  onFormChange(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ [`form.${key}`]: e.detail })
  },

  async saveChildInfo() {
    const { name, ageYears, ageMonths, hometown } = this.data.form
    if (!name) return wx.showToast({ title: '请输入孩子姓名', icon: 'none' })
    if (!ageYears) return wx.showToast({ title: '请输入孩子年龄', icon: 'none' })
    try {
      const years = parseInt(ageYears) || 5
      const months = parseInt(ageMonths) || 0
      const age = years + months / 12
      const child = { name, age, ageYears: years, ageMonths: months, hometown }
      const db = wx.cloud.database()
      const res = await db.collection('children').add({ data: { ...child, createdAt: db.serverDate() } })
      child._id = res._id
      getApp().globalData.currentChild = child
      this.setData({ showChildSetup: false, childName: name, childAgeDisplay: formatAge(years, months) })
    } catch (err) {
      wx.showToast({ title: '保存失败，请重试', icon: 'none' })
      console.error('saveChildInfo error:', err)
    }
  },

  editChildInfo() {
    const child = getApp().globalData.currentChild || {}
    const years = child.ageYears !== undefined ? child.ageYears : Math.floor(child.age || 5)
    const months = child.ageMonths !== undefined ? child.ageMonths : Math.round(((child.age || 5) - Math.floor(child.age || 5)) * 12)
    this.setData({
      showChildSetup: true,
      form: { name: child.name || '', ageYears: String(years || ''), ageMonths: months > 0 ? String(months) : '', hometown: child.hometown || '' },
    })
  },

  toggleChildMode(e) {
    const childMode = e.detail.value
    // Rebuild dimensions with new question set, preserve done/rating/locked state
    const current = this.data.dimensions
    const newDimensions = DIMENSIONS.map((d, i) => ({
      ...d,
      done: current[i].done,
      rating: current[i].rating,
      locked: current[i].locked,
      questions: childMode ? d.childQuestions : d.questions,
    }))
    this.setData({ childMode, dimensions: newDimensions })
  },

  openPopup(e) {
    const index = +e.currentTarget.dataset.index
    const dim = this.data.dimensions[index]
    if (dim.locked) {
      wx.showToast({ title: '请先完成前面的评估', icon: 'none' })
      return
    }
    const questions = dim.questions
    this.setData({
      showPopup: true,
      currentDim: index,
      currentDimData: dim,
      currentQuestions: questions,
      currentAnswers: new Array(questions.length).fill(null),
    })
  },

  closePopup() { this.setData({ showPopup: false }) },

  selectOption(e) {
    const { qindex, score } = e.currentTarget.dataset
    const newAnswers = [...this.data.currentAnswers]
    newAnswers[+qindex] = score
    this.setData({ currentAnswers: newAnswers })
  },

  confirmRating() {
    const { currentDim, currentAnswers, dimensions, scores, currentQuestions } = this.data
    const answered = currentAnswers.filter(a => a !== null && a !== undefined)
    if (answered.length < currentQuestions.length) {
      return wx.showToast({ title: '请完成所有问题', icon: 'none' })
    }
    const rating = Math.round(answered.reduce((a, b) => a + b, 0) / answered.length)
    const dim = dimensions[currentDim]
    const newScores = JSON.parse(JSON.stringify(scores))
    if (dim.key === 'listening') newScores.language.listening = rating
    else if (dim.key === 'expression') newScores.language.expression = rating
    else if (dim.key === 'reading') newScores.language.reading = rating
    else if (dim.key === 'writing') newScores.language.writing_interest = rating
    else if (dim.key === 'math') { newScores.math.counting = rating; newScores.math.operation = rating; newScores.math.shapes = rating; newScores.math.space = rating }
    else if (dim.key === 'social') newScores.social = rating
    else if (dim.key === 'self_care') newScores.self_care = rating
    else if (dim.key === 'focus') { newScores.focus = rating; newScores.motor = rating; newScores.emotion = rating; newScores.time_awareness = rating }

    // Update done state and unlock next card
    const newDimensions = dimensions.map((d, i) => {
      if (i === currentDim) return { ...d, done: true, rating }
      if (i === currentDim + 1) return { ...d, locked: false }
      return d
    })
    const doneCount = newDimensions.filter(d => d.done).length
    this.setData({ dimensions: newDimensions, doneCount, showPopup: false, scores: newScores, currentAnswers: [] })

    // Auto-open next card after short delay
    const nextIndex = currentDim + 1
    if (nextIndex < newDimensions.length) {
      setTimeout(() => {
        const nextDim = newDimensions[nextIndex]
        const nextQuestions = nextDim.questions
        this.setData({
          showPopup: true,
          currentDim: nextIndex,
          currentDimData: nextDim,
          currentQuestions: nextQuestions,
          currentAnswers: new Array(nextQuestions.length).fill(null),
        })
      }, 400)
    }
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
