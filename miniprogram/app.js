// miniprogram/app.js
App({
  onLaunch() {
    wx.cloud.init({
      env: 'wenwen2code-4gxuthj048ae0fb0',
      traceUser: true,
    })
  },
  globalData: {
    currentChild: null,
  },
})
