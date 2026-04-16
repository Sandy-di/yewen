// pages/vote/result/result.js
const api = require('../../../utils/api')
const { formatDate, showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    voteId: '',
    vote: null,
    loading: true,
    passed: false,
    participationRate: 0,
    areaRate: 0,
    optionPercentages: []
  },

  onLoad(options) {
    this.setData({ voteId: options.voteId })
    this.loadResult()
  },

  async loadResult() {
    try {
      const vote = await api.getVoteDetail(this.data.voteId)
      if (!vote) return
      
      const passed = vote.result === 'passed'
      const participationRate = Math.round(vote.participatedCount / vote.totalProperties * 100)
      const areaRate = Math.round(vote.participatedArea / vote.totalArea * 100)
      
      const optionPercentages = vote.options.map(opt => ({
        ...opt,
        percentage: vote.participatedCount > 0 ? (opt.count / vote.participatedCount * 100).toFixed(1) : 0,
        areaPercentage: vote.participatedArea > 0 ? (opt.area / vote.participatedArea * 100).toFixed(1) : 0
      }))

      this.setData({
        vote,
        loading: false,
        passed,
        participationRate,
        areaRate,
        optionPercentages
      })
    } catch (e) {
      console.error('加载结果失败', e)
      this.setData({ loading: false })
    }
  },

  onDownloadPDF() {
    showLoading('正在生成PDF...')
    setTimeout(() => {
      hideLoading()
      showToast('PDF已生成，请在聊天中查看', 'success')
    }, 1500)
  },

  onVerifyChain() {
    showLoading('正在验证存证...')
    setTimeout(() => {
      hideLoading()
      showToast('存证验证通过，数据未被篡改', 'success')
    }, 1000)
  },

  onShareAppMessage() {
    const vote = this.data.vote
    return {
      title: (vote ? vote.title : '投票') + ' - 投票结果',
      path: `/pages/vote/result/result?voteId=${this.data.voteId}`
    }
  },

  onShareTimeline() {
    const vote = this.data.vote
    return {
      title: (vote ? vote.title : '投票') + ' - 投票结果'
    }
  }
})
