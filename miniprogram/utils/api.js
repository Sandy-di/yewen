/**
 * api.js — 后端 API 客户端
 * 与 mock-data.js 保持一致的接口签名。
 * 支持分页（page/pageSize）和新接口（上传、社区、统计）。
 * 正式环境使用 wx.cloud.callContainer 调用云托管服务。
 */

const { mockApi } = require('./mock-data.js')

// 云托管配置
const CLOUD_RUN_CONFIG = {
  env: 'prod-1g48e3i7b1f173d5',   // 云托管环境 ID
  serviceName: 'yejian-api-001',   // 服务名称
}

const FORCE_MOCK = !!wx.getStorageSync('forceMockApi')
const USE_MOCK = FORCE_MOCK

let hasWarnedMockFallback = false

function warnMockFallback(reason) {
  if (hasWarnedMockFallback) return
  hasWarnedMockFallback = true
  console.warn('API 已回退到本地 mock 数据：' + reason)
}

function shouldFallbackToMock(error) {
  const message = String((error && error.message) || error || '')
  return /url not in domain list|request:fail|network|timeout|fail/i.test(message)
}

async function callWithFallback(methodName, realCall, args = []) {
  if (USE_MOCK) {
    warnMockFallback('已开启 forceMockApi。')
    return mockApi[methodName](...args)
  }

  try {
    return await realCall()
  } catch (error) {
    if (mockApi[methodName] && shouldFallbackToMock(error)) {
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

// 封装 wx.cloud.callContainer 为 Promise（正式环境）
// 注意：callContainer 的 path 不支持查询字符串，GET 请求参数需通过 data 传递
function request(url, options = {}) {
  // 分离 path 和 query string（兼容旧写法）
  let path = url
  let queryData = options.data || {}
  const qIndex = url.indexOf('?')
  if (qIndex !== -1) {
    path = url.substring(0, qIndex)
    const queryString = url.substring(qIndex + 1)
    // 解析查询字符串到 queryData
    for (const pair of queryString.split('&')) {
      const [key, value] = pair.split('=')
      if (key) {
        queryData[decodeURIComponent(key)] = decodeURIComponent(value || '')
      }
    }
  }

  // GET 请求把参数放 data；POST 请求 data 作为请求体
  const method = (options.method || 'GET').toUpperCase()
  const isGet = method === 'GET'

  return new Promise((resolve, reject) => {
    wx.cloud.callContainer({
      config: { env: CLOUD_RUN_CONFIG.env },
      path: path,
      method: method,
      data: isGet ? queryData : (options.data || {}),
      header: { ...getHeaders(), ...options.header },
      serviceName: CLOUD_RUN_CONFIG.serviceName,
      timeout: options.timeout || 15000,
      success(res) {
        const data = res.data
        const statusCode = res.statusCode || (data && data.statusCode) || 200
        if (statusCode === 401) {
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

  // ---------- 文件上传（新增） ----------
  async uploadFile(filePath) {
    if (USE_MOCK) {
      warnMockFallback('文件上传使用模拟模式')
      return { success: true, url: '/uploads/mock-image.jpg', filename: 'mock-image.jpg' }
    }
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('token')
      wx.cloud.callContainer({
        config: { env: CLOUD_RUN_CONFIG.env },
        serviceName: CLOUD_RUN_CONFIG.serviceName,
        path: '/api/upload',
        method: 'POST',
        filePath: filePath,
        name: 'file',
        header: { 'Authorization': token ? `Bearer ${token}` : '' },
        success(res) {
          const data = res.data
          const statusCode = res.statusCode || (data && data.statusCode) || 200
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

  // ---------- 社区管理（新增） ----------
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

  // ---------- 数据统计（新增） ----------
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

  // ---------- 用户管理（管理端） ----------
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

  // ---------- 角色变更记录（公示） ----------
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
