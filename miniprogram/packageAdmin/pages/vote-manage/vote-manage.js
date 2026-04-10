// packageAdmin/pages/vote-manage/vote-manage.js
const { mockApi } = require('../../../utils/mock-data')
const { VOTE_STATUS_MAP, getTagClass, formatDate } = require('../../../utils/util')

Page({
  data: {
    voteList: [],
    loading: true,
    currentTab: 'active',
    tabs: [
      { key: 'active', label: '进行中' },
      { key: 'ended', label: '已结束' },
      { key: 'draft', label: '草稿' }
    ]
  },

  onLoad() {
    this.loadVotes()
  },

  async loadVotes() {
    try {
      const res = await mockApi.getVoteList({ status: this.data.currentTab })
      const voteList = res.data.map(v => ({
        ...v,
        statusLabel: VOTE_STATUS_MAP[v.status]?.label,
        statusTagClass: getTagClass(VOTE_STATUS_MAP[v.status]?.type),
        participationRate: Math.round(v.participatedCount / v.totalProperties * 100)
      }))
      this.setData({ voteList, loading: false })
    } catch (e) {
      this.setData({ loading: false })
    }
  },

  onTabChange(e) {
    this.setData({ currentTab: e.currentTarget.dataset.key, loading: true })
    this.loadVotes()
  },

  onCreateVote() {
    wx.navigateTo({ url: '/pages/vote/create/create' })
  },

  onVoteTap(e) {
    const voteId = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/vote/detail/detail?voteId=${voteId}` })
  }
})
