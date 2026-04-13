const api = require('../../utils/api.js')
const app = getApp()

Page({
  data: {
    list: [],
    loading: false,
    currentStatus: '',
    page: 1,
    hasMore: true,
    statusMap: { submitted: '待回复', replied: '已回复', resolved: '已解决', closed: '已关闭' },
    categoryMap: { service: '服务', fee: '收费', safety: '安全', environment: '环境', other: '其他' },
    role: '',
  },

  onLoad() {
    this.setData({ role: app.globalData.currentRole || 'owner' })
    this.loadList()
  },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true, list: [] })
    this.loadList().then(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) this.loadList()
  },

  onFilterTap(e) {
    const status = e.currentTarget.dataset.status
    this.setData({ currentStatus: status, page: 1, hasMore: true, list: [] })
    this.loadList()
  },

  async loadList() {
    if (this.data.loading) return
    this.setData({ loading: true })
    try {
      const res = await api.getComplaintList({
        status: this.data.currentStatus || undefined,
        page: this.data.page,
        pageSize: 10,
      })
      const items = (res.data || []).map(item => ({
        ...item,
        createdAt: item.createdAt ? new Date(item.createdAt).toLocaleString('zh-CN') : '',
      }))
      this.setData({
        list: this.data.page === 1 ? items : [...this.data.list, ...items],
        hasMore: items.length >= 10,
        page: this.data.page + 1,
      })
    } catch (e) {
      console.error('加载投诉列表失败:', e)
    } finally {
      this.setData({ loading: false })
    }
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/complaint/detail?id=${id}` })
  },

  goCreate() {
    wx.navigateTo({ url: '/pages/complaint/create' })
  },
})