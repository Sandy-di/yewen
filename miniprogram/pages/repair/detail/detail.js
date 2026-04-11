// pages/repair/detail/detail.js
const api = require('../../../utils/api')
const { formatDate, ORDER_STATUS_MAP, REPAIR_CATEGORIES, getTagClass, showToast, showLoading, hideLoading, showConfirm } = require('../../../utils/util')

Page({
  data: {
    orderId: '',
    order: null,
    loading: true,
    currentRole: 'owner',
    showRatingModal: false,
    rating: 5,
    ratingComment: '',
    showReworkModal: false,
    reworkReason: ''
  },

  onLoad(options) {
    const app = getApp()
    this.setData({
      orderId: options.orderId,
      currentRole: app.globalData.currentRole
    })
    this.loadOrderDetail()
  },

  async loadOrderDetail() {
    try {
      const order = await mockApi.getOrderDetail(this.data.orderId)
      if (!order) {
        showToast('工单不存在')
        return
      }
      const statusInfo = ORDER_STATUS_MAP[order.status]
      const categoryInfo = REPAIR_CATEGORIES.find(c => c.value === order.category)
      this.setData({
        order,
        loading: false,
        statusLabel: statusInfo.label,
        statusTagClass: getTagClass(statusInfo.type),
        statusIcon: statusInfo.icon,
        categoryLabel: categoryInfo ? categoryInfo.label : '其他'
      })
    } catch (e) {
      console.error('加载工单详情失败', e)
      this.setData({ loading: false })
    }
  },

  onPreviewPhoto(e) {
    const { url, urls } = e.currentTarget.dataset
    wx.previewImage({
      current: url,
      urls: urls || [url]
    })
  },

  onCallWorker() {
    if (this.data.order.acceptorPhone) {
      wx.makePhoneCall({ phoneNumber: this.data.order.acceptorPhone.replace(/\*/g, '0') })
    }
  },

  onUrge() {
    showToast('已催单，物业会尽快处理', 'success')
  },

  onAccept() {
    showConfirm('确认验收通过？验收通过后工单将完结。').then(confirmed => {
      if (confirmed) {
        showLoading('正在提交...')
        setTimeout(() => {
          hideLoading()
          showToast('验收通过', 'success')
          this.loadOrderDetail()
        }, 800)
      }
    })
  },

  onShowRating() {
    this.setData({ showRatingModal: true })
  },

  onRatingChange(e) {
    this.setData({ rating: e.currentTarget.dataset.score })
  },

  onRatingCommentInput(e) {
    this.setData({ ratingComment: e.detail.value })
  },

  async onSubmitRating() {
    showLoading('正在提交...')
    try {
      await mockApi.rateOrder(this.data.orderId, this.data.rating, this.data.ratingComment)
      hideLoading()
      showToast('评价提交成功', 'success')
      this.setData({ showRatingModal: false })
      this.loadOrderDetail()
    } catch (e) {
      hideLoading()
      showToast('提交失败，请重试')
    }
  },

  onShowRework() {
    this.setData({ showReworkModal: true })
  },

  onReworkReasonInput(e) {
    this.setData({ reworkReason: e.detail.value })
  },

  async onSubmitRework() {
    if (!this.data.reworkReason.trim()) {
      showToast('请填写复修原因')
      return
    }
    showLoading('正在提交...')
    try {
      await api.reworkOrder(this.data.orderId, this.data.reworkReason)
      hideLoading()
      showToast('已申请复修', 'success')
      this.setData({ showReworkModal: false })
      this.loadOrderDetail()
    } catch (e) {
      hideLoading()
      showToast('提交失败，请重试')
    }
  },

  onCancel() {
    showConfirm('确认取消工单？取消后需要重新提交报修。').then(confirmed => {
      if (confirmed) {
        showToast('工单已取消')
        setTimeout(() => wx.navigateBack(), 1500)
      }
    })
  },

  onCloseModal() {
    this.setData({ showRatingModal: false, showReworkModal: false })
  }
})
