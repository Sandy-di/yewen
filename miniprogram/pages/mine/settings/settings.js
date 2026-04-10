// pages/mine/settings/settings.js
Page({
  data: {
    settings: {
      notification: true,
      voteReminder: true,
      repairNotify: true,
      financeNotify: false
    }
  },

  onLoad() {
    const saved = wx.getStorageSync('user_settings')
    if (saved) this.setData({ settings: saved })
  },

  onSwitchChange(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ [`settings.${key}`]: e.detail.value })
    wx.setStorageSync('user_settings', this.data.settings)
  },

  onClearCache() {
    wx.showModal({
      title: '提示',
      content: '确认清除本地缓存？不会影响您的账号数据。',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync()
          wx.showToast({ title: '缓存已清除', icon: 'success' })
        }
      }
    })
  },

  onAbout() {
    wx.showModal({
      title: '关于',
      content: '智慧社区业主小程序 v1.0.0\n\n让社区治理更透明、更高效',
      showCancel: false
    })
  }
})
