// pages/mine/community-select/community-select.js
const api = require('../../../utils/api')
const { API_BASE_URL } = require('../../../utils/config')

Page({
  data: {
    keyword: '',
    communities: [],
    loading: false,
    searched: false
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.searchCommunities()
  },

  onClearSearch() {
    this.setData({ keyword: '', communities: [], searched: false })
  },

  async searchCommunities() {
    const keyword = this.data.keyword.trim()
    if (!keyword) {
      wx.showToast({ title: '请输入小区名称', icon: 'none' })
      return
    }
    this.setData({ loading: true, searched: true })
    try {
      const res = await api.getCommunityList({ keyword, pageSize: 50 })
      this.setData({ communities: res.data || [], loading: false })
    } catch (e) {
      console.error('搜索社区失败', e)
      this.setData({ loading: false })
      wx.showToast({ title: '搜索失败', icon: 'none' })
    }
  },

  async onSelectCommunity(e) {
    const community = e.currentTarget.dataset.item
    if (!community) return

    wx.showLoading({ title: '绑定中...' })
    try {
      // 调用后端绑定社区
      const app = getApp()
      const token = wx.getStorageSync('token')
      if (!token || app.globalData.useMock || app.isMockToken(token)) {
        // mock 模式下直接更新本地
        app.globalData.communityInfo = { name: community.name, id: community.id }
        if (app.globalData.userInfo) {
          app.globalData.userInfo.communityId = community.id
          app.globalData.userInfo.communityName = community.name
          wx.setStorageSync('userInfo', app.globalData.userInfo)
        }
        wx.hideLoading()
        wx.showToast({ title: '已选择社区', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 1000)
        return
      }

      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${API_BASE_URL}/api/users/community/bind`,
          method: 'PUT',
          header: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          data: { communityId: community.id },
          timeout: 15000,
          success: (r) => resolve(r),
          fail: (e) => reject(e)
        })
      })

      wx.hideLoading()
      if (res.statusCode === 200 && res.data.success) {
        app.globalData.communityInfo = { name: community.name, id: community.id }
        if (app.globalData.userInfo) {
          app.globalData.userInfo.communityId = community.id
          app.globalData.userInfo.communityName = community.name
          wx.setStorageSync('userInfo', app.globalData.userInfo)
        }
        wx.showToast({ title: '已选择社区', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 1000)
      } else {
        wx.showToast({ title: res.data?.detail || '绑定失败', icon: 'none' })
      }
    } catch (e) {
      wx.hideLoading()
      console.error('绑定社区失败', e)
      wx.showToast({ title: '绑定失败', icon: 'none' })
    }
  }
})
