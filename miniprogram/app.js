// app.js
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
    communityInfo: {
      name: '翠湖花园',
      totalUnits: 512,
      address: '杭州市西湖区翠湖路88号'
    },
    systemInfo: null,
    apiBaseUrl: 'https://api.example.com',  // 替换为实际后端地址
    useMock: false  // 设为 true 使用模拟数据，false 使用真实后端
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
    const baseUrl = this.globalData.apiBaseUrl
    wx.request({
      url: `${baseUrl}/api/auth/login`,
      method: 'POST',
      data: { code },
      success: (res) => {
        if (res.statusCode === 200 && res.data.token) {
          const { token, user_id, role, nickname } = res.data
          wx.setStorageSync('token', token)
          
          // 登录后拉取完整用户信息
          this.refreshProfile()
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
    const baseUrl = this.globalData.apiBaseUrl
    const token = wx.getStorageSync('token')
    if (!token) return

    wx.request({
      url: `${baseUrl}/api/auth/profile`,
      method: 'GET',
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          const profile = res.data
          const userInfo = {
            userId: profile.userId,
            openid: profile.openid,
            nickname: profile.nickname,
            phone: profile.phone,
            avatar: profile.avatar,
            role: profile.role,
            verifiedLevel: profile.verifiedLevel,
            properties: profile.properties || []
          }
          this.globalData.userInfo = userInfo
          this.globalData.currentRole = userInfo.role
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
    this.globalData.currentRole = role
    if (this.globalData.userInfo) {
      this.globalData.userInfo.role = role
      wx.setStorageSync('userInfo', this.globalData.userInfo)
    }
  }
})
