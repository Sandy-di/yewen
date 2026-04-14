// pages/mine/role-switch/role-switch.js
// 测试模式：通过切换 openid 真正切换到不同身份的用户

const CLOUD_RUN_CONFIG = {
  env: 'prod-1g48e3i7b1f173d5',
  serviceName: 'yejian-api',
}

const TEST_USERS = [
  { openid: 'oDev_Owner_001', label: '业主', icon: '🏠', desc: '张先生 — 查看投票、参与投票、发起报修、查看公示', role: 'owner' },
  { openid: 'oDev_Property_001', label: '物业工作人员', icon: '🔧', desc: '物业服务中心 — 接收工单、更新工单状态、上报财务报表', role: 'property' },
  { openid: 'oDev_Committee_001', label: '业委会成员', icon: '📋', desc: '张主任 — 业主全部功能 + 发起投票、审批财务、发布公告', role: 'committee' },
]

Page({
  data: {
    currentOpenid: '',
    currentRole: '',
    testUsers: TEST_USERS,
    isTestMode: false,
    switching: false,
  },

  onLoad() {
    const app = getApp()
    const userInfo = app.globalData.userInfo
    const isTestMode = userInfo && userInfo.openid && userInfo.openid.startsWith('oDev_')
    this.setData({
      currentOpenid: userInfo?.openid || '',
      currentRole: app.globalData.currentRole || '',
      isTestMode,
    })
  },

  async onSwitchUser(e) {
    const { openid, label } = e.currentTarget.dataset
    if (openid === this.data.currentOpenid) return
    if (this.data.switching) return

    this.setData({ switching: true })

    try {
      const res = await new Promise((resolve, reject) => {
        wx.cloud.callContainer({
          config: { env: CLOUD_RUN_CONFIG.env },
          path: '/api/auth/switch-role',
          method: 'POST',
          data: { openid },
          header: {
            'Content-Type': 'application/json',
            'X-WX-SERVICE': CLOUD_RUN_CONFIG.serviceName,
          },
          timeout: 10000,
          success(res) {
            const data = res.data
            const statusCode = res.statusCode || (data && data.statusCode) || 200
            if (statusCode >= 200 && statusCode < 300) {
              resolve(data)
            } else {
              reject(new Error((data && data.detail) || '切换失败'))
            }
          },
          fail(err) {
            reject(new Error(err.errMsg || '网络错误'))
          },
        })
      })

      // 保存新 token
      wx.setStorageSync('token', res.token)

      // 刷新用户信息
      const app = getApp()
      await new Promise((resolve) => {
        app.refreshProfileCallback = () => {
          delete app.refreshProfileCallback
          resolve()
        }
        app.refreshProfile()
        // 超时保护
        setTimeout(resolve, 3000)
      })

      const userInfo = app.globalData.userInfo
      this.setData({
        currentOpenid: userInfo?.openid || openid,
        currentRole: app.globalData.currentRole,
        switching: false,
      })

      wx.showToast({ title: `已切换为${label}`, icon: 'success' })
    } catch (err) {
      console.error('身份切换失败', err)
      wx.showToast({ title: err.message || '切换失败', icon: 'none' })
      this.setData({ switching: false })
    }
  },

  // 使用 dev-token 登录（首次进入测试模式）
  async onDevLogin(e) {
    const { openid, label } = e.currentTarget.dataset
    if (this.data.switching) return

    this.setData({ switching: true })

    try {
      const res = await new Promise((resolve, reject) => {
        wx.cloud.callContainer({
          config: { env: CLOUD_RUN_CONFIG.env },
          path: '/api/auth/dev-token',
          method: 'POST',
          data: { openid },
          header: {
            'Content-Type': 'application/json',
            'X-WX-SERVICE': CLOUD_RUN_CONFIG.serviceName,
          },
          timeout: 10000,
          success(res) {
            const data = res.data
            const statusCode = res.statusCode || (data && data.statusCode) || 200
            if (statusCode >= 200 && statusCode < 300) {
              resolve(data)
            } else {
              reject(new Error((data && data.detail) || '登录失败'))
            }
          },
          fail(err) {
            reject(new Error(err.errMsg || '网络错误'))
          },
        })
      })

      wx.setStorageSync('token', res.token)

      const app = getApp()
      await new Promise((resolve) => {
        app.refreshProfileCallback = () => {
          delete app.refreshProfileCallback
          resolve()
        }
        app.refreshProfile()
        setTimeout(resolve, 3000)
      })

      const userInfo = app.globalData.userInfo
      this.setData({
        currentOpenid: userInfo?.openid || openid,
        currentRole: app.globalData.currentRole,
        isTestMode: true,
        switching: false,
      })

      wx.showToast({ title: `已登录为${label}`, icon: 'success' })
    } catch (err) {
      console.error('测试登录失败', err)
      wx.showToast({ title: err.message || '登录失败', icon: 'none' })
      this.setData({ switching: false })
    }
  },
})
