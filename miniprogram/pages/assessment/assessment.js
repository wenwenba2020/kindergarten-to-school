function formatAge(years, months) {
  const y = parseInt(years) || 0
  const m = parseInt(months) || 0
  if (m === 0) return `${y}岁`
  if (m === 6) return `${y}岁半`
  return `${y}岁${m}个月`
}

const INITIAL_SCORES = {
  language: { listening: 3, expression: 3, reading: 3, writing_interest: 3 },
  math: { counting: 3, operation: 3, shapes: 3, space: 3 },
  social: 3, self_care: 3, motor: 3, focus: 3, emotion: 3, time_awareness: 3,
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

// Alternative question sets (version 1) — used on reassessment
const ALT_QUESTIONS = {
  listening: {
    questions: [
      {
        text: '孩子在嘈杂环境中（如超市、公共场合）能否听清并理解大人的话？',
        options: [
          { label: '能在嘈杂环境中专注听并准确理解', score: 5 },
          { label: '安静环境能听清，嘈杂时需重复', score: 3 },
          { label: '需要大人凑近、反复说才能理解', score: 1 },
        ]
      },
      {
        text: '孩子能否按顺序完成"先…再…最后…"这类多步骤指令？',
        options: [
          { label: '能记住并按顺序完成全部步骤', score: 5 },
          { label: '能完成两步，第三步容易忘', score: 3 },
          { label: '只能跟着做一步，需逐步引导', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '超市里很吵，妈妈叫你名字你能听到吗？',
        options: [
          { label: '😊 能！马上就听到了', score: 5 },
          { label: '🤔 有时候能听到', score: 3 },
          { label: '😅 经常听不到', score: 1 },
        ]
      },
      {
        text: '老师说"先洗手，再吃饭，最后放碗"，你能全部记住吗？',
        options: [
          { label: '😊 记得住，都能做到', score: 5 },
          { label: '🤔 能记住两步', score: 3 },
          { label: '😅 只记住第一步', score: 1 },
        ]
      }
    ]
  },
  expression: {
    questions: [
      {
        text: '孩子与陌生大人交流时的表现如何？',
        options: [
          { label: '主动问好，能清楚回答问题，不怯场', score: 5 },
          { label: '需引导才开口，但能正常交流', score: 3 },
          { label: '不愿开口，躲在大人后面', score: 1 },
        ]
      },
      {
        text: '孩子能否用语言描述一幅图画或一件物品的特征？',
        options: [
          { label: '能使用颜色、形状、大小等多种词汇描述', score: 5 },
          { label: '能说出主要特征，描述较简单', score: 3 },
          { label: '只能说出一两个词', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '遇到不认识的叔叔阿姨问你名字，你会怎么做？',
        options: [
          { label: '😊 大声说出自己的名字', score: 5 },
          { label: '🤔 小声说，有点害羞', score: 3 },
          { label: '😅 不想说，藏起来', score: 1 },
        ]
      },
      {
        text: '你能说出一只小猫有哪些特点吗？',
        options: [
          { label: '😊 能说好多（毛软软的、眼睛圆圆的…）', score: 5 },
          { label: '🤔 能说一两个', score: 3 },
          { label: '😅 不知道怎么说', score: 1 },
        ]
      }
    ]
  },
  reading: {
    questions: [
      {
        text: '孩子是否有自己喜欢的书，会主动翻看、反复阅读？',
        options: [
          { label: '有固定喜爱的书，会主动拿出来反复看', score: 5 },
          { label: '有时会翻书，但无固定兴趣方向', score: 3 },
          { label: '对书无明显兴趣，更喜欢视频或玩具', score: 1 },
        ]
      },
      {
        text: '孩子对文字的兴趣如何？（如路牌、商标上的字）',
        options: [
          { label: '会主动询问字的含义，尝试认读', score: 5 },
          { label: '偶尔关注，被问到才说', score: 3 },
          { label: '对文字没有明显好奇心', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你有没有特别喜欢的一本书，愿意反复看？',
        options: [
          { label: '😊 有！我能讲出里面的故事', score: 5 },
          { label: '🤔 有几本，但不太记得内容', score: 3 },
          { label: '😅 没有特别喜欢的书', score: 1 },
        ]
      },
      {
        text: '走路看到路牌或商店名字，你会想知道那是什么字吗？',
        options: [
          { label: '😊 会！我经常问爸爸妈妈', score: 5 },
          { label: '🤔 有时候会问', score: 3 },
          { label: '😅 不太在意', score: 1 },
        ]
      }
    ]
  },
  writing: {
    questions: [
      {
        text: '孩子是否会用图画或符号表达自己的想法（如画日记）？',
        options: [
          { label: '会主动用画画或图文结合记录事情', score: 5 },
          { label: '喜欢画画，但不会结合文字', score: 3 },
          { label: '不喜欢画画或书写类活动', score: 1 },
        ]
      },
      {
        text: '孩子能否写出自己的名字？',
        options: [
          { label: '能工整地写出全名，笔划基本正确', score: 5 },
          { label: '能写，但笔划顺序或形状有误', score: 3 },
          { label: '不会写，或只能描红', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '你有没有用画画记录过今天发生的事情？',
        options: [
          { label: '😊 有！我喜欢画"日记"', score: 5 },
          { label: '🤔 偶尔画一画', score: 3 },
          { label: '😅 没有', score: 1 },
        ]
      },
      {
        text: '你能自己写出自己的名字吗？',
        options: [
          { label: '😊 能！写得很好看', score: 5 },
          { label: '🤔 能写，但有时候写错', score: 3 },
          { label: '😅 还不会写', score: 1 },
        ]
      }
    ]
  },
  math: {
    questions: [
      {
        text: '孩子在生活中能否自发用数学解决问题（如分糖果、数台阶）？',
        options: [
          { label: '会主动用数数、比较解决实际问题', score: 5 },
          { label: '在引导下能用数学方法，不会主动', score: 3 },
          { label: '对生活中的数学场景不感兴趣', score: 1 },
        ]
      },
      {
        text: '孩子能否按大小、长短对5个以上物品排序？',
        options: [
          { label: '能准确排序5个以上，还能说出"最大""第三"', score: 5 },
          { label: '能排3-4个，较多时出现混乱', score: 3 },
          { label: '排序概念较模糊', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '如果把5颗糖分给2个人，你知道怎么分吗？',
        options: [
          { label: '😊 知道！一人2颗，还剩1颗', score: 5 },
          { label: '🤔 大概知道，要数一数', score: 3 },
          { label: '😅 不知道怎么分', score: 1 },
        ]
      },
      {
        text: '把5根小棒从短到长排好，你能做到吗？',
        options: [
          { label: '😊 能！还能说出哪根最短', score: 5 },
          { label: '🤔 能排，有时候会搞错', score: 3 },
          { label: '😅 不太会排', score: 1 },
        ]
      }
    ]
  },
  social: {
    questions: [
      {
        text: '孩子在陌生小朋友中的表现如何？',
        options: [
          { label: '主动打招呼，很快融入新群体', score: 5 },
          { label: '需要时间热身，但能逐步融入', score: 3 },
          { label: '长时间保持距离，不愿主动接触', score: 1 },
        ]
      },
      {
        text: '孩子能否使用"请、谢谢、对不起"等礼貌用语？',
        options: [
          { label: '自然地在合适场景使用礼貌用语', score: 5 },
          { label: '需提醒才会用', score: 3 },
          { label: '很少主动使用礼貌用语', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '去新的地方遇到不认识的小朋友，你会主动和他们玩吗？',
        options: [
          { label: '😊 会！我会去打招呼', score: 5 },
          { label: '🤔 要先观察一下才敢去', score: 3 },
          { label: '😅 不敢，我会等他们来找我', score: 1 },
        ]
      },
      {
        text: '不小心碰到别人，你会说什么？',
        options: [
          { label: '😊 马上说"对不起"', score: 5 },
          { label: '🤔 有时候说，有时候忘', score: 3 },
          { label: '😅 不知道要说什么', score: 1 },
        ]
      }
    ]
  },
  self_care: {
    questions: [
      {
        text: '孩子能否独立处理如厕及个人卫生（饭前洗手、擦嘴等）？',
        options: [
          { label: '完全独立，养成良好卫生习惯', score: 5 },
          { label: '能基本自理，部分环节需提醒', score: 3 },
          { label: '如厕或洗手等需要大人全程协助', score: 1 },
        ]
      },
      {
        text: '孩子在幼儿园的自我管理情况如何（老师反馈）？',
        options: [
          { label: '老师反馈自理能力强，不需要特别照顾', score: 5 },
          { label: '偶尔需要老师提醒', score: 3 },
          { label: '经常需要老师额外协助', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '上厕所和洗手，你能自己做好吗？',
        options: [
          { label: '😊 能！每次都自己做', score: 5 },
          { label: '🤔 基本可以，有时候要提醒', score: 3 },
          { label: '😅 需要爸爸妈妈帮忙', score: 1 },
        ]
      },
      {
        text: '在幼儿园，老师需要经常帮助你吗？',
        options: [
          { label: '😊 不需要，我自己能搞定', score: 5 },
          { label: '🤔 偶尔需要老师提醒', score: 3 },
          { label: '😅 老师经常要帮我', score: 1 },
        ]
      }
    ]
  },
  focus: {
    questions: [
      {
        text: '孩子在没有大人监督时能否独立完成一项活动（如拼图、画画）？',
        options: [
          { label: '能自主完成，中间不需要大人介入', score: 5 },
          { label: '需要偶尔鼓励，大人陪着能完成', score: 3 },
          { label: '离开大人监督很快放弃', score: 1 },
        ]
      },
      {
        text: '孩子对时间的感知如何（如知道"再过5分钟就要走了"）？',
        options: [
          { label: '能理解时间提示，按约定收拾停止', score: 5 },
          { label: '能理解，但执行时经常拖延', score: 3 },
          { label: '对时间没概念，需要强制转换', score: 1 },
        ]
      }
    ],
    childQuestions: [
      {
        text: '爸爸妈妈不在旁边，你能自己把拼图拼完吗？',
        options: [
          { label: '😊 能！我自己能拼完', score: 5 },
          { label: '🤔 要爸爸妈妈偶尔鼓励我', score: 3 },
          { label: '😅 没人陪就不想拼了', score: 1 },
        ]
      },
      {
        text: '妈妈说"再玩5分钟就要走了"，你能在5分钟后自己停下来吗？',
        options: [
          { label: '😊 能！我知道时间到了要走', score: 5 },
          { label: '🤔 有时候能，有时候还想再玩', score: 3 },
          { label: '😅 不想停，要妈妈拉着走', score: 1 },
        ]
      }
    ]
  },
}

function buildDimensions(phase, version) {
  return DIMENSIONS.map((d, i) => {
    const useAlt = version && version % 2 === 1 && ALT_QUESTIONS[d.key]
    const altSet = useAlt ? ALT_QUESTIONS[d.key] : null
    const qs = phase === 'child'
      ? (altSet ? altSet.childQuestions : d.childQuestions)
      : (altSet ? altSet.questions : d.questions)
    return { ...d, done: false, rating: 0, locked: i > 0, questions: qs }
  })
}

Page({
  data: {
    dimensions: buildDimensions('parent', 0),
    doneCount: 0,
    phase: 'parent',       // 'parent' | 'child'
    parentScores: null,    // stored after parent phase
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
    scores: JSON.parse(JSON.stringify(INITIAL_SCORES)),
    assessRemain: null,   // remaining assessments this month
    assessLimit: 3,
  },

  onLoad() {
    const version = wx.getStorageSync('assessmentVersion') || 0
    const app = getApp()
    if (!app.globalData.currentChild) {
      this.setData({ showChildSetup: true, dimensions: buildDimensions('parent', version) })
    } else {
      const child = app.globalData.currentChild
      const years = child.ageYears !== undefined ? child.ageYears : Math.floor(child.age || 5)
      const months = child.ageMonths !== undefined ? child.ageMonths : Math.round(((child.age || 5) - Math.floor(child.age || 5)) * 12)
      this.setData({ childName: child.name, childAgeDisplay: formatAge(years, months), dimensions: buildDimensions('parent', version) })
    }
    this._loadAssessQuota()
  },

  async _loadAssessQuota() {
    try {
      const res = await wx.cloud.callFunction({ name: 'assessment', data: { action: 'getQuota' } })
      const { remain, limit } = res.result?.data || {}
      if (remain !== undefined) this.setData({ assessRemain: remain, assessLimit: limit || 3 })
    } catch { /* ignore */ }
  },

  onShow() {
    if (wx.getStorageSync('assessmentNeedReset')) {
      wx.removeStorageSync('assessmentNeedReset')
      // Increment version so next assessment uses alternate questions
      const prevVersion = wx.getStorageSync('assessmentVersion') || 0
      const nextVersion = prevVersion + 1
      wx.setStorageSync('assessmentVersion', nextVersion)
      this.setData({
        dimensions: buildDimensions('parent', nextVersion),
        doneCount: 0,
        phase: 'parent',
        parentScores: null,
        showPopup: false,
        currentAnswers: [],
        scores: JSON.parse(JSON.stringify(INITIAL_SCORES)),
      })
      this._loadAssessQuota()
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

    const newDimensions = dimensions.map((d, i) => {
      if (i === currentDim) return { ...d, done: true, rating }
      if (i === currentDim + 1) return { ...d, locked: false }
      return d
    })
    const doneCount = newDimensions.filter(d => d.done).length
    this.setData({ dimensions: newDimensions, doneCount, showPopup: false, scores: newScores, currentAnswers: [] })

    // Auto-open next card
    const nextIndex = currentDim + 1
    if (nextIndex < newDimensions.length) {
      setTimeout(() => {
        const nextDim = newDimensions[nextIndex]
        this.setData({
          showPopup: true,
          currentDim: nextIndex,
          currentDimData: nextDim,
          currentQuestions: nextDim.questions,
          currentAnswers: new Array(nextDim.questions.length).fill(null),
        })
      }, 400)
    }
  },

  submitAssessment() {
    if (this.data.phase === 'parent') {
      wx.showModal({
        title: '家长评估已完成 🎉',
        content: '是否邀请孩子参与自测？双方评估可生成家长与孩子的对比分析，发现认知差异。',
        confirmText: '孩子自测',
        cancelText: '看结果',
        success: (res) => {
          if (res.confirm) {
            this._startChildPhase()
          } else {
            this._doSubmit(this.data.scores, null)
          }
        }
      })
      return
    }
    this._doSubmit(this.data.parentScores, this.data.scores)
  },

  _startChildPhase() {
    const parentScores = JSON.parse(JSON.stringify(this.data.scores))
    this.setData({
      parentScores,
      phase: 'child',
      dimensions: buildDimensions('child', wx.getStorageSync('assessmentVersion') || 0),
      doneCount: 0,
      scores: JSON.parse(JSON.stringify(INITIAL_SCORES)),
      showPopup: false,
      currentAnswers: [],
    })
    wx.showToast({ title: '现在开始孩子自测', icon: 'success' })
  },

  async _doSubmit(parentScores, childScores) {
    this.setData({ submitting: true })
    wx.showLoading({ title: '正在生成报告...' })
    try {
      const data = { scores: parentScores }
      if (childScores) data.childScores = childScores
      const res = await wx.cloud.callFunction({ name: 'assessment', data })
      if (res.result.code === 429) {
        wx.showModal({
          title: '本月评估次数已用完',
          content: `每月最多评估 ${this.data.assessLimit} 次，下月自动重置。如有需要请联系客服。`,
          showCancel: false,
          confirmText: '知道了',
        })
        this.setData({ submitting: false, assessRemain: 0 })
        wx.hideLoading()
        return
      }
      if (res.result.code !== 0) throw new Error(res.result.message)
      const result = res.result.data
      const app = getApp()
      const child = app.globalData.currentChild
      const db = wx.cloud.database()
      const record = await db.collection('assessments').add({
        data: { childId: child?._id || '', scores: parentScores, childScores: childScores || null, result, createdAt: db.serverDate() },
      })
      wx.setStorageSync('lastAssessmentResult', result)
      wx.setStorageSync('lastAssessmentScores', parentScores)
      if (result.remain !== undefined) this.setData({ assessRemain: result.remain })
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
