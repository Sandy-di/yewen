/**
 * api.js — 业问后端 API 客户端
 * 替换 mock-data.js，保持接口签名完全一致
 */

const app = getApp()

// API 基础地址
const BASE_URL = 'https://api.example.com'  // 替换为实际后端地址

// 是否使用模拟数据（开发时可切换）
const USE_MOCK = false

// 获取请求头（带 token）
function getHeaders() {
  const token = wx.getStorageSync('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  }
}

// 封装 wx.request 为 Promise
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: { ...getHeaders(), ...options.header },
      success(res) {
        if (res.statusCode === 401) {
          // token 过期，重新登录
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          const app = getApp()
          if (app && app.doLogin) {
            app.doLogin()
          }
          reject(new Error('登录已过期，请重新登录'))
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const msg = (res.data && res.data.detail) || '请求失败'
          reject(new Error(msg))
        }
      },
      fail(err) {
        reject(new Error(err.errMsg || '网络错误'))
      },
    })
  })
}

// ============================================================
// API 接口 — 与 mockApi 签名完全一致
// ============================================================

const api = {
  // ---------- 投票 ----------
  async getVoteList(params = {}) {
    const query = params.status && params.status !== 'all' ? `?status=${params.status}` : ''
    return request(`/api/votes${query}`)
  },

  async getVoteDetail(voteId) {
    try {
      return await request(`/api/votes/${voteId}`)
    } catch {
      return null
    }
  },

  async submitVote(voteId, optionId) {
    const res = await request(`/api/votes/${voteId}/submit`, {
      method: 'POST',
      data: { optionId },
    })
    return { success: true, txHash: res.txHash || '' }
  },

  async createVote(data) {
    const res = await request('/api/votes', {
      method: 'POST',
      data,
    })
    return { success: true, voteId: res.voteId }
  },

  // ---------- 报修工单 ----------
  async getOrderList(params = {}) {
    const query = params.status && params.status !== 'all' ? `?status=${params.status}` : ''
    return request(`/api/orders${query}`)
  },

  async getOrderDetail(orderId) {
    try {
      return await request(`/api/orders/${orderId}`)
    } catch {
      return null
    }
  },

  async submitRepair(data) {
    const res = await request('/api/orders', {
      method: 'POST',
      data,
    })
    return { success: true, orderId: res.orderId }
  },

  async rateOrder(orderId, rating, comment) {
    await request(`/api/orders/${orderId}/rate`, {
      method: 'POST',
      data: { rating, comment },
    })
    return { success: true }
  },

  async acceptOrder(orderId) {
    await request(`/api/orders/${orderId}/accept`, {
      method: 'POST',
    })
    return { success: true }
  },

  async reworkOrder(orderId, reason) {
    await request(`/api/orders/${orderId}/rework`, {
      method: 'POST',
      data: { reason },
    })
    return { success: true }
  },

  // ---------- 财务 ----------
  async getFinanceList() {
    return request('/api/finance')
  },

  async getFinanceDetail(reportId) {
    try {
      return await request(`/api/finance/${reportId}`)
    } catch {
      return null
    }
  },

  // ---------- 公告 ----------
  async getAnnouncementList() {
    return request('/api/announcements')
  },

  async getAnnouncementDetail(id) {
    try {
      return await request(`/api/announcements/${id}`)
    } catch {
      return null
    }
  },

  // ---------- 身份核验 ----------
  async verifyIdentity(level, data) {
    await request('/api/users/verify', {
      method: 'POST',
      data: { level, data },
    })
    return { success: true, verifiedLevel: level }
  },
}

// 如果使用模拟数据，回退到 mockApi
if (USE_MOCK) {
  const { mockApi } = require('./mock-data.js')
  module.exports = mockApi
} else {
  module.exports = api
}
