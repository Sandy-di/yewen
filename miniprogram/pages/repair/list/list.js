// pages/repair/list/list.js
const api = require('../../../utils/api')
const { formatDate, ORDER_STATUS_MAP, REPAIR_CATEGORIES, getTagClass } = require('../../../utils/util')

Page({
  data: {
    currentTab: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'submitted', label: '已提交' },
      { key: 'processing', label: '处理中' },
      { key: 'pending_check', label: '待验收' },
      { key: 'completed', label: '已完结' }
    ],
    orderList: [],
    loading: true,
    currentRole: 'owner'
  },

  onLoad() {
    const app = getApp()
    this.setData({ currentRole: app.globalData.currentRole })
    this.loadOrders()
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    this.loadOrders()
  },

  onPullDownRefresh() {
    this.loadOrders().then(() => wx.stopPullDownRefresh())
  },

  async loadOrders() {
    try {
      const res = await api.getOrderList({ status: this.data.currentTab })
      const orderList = res.data.map(order => {
        const statusInfo = ORDER_STATUS_MAP[order.status]
        const categoryInfo = REPAIR_CATEGORIES.find(c => c.value === order.category)
        return {
          ...order,
          statusLabel: statusInfo.label,
          statusTagClass: getTagClass(statusInfo.type),
          statusIcon: statusInfo.icon,
          categoryIcon: categoryInfo ? categoryInfo.icon : '📌',
          categoryLabel: categoryInfo ? categoryInfo.label : '其他',
          createdAtFormatted: formatDate(order.createdAt, 'MM-DD HH:mm')
        }
      })
      this.setData({ orderList, loading: false })
    } catch (e) {
      console.error('加载工单列表失败', e)
      this.setData({ loading: false })
    }
  },

  onTabChange(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ currentTab: key, loading: true })
    this.loadOrders()
  },

  onOrderTap(e) {
    const orderId = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/repair/detail/detail?orderId=${orderId}` })
  },

  onCreateRepair() {
    wx.navigateTo({ url: '/pages/repair/create/create' })
  }
})
