// pages/announce/list/list.js
const { mockApi } = require('../../../utils/mock-data')
const { formatDate } = require('../../../utils/util')

Page({
  data: {
    currentTab: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'notice', label: '物业通知' },
      { key: 'vote', label: '投票通知' },
      { key: 'finance', label: '财务公示' }
    ],
    announcements: [],
    loading: true
  },

  onLoad() {
    this.loadAnnouncements()
  },

  async loadAnnouncements() {
    try {
      const res = await mockApi.getAnnouncementList()
      let list = res.data
      if (this.data.currentTab !== 'all') {
        list = list.filter(a => a.type === this.data.currentTab)
      }
      this.setData({ announcements: list, loading: false })
    } catch (e) {
      console.error('加载公告失败', e)
      this.setData({ loading: false })
    }
  },

  onTabChange(e) {
    this.setData({ currentTab: e.currentTarget.dataset.key, loading: true })
    this.loadAnnouncements()
  },

  onAnnounceTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/announce/detail/detail?id=${id}` })
  }
})
