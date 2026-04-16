// pages/announce/detail/detail.js
const api = require('../../../utils/api')

Page({
  data: {
    id: '',
    announcement: null,
    loading: true
  },

  onLoad(options) {
    this.setData({ id: options.id })
    this.loadDetail()
  },

  async loadDetail() {
    try {
      const announcement = await api.getAnnouncementDetail(this.data.id)
      this.setData({ announcement, loading: false })
    } catch (e) {
      console.error('加载公告详情失败', e)
      this.setData({ loading: false })
    }
  },

  onShareAppMessage() {
    return {
      title: this.data.announcement?.title || '社区公告',
      path: `/pages/announce/detail/detail?id=${this.data.id}`
    }
  },

  onShareTimeline() {
    return {
      title: this.data.announcement?.title || '社区公告'
    }
  }
})
