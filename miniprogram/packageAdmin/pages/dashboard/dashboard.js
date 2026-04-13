// packageAdmin/pages/dashboard/dashboard.js
const api = require('../../../utils/api')
const { showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    loading: true,
    dashboard: null,
    overview: null
  },

  onLoad() { this.loadData() },

  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh())
  },

  async loadData() {
    try {
      const [dashboard, overview] = await Promise.all([
        api.getDashboard(),
        api.getOverview()
      ])
      this.setData({
        dashboard,
        overview,
        loading: false
      })
    } catch (e) {
      this.setData({ loading: false })
      showToast('加载失败')
    }
  },

  onNavigateTo(e) {
    const url = e.currentTarget.dataset.url
    if (url) wx.navigateTo({ url })
  }
})
