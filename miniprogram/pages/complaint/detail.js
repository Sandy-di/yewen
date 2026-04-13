const api = require('../../utils/api.js')
const app = getApp()

Page({
  data: {
    detail: null,
    id: '',
    role: '',
    canReply: false,
    statusMap: { submitted: '待回复', replied: '已回复', resolved: '已解决', closed: '已关闭' },
    categoryMap: { service: '服务', fee: '收费', safety: '安全', environment: '环境', other: '其他' },
    replyTypeMap: { reply: '回复', supervise: '督导', resolve: '结案' },
  },

  onLoad(options) {
    const id = options.id
    const role = app.globalData.currentRole || 'owner'
    this.setData({ id, role, canReply: role === 'property' || role === 'committee' })
    this.loadDetail()
  },

  async loadDetail() {
    try {
      const detail = await api.getComplaintDetail(this.data.id)
      if (detail) {
        detail.createdAt = detail.createdAt ? new Date(detail.createdAt).toLocaleString('zh-CN') : ''
        if (detail.replies) {
          detail.replies = detail.replies.map(r => ({
            ...r,
            createdAt: r.createdAt ? new Date(r.createdAt).toLocaleString('zh-CN') : '',
          }))
        }
        this.setData({ detail })
      }
    } catch (e) {
      console.error('加载投诉详情失败:', e)
    }
  },

  previewPhoto(e) {
    const url = e.currentTarget.dataset.url
    wx.previewImage({ current: url, urls: this.data.detail.photos || [] })
  },

  showReplyInput() {
    const self = this
    wx.showModal({
      title: '回复投诉',
      editable: true,
      placeholderText: '请输入回复内容',
      success: async (res) => {
        if (res.confirm && res.content) {
          try {
            await api.replyComplaint(self.data.id, res.content, 'reply')
            wx.showToast({ title: '回复成功', icon: 'success' })
            self.loadDetail()
          } catch (e) {
            wx.showToast({ title: e.message || '回复失败', icon: 'none' })
          }
        }
      }
    })
  },

  supervise() {
    const self = this
    wx.showModal({
      title: '督导意见',
      editable: true,
      placeholderText: '请输入督导意见',
      success: async (res) => {
        if (res.confirm && res.content) {
          try {
            await api.replyComplaint(self.data.id, res.content, 'supervise')
            wx.showToast({ title: '督导成功', icon: 'success' })
            self.loadDetail()
          } catch (e) {
            wx.showToast({ title: e.message || '操作失败', icon: 'none' })
          }
        }
      }
    })
  },

  resolve() {
    const self = this
    wx.showModal({
      title: '确认结案',
      content: '确定要结案此投诉吗？',
      editable: true,
      placeholderText: '结案说明（可选）',
      success: async (res) => {
        if (res.confirm) {
          try {
            await api.replyComplaint(self.data.id, res.content || '业委会确认结案', 'resolve')
            wx.showToast({ title: '已结案', icon: 'success' })
            self.loadDetail()
          } catch (e) {
            wx.showToast({ title: e.message || '操作失败', icon: 'none' })
          }
        }
      }
    })
  },
})