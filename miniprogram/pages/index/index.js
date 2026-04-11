// pages/index/index.js
const api = require('../../utils/api')
const { formatDate, formatRemainTime, VOTE_STATUS_MAP, getTagClass } = require('../../utils/util')

Page({
  data: {
    currentTab: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'active', label: '进行中' },
      { key: 'ended', label: '已结束' }
    ],
    voteList: [],
    loading: true,
    refreshing: false,
    communityName: '翠湖花园',
    currentRole: 'owner',
    showAnnouncement: true,
    latestAnnouncement: null
  },

  onLoad() {
    this.syncRole()
    this.loadVotes()
    this.loadLatestAnnouncement()
  },

  onShow() {
    this.syncRole()
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
  },

  syncRole() {
    const app = getApp()
    const role = app.globalData.currentRole || 'owner'
    if (this.data.currentRole !== role) {
      this.setData({ currentRole: role })
    }
  },

  onSwitchRole() {
    wx.navigateTo({ url: '/pages/mine/role-switch/role-switch' })
  },

  onPullDownRefresh() {
    this.setData({ refreshing: true })
    this.loadVotes().then(() => {
      wx.stopPullDownRefresh()
      this.setData({ refreshing: false })
    })
  },

  async loadVotes() {
    try {
      const res = await mockApi.getVoteList({ status: this.data.currentTab })
      const voteList = res.data.map(vote => {
        const statusInfo = VOTE_STATUS_MAP[vote.status]
        const participationRate = vote.totalProperties > 0 
          ? Math.round(vote.participatedCount / vote.totalProperties * 100) 
          : 0
        return {
          ...vote,
          statusLabel: statusInfo.label,
          statusTagClass: getTagClass(statusInfo.type),
          participationRate,
          remainTime: vote.status === 'active' ? formatRemainTime(vote.endTime) : '',
          endTimeFormatted: formatDate(vote.endTime, 'MM月DD日 HH:mm')
        }
      })
      this.setData({ voteList, loading: false })
    } catch (e) {
      console.error('加载投票列表失败', e)
      this.setData({ loading: false })
    }
  },

  async loadLatestAnnouncement() {
    try {
      const res = await api.getAnnouncementList()
      const latest = res.data.find(a => a.isTop) || res.data[0]
      if (latest) {
        this.setData({ latestAnnouncement: latest })
      }
    } catch (e) {
      console.error('加载公告失败', e)
    }
  },

  onTabChange(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ currentTab: key, loading: true })
    this.loadVotes()
  },

  onVoteItemTap(e) {
    const voteId = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/vote/detail/detail?voteId=${voteId}` })
  },

  onAnnouncementTap() {
    if (this.data.latestAnnouncement) {
      wx.navigateTo({ url: `/pages/announce/detail/detail?id=${this.data.latestAnnouncement.id}` })
    }
  },

  onCloseAnnouncement() {
    this.setData({ showAnnouncement: false })
  },

  onSearchTap() {
    wx.showToast({ title: '搜索功能开发中', icon: 'none' })
  },

  onCreateVote() {
    const app = getApp()
    if (app.globalData.currentRole !== 'committee') {
      wx.showToast({ title: '仅业委会成员可发起投票', icon: 'none' })
      return
    }
    wx.navigateTo({ url: '/pages/vote/create/create' })
  }
})
