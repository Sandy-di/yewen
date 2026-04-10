// pages/finance/list/list.js
const { mockApi } = require('../../../utils/mock-data')
const { formatMoney, getTagClass } = require('../../../utils/util')

Page({
  data: {
    financeList: [],
    loading: true,
    summary: {
      totalIncome: 0,
      totalExpense: 0,
      balance: 0
    },
    announcements: [],
    currentRole: 'owner'
  },

  onLoad() {
    const app = getApp()
    this.setData({ currentRole: app.globalData.currentRole })
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 })
    }
    this.loadData()
  },

  async loadData() {
    try {
      const [financeRes, announceRes] = await Promise.all([
        mockApi.getFinanceList(),
        mockApi.getAnnouncementList()
      ])
      
      const publishedReports = financeRes.data.filter(r => r.status === 'published')
      const latestReport = publishedReports[0]
      
      const financeList = financeRes.data.map(r => ({
        ...r,
        statusLabel: r.status === 'published' ? '已公示' : r.status === 'pending' ? '待审批' : '草稿',
        statusTagClass: r.status === 'published' ? 'tag-success' : r.status === 'pending' ? 'tag-warning' : 'tag-grey',
        totalIncomeFormatted: formatMoney(r.totalIncome),
        totalExpenseFormatted: formatMoney(r.totalExpense),
        balanceFormatted: formatMoney(r.balance)
      }))

      this.setData({
        financeList,
        loading: false,
        summary: latestReport ? {
          totalIncome: latestReport.totalIncome,
          totalExpense: latestReport.totalExpense,
          balance: latestReport.balance,
          totalIncomeFormatted: formatMoney(latestReport.totalIncome),
          totalExpenseFormatted: formatMoney(latestReport.totalExpense),
          balanceFormatted: formatMoney(latestReport.balance)
        } : { totalIncome: 0, totalExpense: 0, balance: 0 },
        announcements: announceRes.data.slice(0, 3)
      })
    } catch (e) {
      console.error('加载财务数据失败', e)
      this.setData({ loading: false })
    }
  },

  onFinanceTap(e) {
    const reportId = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/finance/detail/detail?reportId=${reportId}` })
  },

  onAnnounceTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/announce/detail/detail?id=${id}` })
  },

  onViewAllAnnouncements() {
    wx.navigateTo({ url: '/pages/announce/list/list' })
  },

  onReportFinance() {
    wx.navigateTo({ url: '/pages/finance/report/report' })
  }
})
