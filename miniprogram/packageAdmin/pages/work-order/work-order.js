// packageAdmin/pages/work-order/work-order.js
const api = require('../../../utils/api')
const { ORDER_STATUS_MAP, REPAIR_CATEGORIES, getTagClass, showToast } = require('../../../utils/util')

Page({
  data: {
    orderList: [],
    loading: true,
    currentTab: 'submitted',
    tabs: [
      { key: 'submitted', label: '待接单' },
      { key: 'processing', label: '处理中' },
      { key: 'pending_check', label: '待验收' },
      { key: 'completed', label: '已完结' }
    ]
  },

  onLoad() { this.loadOrders() },

  async loadOrders() {
    try {
      const res = await api.getOrderList({ status: this.data.currentTab })
      const orderList = res.data.map(o => ({
        ...o,
        statusLabel: ORDER_STATUS_MAP[o.status]?.label,
        statusTagClass: getTagClass(ORDER_STATUS_MAP[o.status]?.type),
        categoryLabel: REPAIR_CATEGORIES.find(c => c.value === o.category)?.label || '其他'
      }))
      this.setData({ orderList, loading: false })
    } catch (e) { this.setData({ loading: false }) }
  },

  onTabChange(e) {
    this.setData({ currentTab: e.currentTarget.dataset.key, loading: true })
    this.loadOrders()
  },

  async onAcceptOrder(e) {
    const id = e.currentTarget.dataset.id
    try {
      await api.acceptOrder(id)
      showToast('已接单', 'success')
      this.loadOrders()
    } catch (err) {
      showToast(err.message || '接单失败')
    }
  },

  onOrderTap(e) {
    wx.navigateTo({ url: `/pages/repair/detail/detail?orderId=${e.currentTarget.dataset.id}` })
  }
})
