// cloudfunctions/chat/fallback-qa.js
'use strict'

const QA = [
  {
    keywords: ['提前学', '小学内容', '超前学习'],
    answer: '不建议系统学习小学内容，但可以通过游戏方式接触。重点是培养学习习惯和基础能力，避免超前学习导致入学后厌学。',
  },
  {
    keywords: ['不想去小学', '害怕小学', '入学焦虑'],
    answer: '可以带孩子参观小学熟悉环境，读《我上小学了》等绘本，认识邻居的哥哥姐姐，用正向引导取代恐吓。',
  },
  {
    keywords: ['注意力', '专注力', '坐不住'],
    answer: '从15分钟开始训练专注力，保持安静环境，通过拼图、积木、棋类游戏培养，每次只做一件事。',
  },
  {
    keywords: ['时间观念', '磨蹭', '拖拉'],
    answer: '使用可视化计时器（沙漏、番茄钟），制定固定作息表，提前提醒将要进行的活动，让孩子参与时间管理。',
  },
  {
    keywords: ['拼音', '学拼音'],
    answer: '不建议系统学习拼音，通过亲子阅读培养语感即可，避免超前学习导致入学后失去兴趣。',
  },
  {
    keywords: ['写字', '握笔', '姿势'],
    answer: '从握笔姿势开始，使用矫正器辅助，控制书写时间每次不超过15分钟，注意坐姿"三个一"（一尺一寸一拳头）。',
  },
  {
    keywords: ['社交', '内向', '不合群'],
    answer: '多安排与同龄人玩耍，通过角色扮演练习打招呼，及时鼓励社交行为，了解孩子不愿交往的原因。',
  },
  {
    keywords: ['自理', '独立', '依赖'],
    answer: '让孩子自己穿衣整理书包，把复杂任务分解成小步骤，耐心等待不代劳，及时鼓励独立行为。',
  },
]

const DEFAULT = '这个问题建议咨询专业教育人士或查看当地教育部门官方指南。'

function fallbackAnswer(message) {
  const msg = message.toLowerCase()
  for (const item of QA) {
    if (item.keywords.some(kw => msg.includes(kw))) {
      return item.answer
    }
  }
  return DEFAULT
}

module.exports = { fallbackAnswer }
