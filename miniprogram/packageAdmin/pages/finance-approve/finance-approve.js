// packageAdmin/pages/finance-approve/finance-approve.js
const api = require('../../../utils/api')
const { formatMoney, getTagClass, showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    pendingList: [],
    loading: true
  },

  onLoad() { this.loadPending() },

  async loadPending() {
    try {
      const res = await api.getFinanceList()
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
    try {
      showLoading('审批中...')
      await api.approveFinance(id)
      hideLoading()
      showToast('已审批通过', 'success')
      this.loadPending()
    } catch (err) {
      hideLoading()
      showToast(err.message || '审批失败')
    }
  },

  onReject(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '拒绝原因',
      editable: true,
      placeholderText: '请输入拒绝原因',
      success: async (res) => {
        if (res.confirm) {
          try {
            const reason = res.content || ''
            showLoading('处理中...')
            await api.rejectFinance(id, reason)
            hideLoading()
            showToast('已退回修改', 'success')
            this.loadPending()
          } catch (err) {
            hideLoading()
            showToast(err.message || '操作失败')
          }
        }
      }
    })
  }
})
