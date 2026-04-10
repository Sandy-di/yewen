// pages/mine/mine.js
const { ROLE_MAP, VERIFY_LEVEL_MAP } = require('../../utils/util')

Page({
  data: {
    userInfo: null,
    currentRole: 'owner',
    roleLabel: '业主',
    roleIcon: '🏠',
    verifiedLevel: 2,
    verifyLabel: '',
    properties: [],
    menuList: [
      { id: 'my_votes', icon: '🗳️', label: '我的投票', url: '/pages/index/index' },
      { id: 'my_repairs', icon: '🔧', label: '我的报修', url: '/pages/repair/list/list' },
      { id: 'my_verify', icon: '🔐', label: '身份核验', action: 'verify' },
      { id: 'my_property', icon: '🏠', label: '房产管理', url: '/pages/mine/property/property' },
      { id: 'role_switch', icon: '🔄', label: '角色切换', url: '/pages/mine/role-switch/role-switch' },
      { id: 'settings', icon: '⚙️', label: '设置', url: '/pages/mine/settings/settings' }
    ],
    adminMenuList: [
      { id: 'vote_manage', icon: '📋', label: '投票管理', role: 'committee' },
      { id: 'work_order', icon: '📝', label: '工单处理', role: 'property' },
      { id: 'finance_approve', icon: '💰', label: '财务审批', role: 'committee' },
      { id: 'announce_publish', icon: '📢', label: '发布公告', role: 'committee' }
    ]
  },

  onLoad() {
    this.initUserInfo()
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 })
    }
    this.initUserInfo()
  },

  initUserInfo() {
    const app = getApp()
    const userInfo = app.globalData.userInfo
    const currentRole = app.globalData.currentRole
    if (userInfo) {
      const roleInfo = ROLE_MAP[currentRole]
      const verifyInfo = VERIFY_LEVEL_MAP[userInfo.verifiedLevel || 1]
      this.setData({
        userInfo,
        currentRole,
        roleLabel: roleInfo.label,
        roleIcon: roleInfo.icon,
        verifiedLevel: userInfo.verifiedLevel || 1,
        verifyLabel: verifyInfo.label,
        properties: userInfo.properties || []
      })
    }
  },

  onMenuTap(e) {
    const menu = e.currentTarget.dataset.menu
    if (menu.action === 'verify') {
      wx.navigateTo({ url: '/pages/vote/verify/verify?level=' + (this.data.verifiedLevel + 1) })
      return
    }
    if (menu.url) {
      // 对于tab页面使用switchTab
      if (menu.url.includes('/pages/index/') || menu.url.includes('/pages/repair/list/')) {
        wx.switchTab({ url: menu.url })
      } else {
        wx.navigateTo({ url: menu.url })
      }
    }
  },

  onAdminMenuTap(e) {
    const menu = e.currentTarget.dataset.menu
    const urlMap = {
      vote_manage: '/packageAdmin/pages/vote-manage/vote-manage',
      work_order: '/packageAdmin/pages/work-order/work-order',
      finance_approve: '/packageAdmin/pages/finance-approve/finance-approve',
      announce_publish: '/packageAdmin/pages/announce-publish/announce-publish'
    }
    wx.navigateTo({ url: urlMap[menu.id] })
  },

  onAvatarTap() {
    wx.navigateTo({ url: '/pages/mine/settings/settings' })
  }
})
