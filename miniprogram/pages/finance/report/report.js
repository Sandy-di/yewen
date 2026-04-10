// pages/finance/report/report.js
const { showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    form: {
      reportMonth: '',
      items: [
        { itemType: 'income', category: '', amount: '', description: '' }
      ]
    },
    currentTab: 'income',
    submitting: false,
    monthPickerVisible: false
  },

  onLoad() {
    const now = new Date()
    const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    this.setData({ 'form.reportMonth': month })
  },

  onTabChange(e) {
    this.setData({ currentTab: e.currentTarget.dataset.tab })
  },

  onMonthChange(e) {
    this.setData({ 'form.reportMonth': e.detail.value, monthPickerVisible: false })
  },

  toggleMonthPicker() {
    this.setData({ monthPickerVisible: !this.data.monthPickerVisible })
  },

  onItemTypeChange(e) {
    const idx = e.currentTarget.dataset.idx
    this.setData({ [`form.items[${idx}].itemType`]: e.detail.value })
  },

  onCategoryInput(e) {
    const idx = e.currentTarget.dataset.idx
    this.setData({ [`form.items[${idx}].category`]: e.detail.value })
  },

  onAmountInput(e) {
    const idx = e.currentTarget.dataset.idx
    this.setData({ [`form.items[${idx}].amount`]: e.detail.value })
  },

  onDescInput(e) {
    const idx = e.currentTarget.dataset.idx
    this.setData({ [`form.items[${idx}].description`]: e.detail.value })
  },

  onAddItem() {
    const items = this.data.form.items
    items.push({ itemType: this.data.currentTab === 'income' ? 'income' : 'expense', category: '', amount: '', description: '' })
    this.setData({ 'form.items': items })
  },

  onRemoveItem(e) {
    const idx = e.currentTarget.dataset.idx
    if (this.data.form.items.length <= 1) {
      showToast('至少保留一条记录')
      return
    }
    const items = this.data.form.items
    items.splice(idx, 1)
    this.setData({ 'form.items': items })
  },

  async onSubmit() {
    const { form } = this.data
    if (!form.reportMonth) {
      showToast('请选择报表月份')
      return
    }
    const validItems = form.items.filter(i => i.category && i.amount)
    if (validItems.length === 0) {
      showToast('请至少填写一条收支记录')
      return
    }
    const invalidItem = validItems.find(i => isNaN(Number(i.amount)) || Number(i.amount) <= 0)
    if (invalidItem) {
      showToast('金额必须为正数')
      return
    }

    this.setData({ submitting: true })
    showLoading('正在提交...')

    setTimeout(() => {
      hideLoading()
      showToast('报表已提交，等待业委会审批', 'success')
      setTimeout(() => wx.navigateBack(), 1500)
      this.setData({ submitting: false })
    }, 1000)
  }
})
