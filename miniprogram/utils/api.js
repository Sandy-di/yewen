/**
 * api.js — 后端 API 客户端
 * 使用 wx.request 发送 HTTP 请求，不再依赖微信云托管。
 * 与 mock-data.js 保持一致的接口签名。
 */

const { API_BASE_URL } = require('./config.js')
const { mockApi } = require('./mock-data.js')

const FORCE_MOCK = !!wx.getStorageSync('forceMockApi')
const USE_MOCK = FORCE_MOCK

// 后端可用性标记：一旦检测到后端不可用，后续请求直接走 mock，避免重复等待超时
let backendUnavailable = false

let hasWarnedMockFallback = false

function warnMockFallback(reason) {
  if (hasWarnedMockFallback) return
  hasWarnedMockFallback = true
  console.warn('API 已回退到本地 mock 数据：' + reason)
}

function isMockToken() {
  const token = wx.getStorageSync('token')
  return typeof token === 'string' && token.indexOf('mock_token_') === 0
}

function shouldUseMock() {
  return USE_MOCK || isMockToken() || backendUnavailable
}

function shouldFallbackToMock(error) {
  const message = String((error && error.message) || error || '')
  return /url not in domain list|request:fail|network|timeout|fail|401|403|认证|登录已过期/i.test(message)
}

async function callWithFallback(methodName, realCall, args = []) {
  if (shouldUseMock()) {
    if (USE_MOCK) warnMockFallback('已开启 forceMockApi。')
    else if (isMockToken()) warnMockFallback('当前为测试模式（mock token）。')
    else warnMockFallback('后端不可用，已自动切换到 mock 数据。')
    return mockApi[methodName](...args)
  }

  try {
    const result = await realCall()
    backendUnavailable = false
    return result
  } catch (error) {
    if (mockApi[methodName] && shouldFallbackToMock(error)) {
      backendUnavailable = true
      warnMockFallback((error && error.message) || '请求失败')
      return mockApi[methodName](...args)
    }
    throw error
  }
}

// 获取请求头（带 token）
function getHeaders() {
  const token = wx.getStorageSync('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  }
}

/**
 * 封装 wx.request 为 Promise
 * @param {string} path - 请求路径，如 '/api/votes'
 * @param {object} options - 请求选项
 */
function request(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const url = `${API_BASE_URL}${path}`

  const header = { ...getHeaders(), ...options.header }

  // GET 请求不带 Content-Type（避免某些服务器把 data 当请求体）
  if (method === 'GET') {
    delete header['Content-Type']
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url,
      method,
      data: options.data || {},
      header,
      timeout: options.timeout || 15000,
      dataType: 'json',
      success(res) {
        console.log(`[request] ${method} ${path}`, res.statusCode, res.data)
        const data = res.data
        const statusCode = res.statusCode || 200

        if (statusCode === 401) {
          // mock token 不触发重新登录，直接走 mock 降级
          if (isMockToken()) {
            reject(new Error('登录已过期'))
            return
          }
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          const app = getApp()
          if (app && app.doLogin) {
            app.doLogin()
          }
          reject(new Error('登录已过期，请重新登录'))
          return
        }

        if (statusCode >= 200 && statusCode < 300) {
          resolve(data)
        } else {
          const msg = (data && data.detail) || '请求失败'
          reject(new Error(msg))
        }
      },
      fail(err) {
        console.error(`[request] ${method} ${path} FAIL`, err)
        reject(new Error(err.errMsg || '网络错误'))
      },
    })
  })
}

const api = {
  // ---------- 投票 ----------
  async getVoteList(params = {}) {
    return callWithFallback('getVoteList', () => {
      return request('/api/votes', {
        data: {
          status: params.status && params.status !== 'all' ? params.status : undefined,
          keyword: params.keyword || undefined,
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async getVoteDetail(voteId) {
    try {
      return await callWithFallback('getVoteDetail', () => request(`/api/votes/${voteId}`), [voteId])
    } catch {
      return null
    }
  },

  async submitVote(voteId, optionId) {
    return callWithFallback('submitVote', async () => {
      const res = await request(`/api/votes/${voteId}/submit`, {
        method: 'POST',
        data: { optionId },
      })
      return { success: true, txHash: res.txHash || '' }
    }, [voteId, optionId])
  },

  async createVote(data) {
    return callWithFallback('createVote', async () => {
      const res = await request('/api/votes', {
        method: 'POST',
        data,
      })
      return { success: true, voteId: res.voteId }
    }, [data])
  },

  // ---------- 报修工单 ----------
  async getOrderList(params = {}) {
    return callWithFallback('getOrderList', () => {
      return request('/api/orders', {
        data: {
          status: params.status && params.status !== 'all' ? params.status : undefined,
          category: params.category || undefined,
          keyword: params.keyword || undefined,
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async getOrderDetail(orderId) {
    try {
      return await callWithFallback('getOrderDetail', () => request(`/api/orders/${orderId}`), [orderId])
    } catch {
      return null
    }
  },

  async submitRepair(data) {
    return callWithFallback('submitRepair', async () => {
      const res = await request('/api/orders', {
        method: 'POST',
        data,
      })
      return { success: true, orderId: res.orderId }
    }, [data])
  },

  async rateOrder(orderId, rating, comment) {
    return callWithFallback('rateOrder', async () => {
      await request(`/api/orders/${orderId}/rate`, {
        method: 'POST',
        data: { rating, comment },
      })
      return { success: true }
    }, [orderId, rating, comment])
  },

  async acceptOrder(orderId) {
    return callWithFallback('acceptOrder', async () => {
      await request(`/api/orders/${orderId}/accept`, {
        method: 'POST',
      })
      return { success: true }
    }, [orderId])
  },

  async reworkOrder(orderId, reason) {
    return callWithFallback('reworkOrder', async () => {
      await request(`/api/orders/${orderId}/rework`, {
        method: 'POST',
        data: { reason },
      })
      return { success: true }
    }, [orderId, reason])
  },

  // ---------- 财务 ----------
  async getFinanceList(params = {}) {
    return callWithFallback('getFinanceList', () => {
      return request('/api/finance', {
        data: {
          status: params.status && params.status !== 'all' ? params.status : undefined,
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async getFinanceDetail(reportId) {
    try {
      return await callWithFallback('getFinanceDetail', () => request(`/api/finance/${reportId}`), [reportId])
    } catch {
      return null
    }
  },

  // ---------- 公告 ----------
  async getAnnouncementList(params = {}) {
    return callWithFallback('getAnnouncementList', () => {
      return request('/api/announcements', {
        data: {
          type: params.type && params.type !== 'all' ? params.type : undefined,
          keyword: params.keyword || undefined,
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async getAnnouncementDetail(id) {
    try {
      return await callWithFallback('getAnnouncementDetail', () => request(`/api/announcements/${id}`), [id])
    } catch {
      return null
    }
  },

  // ---------- 身份核验 ----------
  async verifyIdentity(level, data) {
    return callWithFallback('verifyIdentity', async () => {
      await request('/api/users/verify', {
        method: 'POST',
        data: { level, data },
      })
      return { success: true, verifiedLevel: level }
    }, [level, data])
  },

  // ---------- 文件上传 ----------
  async uploadFile(filePath) {
    if (USE_MOCK) {
      warnMockFallback('文件上传使用模拟模式')
      return { success: true, url: '/uploads/mock-image.jpg', filename: 'mock-image.jpg' }
    }
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('token')
      wx.uploadFile({
        url: `${API_BASE_URL}/api/upload`,
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
        success(res) {
          const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
          const statusCode = res.statusCode || 200
          if (statusCode >= 200 && statusCode < 300) {
            resolve({ success: true, url: data.url, filename: data.filename })
          } else {
            reject(new Error('上传失败'))
          }
        },
        fail(err) {
          reject(new Error(err.errMsg || '上传失败'))
        },
      })
    })
  },

  // ---------- 社区管理 ----------
  async getCommunityList(params = {}) {
    return callWithFallback('getCommunityList', () => {
      return request('/api/communities', {
        data: {
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async getCommunityDetail(communityId) {
    try {
      return await callWithFallback('getCommunityDetail', () => request(`/api/communities/${communityId}`), [communityId])
    } catch {
      return null
    }
  },

  // ---------- 数据统计 ----------
  async getDashboard() {
    return callWithFallback('getDashboard', () => request('/api/stats/dashboard'), [])
  },

  async getOverview() {
    return callWithFallback('getOverview', () => request('/api/stats/overview'), [])
  },

  // ---------- 财务审批 ----------
  async approveFinance(reportId) {
    return callWithFallback('approveFinance', async () => {
      await request(`/api/finance/${reportId}/approve`, { method: 'POST' })
      return { success: true }
    }, [reportId])
  },

  async rejectFinance(reportId, reason) {
    return callWithFallback('rejectFinance', async () => {
      await request(`/api/finance/${reportId}/reject`, {
        method: 'POST',
        data: { reason },
      })
      return { success: true }
    }, [reportId, reason])
  },

  // ---------- 公告管理 ----------
  async createAnnouncement(data) {
    return callWithFallback('createAnnouncement', async () => {
      const res = await request('/api/announcements', {
        method: 'POST',
        data,
      })
      return { success: true, id: res.id }
    }, [data])
  },

  async updateAnnouncement(id, data) {
    return callWithFallback('updateAnnouncement', async () => {
      await request(`/api/announcements/${id}`, {
        method: 'PUT',
        data,
      })
      return { success: true }
    }, [id, data])
  },

  async deleteAnnouncement(id) {
    return callWithFallback('deleteAnnouncement', async () => {
      await request(`/api/announcements/${id}`, {
        method: 'DELETE',
      })
      return { success: true }
    }, [id])
  },

  // ---------- 工单管理 ----------
  async completeOrder(orderId, note, completionPhotos) {
    return callWithFallback('completeOrder', async () => {
      await request(`/api/orders/${orderId}/complete`, {
        method: 'POST',
        data: { note, completionPhotos: completionPhotos || [] },
      })
      return { success: true }
    }, [orderId, note, completionPhotos])
  },

  async processOrder(orderId) {
    return callWithFallback('processOrder', async () => {
      await request(`/api/orders/${orderId}/process`, {
        method: 'POST',
      })
      return { success: true }
    }, [orderId])
  },

  // ---------- 用户管理 ----------
  async getUserList(params = {}) {
    return callWithFallback('getUserList', () => {
      return request('/api/users/list', {
        data: {
          role: params.role || undefined,
          keyword: params.keyword || undefined,
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async updateUserRole(userId, role, reason) {
    return callWithFallback('updateUserRole', async () => {
      await request(`/api/users/${userId}/role`, {
        method: 'PUT',
        data: { role, reason: reason || '' },
      })
      return { success: true }
    }, [userId, role, reason])
  },

  async toggleUserActive(userId, isActive) {
    return callWithFallback('toggleUserActive', async () => {
      await request(`/api/users/${userId}/active`, {
        method: 'PUT',
        data: { isActive },
      })
      return { success: true }
    }, [userId, isActive])
  },

  // ---------- 角色变更记录 ----------
  async getRoleLogs(params = {}) {
    return callWithFallback('getRoleLogs', () => {
      return request('/api/users/role-logs', {
        data: {
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async createFinanceReport(data) {
    return callWithFallback('createFinanceReport', async () => {
      const res = await request('/api/finance', {
        method: 'POST',
        data,
      })
      return { success: true, reportId: res.reportId }
    }, [data])
  },

  // ---------- 社区管理（补充） ----------
  async createCommunity(data) {
    return callWithFallback('createCommunity', async () => {
      const res = await request('/api/communities', {
        method: 'POST',
        data,
      })
      return { success: true, id: res.id }
    }, [data])
  },

  async updateCommunity(communityId, data) {
    return callWithFallback('updateCommunity', async () => {
      await request(`/api/communities/${communityId}`, {
        method: 'PUT',
        data,
      })
      return { success: true }
    }, [communityId, data])
  },

  // ---------- 投诉建议 ----------
  async getComplaintList(params = {}) {
    return callWithFallback('getComplaintList', () => {
      return request('/api/complaints', {
        data: {
          status: params.status && params.status !== 'all' ? params.status : undefined,
          category: params.category || undefined,
          keyword: params.keyword || undefined,
          page: params.page || 1,
          pageSize: params.pageSize || 20,
        }
      })
    }, [params])
  },

  async getComplaintDetail(complaintId) {
    try {
      return await callWithFallback('getComplaintDetail', () => request(`/api/complaints/${complaintId}`), [complaintId])
    } catch {
      return null
    }
  },

  async createComplaint(data) {
    return callWithFallback('createComplaint', async () => {
      const res = await request('/api/complaints', {
        method: 'POST',
        data,
      })
      return { success: true, complaintId: res.complaintId }
    }, [data])
  },

  async replyComplaint(complaintId, content, replyType) {
    return callWithFallback('replyComplaint', async () => {
      await request(`/api/complaints/${complaintId}/reply`, {
        method: 'POST',
        data: { content, replyType: replyType || 'reply' },
      })
      return { success: true }
    }, [complaintId, content, replyType])
  },

  async markComplaintImportant(complaintId, isImportant) {
    return callWithFallback('markComplaintImportant', async () => {
      await request(`/api/complaints/${complaintId}/important`, {
        method: 'PUT',
        data: { isImportant },
      })
      return { success: true }
    }, [complaintId, isImportant])
  },

  async closeComplaint(complaintId) {
    return callWithFallback('closeComplaint', async () => {
      await request(`/api/complaints/${complaintId}/close`, {
        method: 'POST',
      })
      return { success: true }
    }, [complaintId])
  },

  // ---------- 投票模板 ----------
  async getVoteTemplates() {
    return callWithFallback('getVoteTemplates', () => request('/api/vote-templates'), [])
  },
}

module.exports = api
