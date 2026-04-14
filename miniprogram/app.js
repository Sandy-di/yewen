// app.js

// 云托管配置
const CLOUD_RUN_CONFIG = {
  env: 'prod-1g48e3i7b1f173d5',
  serviceName: 'yejian-api-001',
}

App({
  onLaunch() {
    // 初始化云开发（callContainer 需要）
    if (wx.cloud) {
      wx.cloud.init({ env: CLOUD_RUN_CONFIG.env })
    }
    // 检查登录状态
    this.checkLoginStatus()
    // 获取系统信息
    this.getSystemInfo()
  },

  globalData: {
    userInfo: null,
    currentRole: 'owner', // owner | property | committee
    communityInfo: null,  // 从后端 profile 获取
    systemInfo: null,
    useMock: false  // 设为 true 使用模拟数据，false 使用真实后端
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
        // 登录失败，回退到模拟数据
        console.warn('wx.login 失败，使用模拟登录')
        this.mockLogin()
      }
    })
  },

  // 用 code 换取后端 token
  loginWithCode(code) {
    wx.cloud.callContainer({
      config: { env: CLOUD_RUN_CONFIG.env },
      serviceName: CLOUD_RUN_CONFIG.serviceName,
      path: '/api/auth/login',
      method: 'POST',
      data: { code },
      header: { 'Content-Type': 'application/json' },
      timeout: 15000,
      success: (res) => {
        const data = res.data
        const statusCode = res.statusCode || (data && data.statusCode) || 200
        if (statusCode === 200 && data.token) {
          const { token, user_id, role, nickname } = data
          wx.setStorageSync('token', token)
          
          // 登录后拉取完整用户信息
          this.refreshProfile()
        } else {
          console.warn('后端登录返回异常，使用模拟登录')
          this.mockLogin()
        }
      },
      fail: () => {
        // 网络失败，回退到模拟数据
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

    wx.cloud.callContainer({
      config: { env: CLOUD_RUN_CONFIG.env },
      serviceName: CLOUD_RUN_CONFIG.serviceName,
      path: '/api/auth/profile',
      method: 'GET',
      header: { 'Authorization': `Bearer ${token}` },
      timeout: 10000,
      success: (res) => {
        const data = res.data
        const statusCode = res.statusCode || (data && data.statusCode) || 200
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
            identities: profile.identities || { isOwner: profile.role === 'owner' || profile.role === 'committee', isProperty: profile.role === 'property', isCommittee: profile.role === 'committee' },
            properties: profile.properties || []
          }
          this.globalData.userInfo = userInfo
          this.globalData.currentRole = userInfo.role
          this.globalData.communityInfo = profile.communityName ? { name: profile.communityName, id: profile.communityId } : null
          wx.setStorageSync('userInfo', userInfo)
        }
      },
    })
  },

  // 模拟登录（开发/离线模式）
  mockLogin() {
    const mockUser = {
      userId: 'U20260410001',
      openid: 'oXXXXXXXXXXXXXXXX',
      nickname: '张先生',
      phone: '138****5678',
      avatar: '',
      role: 'owner',
      verifiedLevel: 2,
      communityId: null,
      communityName: null,
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
    this.globalData.communityInfo = null
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

  // 切换角色（需后端校验）
  switchRole(role) {
    // 角色切换需要后端校验，只允许切换到 identities 中标记为 true 的角色
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
