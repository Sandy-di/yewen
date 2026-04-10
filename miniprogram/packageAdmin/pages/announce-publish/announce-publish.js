// packageAdmin/pages/announce-publish/announce-publish.js
const { showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    form: {
      title: '',
      content: '',
      type: 'notice',
      isTop: false
    },
    typeOptions: [
      { value: 'notice', label: '物业通知' },
      { value: 'vote', label: '投票通知' },
      { value: 'finance', label: '财务公示' }
    ],
    submitting: false
  },

  onTitleInput(e) { this.setData({ 'form.title': e.detail.value }) },
  onContentInput(e) { this.setData({ 'form.content': e.detail.value }) },
  onTypeSelect(e) { this.setData({ 'form.type': e.currentTarget.dataset.value }) },
  onTopChange(e) { this.setData({ 'form.isTop': e.detail.value }) },

  async onSubmit() {
    const { form } = this.data
    if (!form.title.trim()) { showToast('请输入公告标题'); return }
    if (!form.content.trim()) { showToast('请输入公告内容'); return }

    this.setData({ submitting: true })
    showLoading('发布中...')
    setTimeout(() => {
      hideLoading()
      showToast('公告已发布', 'success')
      setTimeout(() => wx.navigateBack(), 1500)
      this.setData({ submitting: false })
    }, 800)
  }
})
