const api = require('../../utils/api.js')

Page({
  data: {
    title: '',
    content: '',
    categoryIndex: 0,
    categories: [
      { value: 'service', label: '服务问题' },
      { value: 'fee', label: '收费问题' },
      { value: 'safety', label: '安全隐患' },
      { value: 'environment', label: '环境卫生' },
      { value: 'other', label: '其他' },
    ],
    photos: [],
    submitting: false,
  },

  onTitleInput(e) { this.setData({ title: e.detail.value }) },
  onContentInput(e) { this.setData({ content: e.detail.value }) },
  onCategoryChange(e) { this.setData({ categoryIndex: e.detail.value }) },

  choosePhoto() {
    const count = 6 - this.data.photos.length
    wx.chooseMedia({
      count,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        for (const file of res.tempFiles) {
          try {
            const result = await api.uploadFile(file.tempFilePath)
            if (result.url) {
              this.setData({ photos: [...this.data.photos, result.url] })
            }
          } catch (e) {
            console.error('上传图片失败:', e)
          }
        }
      }
    })
  },

  removePhoto(e) {
    const index = e.currentTarget.dataset.index
    const photos = [...this.data.photos]
    photos.splice(index, 1)
    this.setData({ photos })
  },

  previewPhoto(e) {
    const url = e.currentTarget.dataset.url
    wx.previewImage({ current: url, urls: this.data.photos })
  },

  async submit() {
    const { title, content, categories, categoryIndex, photos } = this.data
    if (!title.trim()) { wx.showToast({ title: '请输入标题', icon: 'none' }); return }
    if (!content.trim()) { wx.showToast({ title: '请输入内容', icon: 'none' }); return }

    this.setData({ submitting: true })
    try {
      await api.createComplaint({
        title: title.trim(),
        content: content.trim(),
        category: categories[categoryIndex].value,
        photos,
      })
      wx.showToast({ title: '投诉已提交', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (e) {
      wx.showToast({ title: e.message || '提交失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },
})