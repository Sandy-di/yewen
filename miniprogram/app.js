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
    apiBaseUrl: 'https://api.example.com'
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (!token) {
      // 模拟登录 - 实际项目中需要调用wx.login
      this.mockLogin()
    }
  },

  // 模拟登录
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
