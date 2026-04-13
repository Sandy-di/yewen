// packageAdmin/pages/community-manage/community-manage.js
const api = require('../../../utils/api')
const { showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    communityList: [],
    loading: true,
    page: 1,
    total: 0,
    hasMore: true
  },

  onLoad() { this.loadCommunities() },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true })
    this.loadCommunities().then(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore()
    }
  },

  async loadCommunities() {
    try {
      const res = await api.getCommunityList({ page: 1, pageSize: 20 })
      this.setData({
        communityList: res.data || [],
        total: res.total || 0,
        page: 1,
        hasMore: (res.data || []).length >= 20,
        loading: false
      })
    } catch (e) {
      this.setData({ loading: false })
      showToast('加载失败')
    }
  },

  async loadMore() {
    const page = this.data.page + 1
    this.setData({ loading: true })
    try {
      const res = await api.getCommunityList({ page, pageSize: 20 })
      const newList = this.data.communityList.concat(res.data || [])
      this.setData({
        communityList: newList,
        page,
        hasMore: (res.data || []).length >= 20,
        loading: false
      })
    } catch (e) {
      this.setData({ loading: false })
    }
  },

  onCommunityTap(e) {
    const id = e.currentTarget.dataset.id
    const name = e.currentTarget.dataset.name
    wx.showActionSheet({
      itemList: ['编辑社区信息'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.showEditModal(id, name)
        }
      }
    })
  },

  showEditModal(id, currentName) {
    // 找到当前社区数据
    const community = this.data.communityList.find(c => c.id === id)
    const that = this
    // 使用自定义弹窗方式，因为 wx.showModal 只支持单行输入
    that.setData({
      editingId: id,
      editForm: {
        name: community ? community.name : currentName,
        totalUnits: community ? String(community.totalUnits || 0) : '',
        totalArea: community ? String(community.totalArea || 0) : '',
        address: community ? (community.address || '') : ''
      },
      showEditDialog: true
    })
  },

  onEditInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`editForm.${field}`]: e.detail.value })
  },

  async onSubmitEdit() {
    const { editingId, editForm } = this.data
    if (!editForm.name || !editForm.name.trim()) {
      showToast('请输入社区名称')
      return
    }
    try {
      showLoading('保存中...')
      await api.updateCommunity(editingId, {
        name: editForm.name.trim(),
        totalUnits: parseInt(editForm.totalUnits) || 0,
        totalArea: parseFloat(editForm.totalArea) || 0,
        address: editForm.address || ''
      })
      hideLoading()
      showToast('已更新', 'success')
      this.setData({ showEditDialog: false })
      this.loadCommunities()
    } catch (err) {
      hideLoading()
      showToast(err.message || '更新失败')
    }
  },

  onCancelEdit() {
    this.setData({ showEditDialog: false })
  },

  onCreateCommunity() {
    const that = this
    that.setData({
      editForm: { name: '', totalUnits: '500', totalArea: '30000', address: '' },
      editingId: null,
      showEditDialog: true
    })
  },

  async onSubmitCreate() {
    const { editForm } = this.data
    if (!editForm.name || !editForm.name.trim()) {
      showToast('请输入社区名称')
      return
    }
    try {
      showLoading('创建中...')
      await api.createCommunity({
        name: editForm.name.trim(),
        totalUnits: parseInt(editForm.totalUnits) || 0,
        totalArea: parseFloat(editForm.totalArea) || 0,
        address: editForm.address || ''
      })
      hideLoading()
      showToast('创建成功', 'success')
      this.setData({ showEditDialog: false })
      this.loadCommunities()
    } catch (err) {
      hideLoading()
      showToast(err.message || '创建失败')
    }
  }
})
