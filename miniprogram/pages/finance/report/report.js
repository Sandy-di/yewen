// pages/finance/report/report.js
const api = require('../../../utils/api')
const { showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    form: {
      reportMonth: '',
      items: [
        { itemType: 'income', category: '', amount: '', description: '' }
      ],
      attachments: []
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

  onAddAttachment() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx'],
      success: async (res) => {
        const file = res.tempFiles[0]
        if (file.size > 10 * 1024 * 1024) {
          showToast('文件不能超过10MB')
          return
        }
        showLoading('上传中...')
        try {
          const result = await api.uploadFile(file.path)
          const name = file.name || result.filename || '附件'
          const ext = name.split('.').pop().toLowerCase()
          const attachment = {
            name,
            url: result.url,
            size: file.size,
            isPdf: ext === 'pdf',
            isDoc: ext === 'doc' || ext === 'docx',
            sizeLabel: file.size >= 1024 * 1024
              ? (file.size / 1024 / 1024).toFixed(1) + 'MB'
              : (file.size / 1024).toFixed(1) + 'KB'
          }
          const attachments = this.data.form.attachments.concat(attachment)
          this.setData({ 'form.attachments': attachments })
          hideLoading()
        } catch (err) {
          hideLoading()
          showToast('上传失败')
        }
      }
    })
  },

  onRemoveAttachment(e) {
    const idx = e.currentTarget.dataset.idx
    const attachments = this.data.form.attachments
    attachments.splice(idx, 1)
    this.setData({ 'form.attachments': attachments })
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

    try {
      const submitItems = validItems.map(i => ({
        itemType: i.itemType,
        category: i.category,
        amount: Number(i.amount),
        description: i.description || ''
      }))
      const submitAttachments = (form.attachments || []).map(a => ({
        name: a.name,
        url: a.url,
        size: a.size
      }))
      await api.createFinanceReport({
        month: form.reportMonth,
        title: `${form.reportMonth} 物业收支报表`,
        items: submitItems,
        attachments: submitAttachments
      })
      hideLoading()
      showToast('报表已提交，等待业委会审批', 'success')
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (err) {
      hideLoading()
      showToast(err.message || '提交失败')
    } finally {
      this.setData({ submitting: false })
    }
  }
})
