// pages/repair/create/create.js
const { REPAIR_CATEGORIES, showToast, showLoading, hideLoading, isValidPhone } = require('../../../utils/util')
const api = require('../../../utils/api')

Page({
  data: {
    form: {
      category: '',
      subCategory: '',
      description: '',
      photos: [],
      contactPhone: '',
      isAnonymous: false
    },
    categories: REPAIR_CATEGORIES,
    selectedCategory: null,
    showSubCategories: false,
    submitting: false,
    draftSaved: false
  },

  onLoad() {
    const app = getApp()
    const phone = app.globalData.userInfo?.phone || ''
    this.setData({ 'form.contactPhone': phone })
    this.loadDraft()
  },

  onUnload() {
    this.saveDraft()
  },

  loadDraft() {
    try {
      const draft = wx.getStorageSync('repair_draft')
      if (draft) {
        this.setData({ form: draft })
        const cat = REPAIR_CATEGORIES.find(c => c.value === draft.category)
        if (cat) this.setData({ selectedCategory: cat })
      }
    } catch (e) {}
  },

  saveDraft() {
    const { form } = this.data
    if (form.description || form.category) {
      wx.setStorageSync('repair_draft', form)
    }
  },

  clearDraft() {
    wx.removeStorageSync('repair_draft')
  },

  onCategorySelect(e) {
    const value = e.currentTarget.dataset.value
    const cat = REPAIR_CATEGORIES.find(c => c.value === value)
    this.setData({ 
      selectedCategory: cat, 
      'form.category': value,
      showSubCategories: true,
      'form.subCategory': ''
    })
  },

  onSubCategorySelect(e) {
    const label = e.currentTarget.dataset.label
    this.setData({ 
      'form.subCategory': label,
      showSubCategories: false
    })
  },

  onDescriptionInput(e) {
    this.setData({ 'form.description': e.detail.value })
  },

  onChoosePhoto() {
    const photos = this.data.form.photos
    if (photos.length >= 4) {
      showToast('最多上传4张照片')
      return
    }
    wx.chooseImage({
      count: 4 - photos.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({ 'form.photos': [...photos, ...res.tempFilePaths] })
      }
    })
  },

  onRemovePhoto(e) {
    const idx = e.currentTarget.dataset.idx
    const photos = this.data.form.photos
    photos.splice(idx, 1)
    this.setData({ 'form.photos': photos })
  },

  onPreviewPhoto(e) {
    const url = e.currentTarget.dataset.url
    wx.previewImage({ current: url, urls: this.data.form.photos })
  },

  onPhoneInput(e) {
    this.setData({ 'form.contactPhone': e.detail.value })
  },

  onAnonymousChange(e) {
    this.setData({ 'form.isAnonymous': e.detail.value })
  },

  async onSubmit() {
    const { form } = this.data

    if (!form.category) {
      showToast('请选择报修类型')
      return
    }
    if (!form.description.trim()) {
      showToast('请描述您的问题')
      return
    }
    if (form.description.trim().length < 10) {
      showToast('描述至少10个字')
      return
    }
    if (!form.contactPhone) {
      showToast('请填写联系电话')
      return
    }
    if (!isValidPhone(form.contactPhone)) {
      showToast('请输入正确的手机号')
      return
    }

    this.setData({ submitting: true })
    showLoading('正在提交...')

    try {
      const res = await api.submitRepair(form)
      hideLoading()
      if (res.success) {
        this.clearDraft()
        showToast('报修已提交！物业会尽快处理', 'success')
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (e) {
      hideLoading()
      showToast('提交失败，请检查网络后重试')
    } finally {
      this.setData({ submitting: false })
    }
  }
})
