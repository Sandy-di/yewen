// pages/finance/detail/detail.js
const api = require('../../../utils/api')
const { formatMoney, formatDate } = require('../../../utils/util')

Page({
  data: {
    reportId: '',
    report: null,
    loading: true,
    incomeItems: [],
    expenseItems: [],
    totalIncome: 0,
    totalExpense: 0,
    incomeCategories: [],
    expenseCategories: [],
    attachments: []
  },

  onLoad(options) {
    this.setData({ reportId: options.reportId })
    this.loadDetail()
  },

  async loadDetail() {
    try {
      const report = await api.getFinanceDetail(this.data.reportId)
      if (!report) return

      const incomeItems = report.items.filter(i => i.itemType === 'income')
      const expenseItems = report.items.filter(i => i.itemType === 'expense')
      
      // 按类别汇总
      const incomeCategories = this.groupByCategory(incomeItems)
      const expenseCategories = this.groupByCategory(expenseItems)

      // 处理附件
      const attachments = (report.attachments || []).map(a => ({
        ...a,
        isPdf: a.name && a.name.endsWith('.pdf'),
        isDoc: a.name && (a.name.endsWith('.doc') || a.name.endsWith('.docx')),
        sizeLabel: a.size ? (a.size >= 1024 * 1024 ? (a.size / 1024 / 1024).toFixed(1) + 'MB' : (a.size / 1024).toFixed(1) + 'KB') : ''
      }))

      this.setData({
        report,
        loading: false,
        incomeItems,
        expenseItems,
        totalIncome: formatMoney(report.totalIncome),
        totalExpense: formatMoney(report.totalExpense),
        incomeCategories,
        expenseCategories,
        attachments
      })
      this.addFormattedFields()
    } catch (e) {
      console.error('加载财务详情失败', e)
      this.setData({ loading: false })
    }
  },

  groupByCategory(items) {
    const map = {}
    items.forEach(item => {
      if (!map[item.category]) {
        map[item.category] = { category: item.category, amount: 0, count: 0 }
      }
      map[item.category].amount += item.amount
      map[item.category].count++
    })
    return Object.values(map).sort((a, b) => b.amount - a.amount)
  },

  addFormattedFields() {
    // WXML 不支持 .toFixed()，必须在 JS 中预处理
    const { report, incomeItems, expenseItems, incomeCategories, expenseCategories } = this.data
    
    const processedReport = {
      ...report,
      totalIncomeFmt: formatMoney(report.totalIncome),
      totalExpenseFmt: formatMoney(report.totalExpense)
    }
    
    const processedIncomeItems = incomeItems.map(item => ({
      ...item,
      amountFmt: '¥' + item.amount.toFixed(2)
    }))
    
    const processedExpenseItems = expenseItems.map(item => ({
      ...item,
      amountFmt: '¥' + item.amount.toFixed(2)
    }))
    
    const processedIncomeCategories = incomeCategories.map(item => ({
      ...item,
      amountFmt: '¥' + item.amount.toFixed(2),
      percent: report.totalIncome > 0 ? (item.amount / report.totalIncome * 100).toFixed(0) : 0
    }))
    
    const processedExpenseCategories = expenseCategories.map(item => ({
      ...item,
      amountFmt: '¥' + item.amount.toFixed(2),
      percent: report.totalExpense > 0 ? (item.amount / report.totalExpense * 100).toFixed(0) : 0
    }))
    
    this.setData({
      report: processedReport,
      incomeItems: processedIncomeItems,
      expenseItems: processedExpenseItems,
      incomeCategories: processedIncomeCategories,
      expenseCategories: processedExpenseCategories
    })
  },

  onAttachmentTap(e) {
    const { url, name } = e.currentTarget.dataset
    if (!url) return
    // 图片预览，文档复制链接
    const ext = (name || '').split('.').pop().toLowerCase()
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    if (imageExts.includes(ext)) {
      wx.previewImage({ current: url, urls: [url] })
    } else {
      wx.setClipboardData({
        data: url,
        success: () => wx.showToast({ title: '链接已复制', icon: 'success' })
      })
    }
  },

  onShareAppMessage() {
    const report = this.data.report
    return {
      title: report ? `${report.month} 财务公示` : '财务公示详情',
      path: `/pages/finance/detail/detail?reportId=${this.data.reportId}`
    }
  },

  onShareTimeline() {
    const report = this.data.report
    return {
      title: report ? `${report.month} 财务公示` : '财务公示详情'
    }
  }
})
