// pages/vote/create/create.js
const { mockApi } = require('../../../utils/mock-data')
const { showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    form: {
      title: '',
      description: '',
      verificationLevel: 2,
      voteType: 'double_majority',
      startTime: '',
      endTime: '',
      options: [
        { id: 'opt1', label: '' },
        { id: 'opt2', label: '' }
      ]
    },
    verifyLevels: [
      { value: 1, label: 'L1 手机核验', desc: '短信验证码' },
      { value: 2, label: 'L2 房产核验', desc: '手机+房产信息' },
      { value: 3, label: 'L3 双重核验', desc: '姓名+身份证+房产证' },
      { value: 4, label: 'L4 人脸核验', desc: '微信人脸核身' }
    ],
    voteTypes: [
      { value: 'double_majority', label: '双过半', desc: '参与人数及面积均过半' },
      { value: 'double_three_quarters', label: '双四分之三', desc: '参与人数及面积均达3/4' }
    ],
    submitting: false,
    showVerifyPicker: false,
    showTypePicker: false,
    showStartPicker: false,
    showEndPicker: false,
    minDate: '',
    maxDate: ''
  },

  onLoad() {
    // 设置最小开始时间为当前时间后1小时
    const now = new Date()
    now.setHours(now.getHours() + 1)
    const minDate = this.formatDateTimeLocal(now)
    // 最大结束时间：3个月后
    const max = new Date(now)
    max.setMonth(max.getMonth() + 3)
    const maxDate = this.formatDateTimeLocal(max)
    this.setData({ minDate, maxDate })
  },

  formatDateTimeLocal(date) {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    const h = String(date.getHours()).padStart(2, '0')
    const min = String(date.getMinutes()).padStart(2, '0')
    return `${y}-${m}-${d} ${h}:${min}`
  },

  onTitleInput(e) {
    this.setData({ 'form.title': e.detail.value })
  },

  onDescInput(e) {
    this.setData({ 'form.description': e.detail.value })
  },

  onVerifyLevelChange(e) {
    const level = Number(e.currentTarget.dataset.value)
    this.setData({ 'form.verificationLevel': level, showVerifyPicker: false })
    
    // 智能推荐：双四分之三事项必须选L4
    if (this.data.form.voteType === 'double_three_quarters' && level < 4) {
      showToast('双四分之三事项建议使用L4核验等级')
    }
  },

  onVoteTypeChange(e) {
    const type = e.currentTarget.dataset.value
    this.setData({ 'form.voteType': type, showTypePicker: false })
    
    // 自动推荐核验等级
    if (type === 'double_three_quarters') {
      this.setData({ 'form.verificationLevel': 4 })
      showToast('已自动升级为L4人脸核验')
    }
  },

  onStartTimeChange(e) {
    this.setData({ 'form.startTime': e.detail.value, showStartPicker: false })
  },

  onEndTimeChange(e) {
    const endTime = e.detail.value
    if (this.data.form.startTime && endTime <= this.data.form.startTime) {
      showToast('结束时间必须晚于开始时间')
      return
    }
    this.setData({ 'form.endTime': endTime, showEndPicker: false })
  },

  onOptionInput(e) {
    const idx = e.currentTarget.dataset.idx
    this.setData({ [`form.options[${idx}].label`]: e.detail.value })
  },

  onAddOption() {
    if (this.data.form.options.length >= 5) {
      showToast('最多添加5个选项')
      return
    }
    const options = this.data.form.options
    options.push({ id: 'opt' + (options.length + 1), label: '' })
    this.setData({ 'form.options': options })
  },

  onRemoveOption(e) {
    const idx = e.currentTarget.dataset.idx
    if (this.data.form.options.length <= 2) {
      showToast('至少保留2个选项')
      return
    }
    const options = this.data.form.options
    options.splice(idx, 1)
    this.setData({ 'form.options': options })
  },

  togglePicker(e) {
    const type = e.currentTarget.dataset.type
    const key = `show${type}Picker`
    this.setData({ [key]: !this.data[key] })
  },

  async onSubmit() {
    const { form } = this.data
    
    // 校验
    if (!form.title.trim()) {
      showToast('请填写投票标题')
      return
    }
    if (form.title.length > 100) {
      showToast('标题不超过100字')
      return
    }
    if (!form.startTime) {
      showToast('请选择开始时间')
      return
    }
    if (!form.endTime) {
      showToast('请选择结束时间')
      return
    }
    if (form.endTime <= form.startTime) {
      showToast('结束时间必须晚于开始时间')
      return
    }
    const emptyOption = form.options.find(o => !o.label.trim())
    if (emptyOption) {
      showToast('请填写所有选项内容')
      return
    }

    this.setData({ submitting: true })
    showLoading('正在提交...')

    try {
      const res = await mockApi.createVote(form)
      hideLoading()
      if (res.success) {
        showToast('投票已发起', 'success')
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (e) {
      hideLoading()
      showToast('发起失败，请检查网络后重试')
    } finally {
      this.setData({ submitting: false })
    }
  }
})
