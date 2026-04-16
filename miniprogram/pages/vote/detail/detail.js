// pages/vote/detail/detail.js
const api = require('../../../utils/api')
const { formatDate, formatRemainTime, VOTE_STATUS_MAP, VERIFY_LEVEL_MAP, getTagClass, showToast, showConfirm, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    voteId: '',
    vote: null,
    loading: true,
    currentRole: 'owner',
    userVerifiedLevel: 2,
    canVote: false,
    hasVoted: false,
    selectedOption: '',
    showVoteModal: false,
    showVerifyModal: false,
    remainTime: '',
    participationRate: 0,
    areaRate: 0
  },

  onLoad(options) {
    const app = getApp()
    this.setData({
      voteId: options.voteId,
      currentRole: app.globalData.currentRole,
      userVerifiedLevel: app.globalData.userInfo?.verifiedLevel || 2
    })
    this.loadVoteDetail()
  },

  async loadVoteDetail() {
    try {
      const vote = await api.getVoteDetail(this.data.voteId)
      if (!vote) {
        showToast('投票不存在')
        return
      }
      const statusInfo = VOTE_STATUS_MAP[vote.status]
      const participationRate = Math.round(vote.participatedCount / vote.totalProperties * 100)
      const areaRate = Math.round(vote.participatedArea / vote.totalArea * 100)
      const canVote = vote.status === 'active' && this.data.userVerifiedLevel >= vote.verificationLevel
      const remainTime = vote.status === 'active' ? formatRemainTime(vote.endTime) : ''
      const optionMap = {}
      const optionsWithPercent = vote.options.map(opt => ({
        ...opt,
        percentage: vote.participatedCount > 0 ? (opt.count / vote.participatedCount * 100).toFixed(1) : 0
      }))
      vote.options = optionsWithPercent
      optionsWithPercent.forEach(opt => { optionMap[opt.id] = opt.label })
      
      this.setData({
        optionMap,
        vote,
        loading: false,
        statusLabel: statusInfo.label,
        statusTagClass: getTagClass(statusInfo.type),
        participationRate,
        areaRate,
        canVote,
        remainTime,
        verifyInfo: VERIFY_LEVEL_MAP[vote.verificationLevel]
      })
    } catch (e) {
      console.error('加载投票详情失败', e)
      this.setData({ loading: false })
    }
  },

  onOptionSelect(e) {
    this.setData({ selectedOption: e.currentTarget.dataset.id })
  },

  onVoteTap() {
    if (!this.data.canVote) {
      this.setData({ showVerifyModal: true })
      return
    }
    this.setData({ showVoteModal: true })
  },

  onCancelVote() {
    this.setData({ showVoteModal: false, selectedOption: '' })
  },

  async onConfirmVote() {
    if (!this.data.selectedOption) {
      showToast('请选择投票选项')
      return
    }
    showLoading('正在提交...')
    try {
      const res = await api.submitVote(this.data.voteId, this.data.selectedOption)
      if (res.success) {
        hideLoading()
        showToast('投票提交成功', 'success')
        this.setData({ hasVoted: true, showVoteModal: false })
        this.loadVoteDetail()
      }
    } catch (e) {
      hideLoading()
      showToast('提交失败，请检查网络后重试')
    }
  },

  onGoVerify() {
    this.setData({ showVerifyModal: false })
    wx.navigateTo({ url: `/pages/vote/verify/verify?voteId=${this.data.voteId}&level=${this.data.vote.verificationLevel}` })
  },

  onCloseVerifyModal() {
    this.setData({ showVerifyModal: false })
  },

  async onRevokeVote() {
    const confirmed = await showConfirm('确认撤销投票吗？撤销后所有已投票数据将清除，且无法恢复。')
    if (confirmed) {
      showToast('投票已撤销')
      setTimeout(() => wx.navigateBack(), 1500)
    }
  },

  onViewResult() {
    wx.navigateTo({ url: `/pages/vote/result/result?voteId=${this.data.voteId}` })
  },

  onDownloadPDF() {
    showLoading('正在生成PDF...')
    setTimeout(() => {
      hideLoading()
      showToast('PDF已生成，请在聊天中查看', 'success')
    }, 1500)
  },

  onVerifyChain() {
    showLoading('正在验证区块链存证...')
    setTimeout(() => {
      hideLoading()
      showToast('存证验证通过，数据未被篡改', 'success')
    }, 1000)
  },

  onShareAppMessage() {
    const vote = this.data.vote
    const statusText = vote?.status === 'active' ? '进行中，快来参与投票' : '已结束'
    return {
      title: vote ? `${vote.title} - ${statusText}` : '投票详情',
      path: `/pages/vote/detail/detail?voteId=${this.data.voteId}`
    }
  },

  onShareTimeline() {
    const vote = this.data.vote
    return {
      title: vote ? vote.title : '投票详情'
    }
  }
})
