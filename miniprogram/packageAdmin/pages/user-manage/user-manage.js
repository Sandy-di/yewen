// packageAdmin/pages/user-manage/user-manage.js
const api = require('../../../utils/api')
const { ROLE_MAP, showToast, showLoading, hideLoading } = require('../../../utils/util')

Page({
  data: {
    userList: [],
    loading: true,
    currentTab: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'owner', label: '业主' },
      { key: 'property', label: '物业' },
      { key: 'committee', label: '业委会' }
    ],
    page: 1,
    total: 0,
    hasMore: true
  },

  onLoad() { this.loadUsers() },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true })
    this.loadUsers().then(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore()
    }
  },

  onTabChange(e) {
    this.setData({ currentTab: e.currentTarget.dataset.key, page: 1, hasMore: true, loading: true })
    this.loadUsers()
  },

  async loadUsers() {
    try {
      const params = { page: 1, pageSize: 20 }
      if (this.data.currentTab !== 'all') {
        params.role = this.data.currentTab
      }
      const res = await api.getUserList(params)
      const userList = (res.data || []).map(u => ({
        ...u,
        roleLabel: ROLE_MAP[u.role]?.label || u.role,
        roleIcon: ROLE_MAP[u.role]?.icon || ''
      }))
      this.setData({
        userList,
        total: res.total || 0,
        page: 1,
        hasMore: userList.length >= 20,
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
      const params = { page, pageSize: 20 }
      if (this.data.currentTab !== 'all') {
        params.role = this.data.currentTab
      }
      const res = await api.getUserList(params)
      const newUsers = (res.data || []).map(u => ({
        ...u,
        roleLabel: ROLE_MAP[u.role]?.label || u.role,
        roleIcon: ROLE_MAP[u.role]?.icon || ''
      }))
      const userList = this.data.userList.concat(newUsers)
      this.setData({
        userList,
        page,
        hasMore: newUsers.length >= 20,
        loading: false
      })
    } catch (e) {
      this.setData({ loading: false })
    }
  },

  onUserTap(e) {
    const user = e.currentTarget.dataset.user
    const roleOptions = ['业主', '物业', '业委会']
    wx.showActionSheet({
      itemList: [
        user.isActive ? '禁用用户' : '启用用户',
        '修改角色'
      ],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.toggleActive(user)
        } else if (res.tapIndex === 1) {
          this.changeRole(user)
        }
      }
    })
  },

  async toggleActive(user) {
    const newActive = !user.isActive
    try {
      showLoading('处理中...')
      await api.toggleUserActive(user.id, newActive)
      hideLoading()
      showToast(newActive ? '已启用' : '已禁用', 'success')
      this.loadUsers()
    } catch (err) {
      hideLoading()
      showToast(err.message || '操作失败')
    }
  },

  changeRole(user) {
    const roles = ['owner', 'property', 'committee']
    const roleLabels = ['业主', '物业', '业委会']
    wx.showActionSheet({
      itemList: roleLabels,
      success: async (res) => {
        const newRole = roles[res.tapIndex]
        if (newRole === user.role) return
        try {
          showLoading('修改中...')
          await api.updateUserRole(user.id, newRole)
          hideLoading()
          showToast('角色已修改', 'success')
          this.loadUsers()
        } catch (err) {
          hideLoading()
          showToast(err.message || '修改失败')
        }
      }
    })
  }
})
