// pages/vote/verify/verify.js
const { VERIFY_LEVEL_MAP, showToast, showLoading, hideLoading } = require('../../../utils/util')
const api = require('../../../utils/api')

Page({
  data: {
    voteId: '',
    requiredLevel: 3,
    currentLevel: 2,
    verifyInfo: null,
    step: 'select', // select | form | verifying | success | fail
    // L1
    phone: '',
    smsCode: '',
    smsSent: false,
    smsCountdown: 0,
    // L2
    building: '',
    unit: '',
    roomNo: '',
    // L3
    realName: '',
    idCard: '',
    propertyCertPhotos: [],
    // L4
    faceVerifying: false
  },

  onLoad(options) {
    const app = getApp()
    const requiredLevel = Number(options.level) || 3
    const currentLevel = app.globalData.userInfo?.verifiedLevel || 2
    this.setData({
      voteId: options.voteId || '',
      requiredLevel,
      currentLevel,
      verifyInfo: VERIFY_LEVEL_MAP[requiredLevel]
    })
  },

  // 选择核验等级
  onSelectLevel(e) {
    const level = e.currentTarget.dataset.level
    if (level <= this.data.currentLevel) {
      showToast('您已完成该等级核验')
      return
    }
    this.setData({ requiredLevel: level, verifyInfo: VERIFY_LEVEL_MAP[level] })
  },

  // 开始核验
  onStartVerify() {
    this.setData({ step: 'form' })
  },

  // 发送验证码
  onSendSms() {
    if (this.data.smsCountdown > 0) return
    if (!this.data.phone) {
      showToast('请输入手机号')
      return
    }
    showToast('验证码已发送', 'success')
    this.setData({ smsSent: true, smsCountdown: 60 })
    this.startCountdown()
  },

  startCountdown() {
    if (this.data.smsCountdown <= 0) return
    setTimeout(() => {
      this.setData({ smsCountdown: this.data.smsCountdown - 1 })
      this.startCountdown()
    }, 1000)
  },

  // 提交L1核验
  async onSubmitL1() {
    if (!this.data.phone || !this.data.smsCode) {
      showToast('请填写手机号和验证码')
      return
    }
    await this.doVerify(1)
  },

  // 提交L2核验
  async onSubmitL2() {
    if (!this.data.building || !this.data.unit || !this.data.roomNo) {
      showToast('请填写完整房产信息')
      return
    }
    await this.doVerify(2)
  },

  // 提交L3核验
  async onSubmitL3() {
    if (!this.data.realName) {
      showToast('请输入姓名')
      return
    }
    if (!this.data.idCard || this.data.idCard.length < 15) {
      showToast('请输入正确的身份证号')
      return
    }
    if (this.data.propertyCertPhotos.length === 0) {
      showToast('请上传房产证照片')
      return
    }
    await this.doVerify(3)
  },

  // L4 人脸核验
  onStartFaceVerify() {
    this.setData({ faceVerifying: true, step: 'verifying' })
    // 模拟微信人脸核身
    setTimeout(() => {
      this.setData({ step: 'success', faceVerifying: false })
      showToast('人脸核验通过', 'success')
    }, 3000)
  },

  // 通用核验方法
  async doVerify(level) {
    this.setData({ step: 'verifying' })
    showLoading('核验中...')
    try {
      const res = await api.verifyIdentity(level, {})
      hideLoading()
      if (res.success) {
        this.setData({ step: 'success', currentLevel: level })
        // 更新全局状态
        const app = getApp()
        if (app.globalData.userInfo) {
          app.globalData.userInfo.verifiedLevel = Math.max(app.globalData.userInfo.verifiedLevel, level)
          wx.setStorageSync('userInfo', app.globalData.userInfo)
        }
        showToast('核验通过', 'success')
      }
    } catch (e) {
      hideLoading()
      this.setData({ step: 'fail' })
      showToast('核验失败，请重试')
    }
  },

  // 上传房产证照片
  onChoosePhoto() {
    const photos = this.data.propertyCertPhotos
    if (photos.length >= 3) {
      showToast('最多上传3张')
      return
    }
    wx.chooseImage({
      count: 3 - photos.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({ propertyCertPhotos: [...photos, ...res.tempFilePaths] })
      }
    })
  },

  onRemovePhoto(e) {
    const idx = e.currentTarget.dataset.idx
    const photos = this.data.propertyCertPhotos
    photos.splice(idx, 1)
    this.setData({ propertyCertPhotos: photos })
  },

  // 返回投票
  onGoBack() {
    wx.navigateBack()
  },

  // 重新核验
  onRetry() {
    this.setData({ step: 'form' })
  }
})
