// pages/mine/role-switch/role-switch.js
// 角色切换页面 — 支持一键切换三个测试身份

const { API_BASE_URL } = require('../../../utils/config')

const TEST_USERS = [
  {
    openid: 'oDev_Owner_001',
    label: '业主',
    name: '张先生',
    icon: '🏠',
    desc: '查看投票、参与投票、发起报修、查看公示',
    role: 'owner',
    mockUser: {
      userId: 'U20260410001',
      openid: 'oDev_Owner_001',
      nickname: '张先生',
      phone: '138****5678',
      avatar: '',
      role: 'owner',
      verifiedLevel: 2,
      communityId: 'C001',
      communityName: '黑金时代',
      communityAddress: '长沙市天心区暮云街道云塘社区',
      identities: { isOwner: true, isProperty: false, isCommittee: false },
      properties: [
        { propertyId: 'P20260410001', building: '3栋', unit: '1单元', roomNo: '502', usableArea: 89.5, isDefault: true }
      ]
    }
  },
  {
    openid: 'oDev_Property_001',
    label: '物业',
    name: '物业服务中心',
    icon: '🔧',
    desc: '接收工单、更新工单状态、上报财务报表',
    role: 'property',
    mockUser: {
      userId: 'U20260410002',
      openid: 'oDev_Property_001',
      nickname: '物业服务中心',
      phone: '139****1234',
      avatar: '',
      role: 'property',
      verifiedLevel: 3,
      communityId: 'C001',
      communityName: '黑金时代',
      communityAddress: '长沙市天心区暮云街道云塘社区',
      identities: { isOwner: false, isProperty: true, isCommittee: false },
      properties: []
    }
  },
  {
    openid: 'oDev_Committee_001',
    label: '业委会',
    name: '张主任',
    icon: '📋',
    desc: '业主全部功能 + 发起投票、审批财务、发布公告',
    role: 'committee',
    mockUser: {
      userId: 'U20260410003',
      openid: 'oDev_Committee_001',
      nickname: '张主任',
      phone: '137****8899',
      avatar: '',
      role: 'committee',
      verifiedLevel: 4,
      communityId: 'C001',
      communityName: '黑金时代',
      communityAddress: '长沙市天心区暮云街道云塘社区',
      identities: { isOwner: true, isProperty: false, isCommittee: true },
      properties: [
        { propertyId: 'P20260410002', building: '1栋', unit: '2单元', roomNo: '101', usableArea: 120.0, isDefault: true }
      ]
    }
  }
]

Page({
  data: {
    currentOpenid: '',
    currentRole: '',
    testUsers: TEST_USERS,
    switching: false,
  },

  onLoad() {
    this.syncCurrentState()
  },

  onShow() {
    this.syncCurrentState()
  },

  syncCurrentState() {
    const app = getApp()
    const userInfo = app.globalData.userInfo
    this.setData({
      currentOpenid: userInfo?.openid || '',
      currentRole: app.globalData.currentRole || '',
    })
  },

  onSwitchUser(e) {
    const { openid, label, role } = e.currentTarget.dataset
    const app = getApp()

    // 已是当前身份则忽略
    if (openid === this.data.currentOpenid) return
    if (this.data.switching) return

    // 角色切换是测试功能，始终先本地切换
    const testUser = TEST_USERS.find(u => u.openid === openid)
    if (!testUser) return

    // 1. 立即更新本地状态
    app.globalData.userInfo = { ...testUser.mockUser }
    app.globalData.currentRole = testUser.role
    app.globalData.communityInfo = testUser.mockUser.communityName
      ? { name: testUser.mockUser.communityName, id: testUser.mockUser.communityId, address: testUser.mockUser.communityAddress }
      : null
    wx.setStorageSync('userInfo', app.globalData.userInfo)
    wx.setStorageSync('token', 'mock_token_' + Date.now())

    this.setData({
      currentOpenid: openid,
      currentRole: testUser.role,
      switching: false,
    })

    wx.showToast({ title: `已切换为${label}（${testUser.name}）`, icon: 'success' })

    // 2. 后台尝试同步后端（不阻塞 UI）
    this.tryBackendSwitch(openid)
  },

  // 后台同步后端（静默失败）
  tryBackendSwitch(openid) {
    const app = getApp()
    const token = wx.getStorageSync('token')
    if (app.globalData.useMock || app.isMockToken(token)) return

    const isTestMode = app.globalData.userInfo?.openid?.startsWith('oDev_')

    wx.request({
      url: `${API_BASE_URL}${isTestMode ? '/api/auth/switch-role' : '/api/auth/dev-token'}`,
      method: 'POST',
      data: { openid },
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      timeout: 8000,
      success(res) {
        const data = res.data
        const statusCode = res.statusCode || 200
        if (statusCode >= 200 && statusCode < 300 && data && data.token) {
          wx.setStorageSync('token', data.token)
          console.log('[角色切换] 后端同步成功')
        }
      },
      fail(err) {
        console.warn('[角色切换] 后端同步跳过（不可用）')
      },
    })
  },
})
