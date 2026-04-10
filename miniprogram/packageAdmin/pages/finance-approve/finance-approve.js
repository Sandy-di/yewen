// packageAdmin/pages/finance-approve/finance-approve.js
const { mockApi } = require('../../../utils/mock-data')
const { formatMoney, getTagClass, showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    pendingList: [],
    loading: true
  },

  onLoad() { this.loadPending() },

  async loadPending() {
    try {
      const res = await mockApi.getFinanceList()
      const pendingList = res.data.filter(r => r.status === 'pending').map(r => ({
        ...r,
        totalIncomeFormatted: formatMoney(r.totalIncome),
        totalExpenseFormatted: formatMoney(r.totalExpense)
      }))
      this.setData({ pendingList, loading: false })
    } catch (e) { this.setData({ loading: false }) }
  },

  async onApprove(e) {
    const id = e.currentTarget.dataset.id
    showLoading('审批中...')
    setTimeout(() => {
      hideLoading()
      showToast('已审批通过', 'success')
      this.loadPending()
    }, 800)
  },

  onReject(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '拒绝原因',
      editable: true,
      placeholderText: '请输入拒绝原因',
      success: (res) => {
        if (res.confirm) {
          showToast('已退回修改')
          this.loadPending()
        }
      }
    })
  }
})
