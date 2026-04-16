// app.js

const { API_BASE_URL } = require('./utils/config')

App({
  onLaunch() {
    // 检查登录状态
    this.checkLoginStatus()
    // 获取系统信息
    this.getSystemInfo()
  },

  globalData: {
    userInfo: null,
    currentRole: 'owner', // owner | property | committee
    communityInfo: null,
    systemInfo: null,
    useMock: false
  },

  isMockToken(token) {
    return typeof token === 'string' && token.indexOf('mock_token_') === 0
  },

  // 检查登录状态
  checkLoginStatus() {
    if (this.globalData.useMock) {
      this.mockLogin()
      return
    }
    const token = wx.getStorageSync('token')
    if (!token) {
      this.doLogin()
    } else {
      // 有 token，恢复用户信息
      const userInfo = wx.getStorageSync('userInfo')
      if (userInfo) {
        this.globalData.userInfo = userInfo
        this.globalData.currentRole = userInfo.role
      }
      // 后台静默刷新用户信息
      this.refreshProfile()
    }
  },

  // 微信登录
  doLogin() {
    wx.login({
      success: (res) => {
        if (res.code) {
          this.loginWithCode(res.code)
        }
      },
      fail: () => {
        console.warn('wx.login 失败，使用模拟登录')
        this.mockLogin()
      }
    })
  },

  // 用 code 换取后端 token
  loginWithCode(code) {
    wx.request({
      url: `${API_BASE_URL}/api/auth/login`,
      method: 'POST',
      data: { code },
      header: { 'Content-Type': 'application/json' },
      timeout: 15000,
      success: (res) => {
        const data = res.data
        const statusCode = res.statusCode || 200
        if (statusCode === 200 && data.token) {
          wx.setStorageSync('token', data.token)
          this.refreshProfile()
        } else {
          console.warn('后端登录返回异常，使用模拟登录')
          this.mockLogin()
        }
      },
      fail: () => {
        console.warn('后端登录失败，使用模拟登录')
        this.mockLogin()
      }
    })
  },

  // 从后端刷新用户信息
  refreshProfile() {
    const token = wx.getStorageSync('token')
    if (!token) return
    if (this.globalData.useMock || this.isMockToken(token)) {
      return
    }

    wx.request({
      url: `${API_BASE_URL}/api/auth/profile`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      timeout: 10000,
      success: (res) => {
        const data = res.data
        const statusCode = res.statusCode || 200
        if (statusCode === 200 && data) {
          const profile = data
          const userInfo = {
            userId: profile.userId,
            openid: profile.openid,
            nickname: profile.nickname,
            phone: profile.phone,
            avatar: profile.avatar,
            role: profile.role,
            verifiedLevel: profile.verifiedLevel,
            communityId: profile.communityId,
            communityName: profile.communityName,
            communityAddress: profile.communityAddress,
            identities: profile.identities || { isOwner: profile.role === 'owner' || profile.role === 'committee', isProperty: profile.role === 'property', isCommittee: profile.role === 'committee' },
            properties: profile.properties || []
          }
          this.globalData.userInfo = userInfo
          this.globalData.currentRole = userInfo.role
          this.globalData.communityInfo = profile.communityName
            ? { name: profile.communityName, id: profile.communityId, address: profile.communityAddress }
            : null
          wx.setStorageSync('userInfo', userInfo)
        }
        if (typeof this.refreshProfileCallback === 'function') {
          this.refreshProfileCallback()
        }
      },
    })
  },

  // 模拟登录（开发/离线模式）
  mockLogin() {
    const mockUser = {
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
        {
          propertyId: 'P20260410001',
          building: '3栋',
          unit: '1单元',
          roomNo: '502',
          usableArea: 89.5,
          isDefault: true
        }
      ]
    }
    this.globalData.userInfo = mockUser
    this.globalData.currentRole = mockUser.role
    this.globalData.communityInfo = mockUser.communityName
      ? { name: mockUser.communityName, id: mockUser.communityId, address: mockUser.communityAddress }
      : null
    wx.setStorageSync('userInfo', mockUser)
    wx.setStorageSync('token', 'mock_token_xxx')
  },

  // 获取系统信息
  getSystemInfo() {
    try {
      const winInfo = wx.getWindowInfo()
      const sysInfo = wx.getSystemSetting()
      this.globalData.systemInfo = {
        model: winInfo.model,
        pixelRatio: winInfo.pixelRatio,
        windowWidth: winInfo.windowWidth,
        windowHeight: winInfo.windowHeight,
        system: winInfo.system,
        platform: winInfo.platform,
        statusBarHeight: winInfo.statusBarHeight,
        navBarHeight: 44,
        albumAuthorized: sysInfo.albumAuthorized,
        cameraAuthorized: sysInfo.cameraAuthorized
      }
    } catch (e) {
      console.error('获取系统信息失败', e)
    }
  },

  // 切换角色
  switchRole(role) {
    const identities = this.globalData.userInfo?.identities || {}
    const allowedRoles = []
    if (identities.isOwner) allowedRoles.push('owner')
    if (identities.isProperty) allowedRoles.push('property')
    if (identities.isCommittee) allowedRoles.push('committee')

    if (!allowedRoles.includes(role)) {
      wx.showToast({ title: '无权切换到该角色', icon: 'none' })
      return false
    }

    this.globalData.currentRole = role
    if (this.globalData.userInfo) {
      this.globalData.userInfo.role = role
      wx.setStorageSync('userInfo', this.globalData.userInfo)
    }
    return true
  }
})
