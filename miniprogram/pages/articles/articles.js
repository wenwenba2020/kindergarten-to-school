const ARTICLES = [
  {
    id: 1,
    title: '幼升小，如何科学衔接（倾听）',
    source: '人民日报',
    date: '2025-03',
    summary: '分析幼小衔接中"抢跑式领先"的危害，强调激发学习兴趣比超前学知识更重要，教育部将从专业指导、社会宣传、规范监管三方面推进幼小衔接工作。',
    url: 'https://paper.people.com.cn/rmrb/pc/content/202503/26/content_30064134.html',
    tag: '政策解读',
  },
  {
    id: 2,
    title: '学前教育法6月1日起施行 幼儿园不得采用小学化的教育方式',
    source: '央视网',
    date: '2025-05',
    summary: '《中华人民共和国学前教育法》自2025年6月1日正式施行，明确幼儿园不得采用小学化教育方式，不得教授小学课程；校外培训机构不得对学前儿童开展培训。',
    url: 'https://edu.cctv.com/2025/05/30/ARTIkKML0YvGK8Ym7RkIWHsg250530.shtml',
    tag: '政策法规',
  },
  {
    id: 3,
    title: '幼升小，如何科学衔接',
    source: '新华网',
    date: '2025-03',
    summary: '提出幼儿园和小学应"双向奔赴"的衔接理念，介绍通过建立幼小衔接学习共同体、开展联合教研等创新做法，实现教师和教学方法的有效衔接。',
    url: 'https://www.news.cn/politics/20250326/3d1dd8edaff9458586460a96b726301e/c.html',
    tag: '实践案例',
  },
  {
    id: 4,
    title: '幼小衔接需关注儿童学习特征',
    source: '中国教育报',
    date: '2024-10',
    summary: '从儿童心理发展规律分析幼小衔接，建议从身心准备、生活准备、社会准备、学习准备四个方面入手，培养良好习惯而非超前学知识。',
    url: 'https://www.cnr.cn/jy/sy/sytjB/20241001/t20241001_526925893.shtml',
    tag: '科学理念',
  },
  {
    id: 5,
    title: '用"双向衔接"助孩子迈好关键一步',
    source: '光明日报',
    date: '2024-07',
    summary: '强调幼小衔接应是"双向衔接"而非单向靠拢，批评培训机构贩卖焦虑，提出小学低年级课程应注重游戏化和生活化，帮助儿童平稳过渡。',
    url: 'https://www.news.cn/comments/20240716/1bea257f55e14d6889a39d9a4ac6e05a/c.html',
    tag: '家长必读',
  },
  {
    id: 6,
    title: '家庭教育：幼升小如何科学衔接？家长要做好这些准备',
    source: '澎湃新闻',
    date: '2024-05',
    summary: '汇集专家观点，强调身心准备、生活准备、社会准备、学习准备四大方面，批评家长焦虑和攀比心理，建议尊重儿童个体差异和发展连续性。',
    url: 'https://www.thepaper.cn/newsDetail_forward_27586550',
    tag: '家长必读',
  },
  {
    id: 7,
    title: '科学幼小衔接怎么"衔"？如何"接"？',
    source: '人民教育',
    date: '2024-05',
    summary: '反对将衔接理解为提前学习小学课程，建议家长通过游戏、阅读等自然方式激发学习兴趣，重点培养自理能力、交往能力和专注力。',
    url: 'https://view.inews.qq.com/a/20240520A04VYN00',
    tag: '实操指南',
  },
  {
    id: 8,
    title: '幼小衔接新规：教育部指导意见全解读',
    source: '搜狐教育',
    date: '2025-06',
    summary: '解读教育部《幼儿园入学准备教育指导要点》，强调在情感、社会性、认知、语言、运动等多方面帮助孩子做准备，家长应理解科学衔接的真正含义。',
    url: 'https://www.sohu.com/a/903801119_121956425',
    tag: '政策解读',
  },
]

Page({
  data: { articles: ARTICLES },

  openArticle(e) {
    const { url, title } = e.currentTarget.dataset
    if (!url) return wx.showToast({ title: '暂无原文链接', icon: 'none' })
    wx.navigateTo({ url: `/pages/webview/webview?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}` })
  },
})
