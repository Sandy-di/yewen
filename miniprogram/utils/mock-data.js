// utils/mock-data.js - 模拟数据

const mockVotes = [
  {
    voteId: 'V20260410001',
    title: '关于小区大门更换的投票',
    description: '现有小区东门及南门大门使用已超过10年，锈蚀严重且存在安全隐患。业委会提议使用公共维修基金更换为智能门禁系统，预算约28万元。请各位业主投票表决。',
    verificationLevel: 3,
    voteType: 'double_majority',
    status: 'active',
    startTime: '2026-04-05 08:00',
    endTime: '2026-04-15 18:00',
    totalProperties: 512,
    participatedCount: 234,
    participatedArea: 18920,
    totalArea: 45600,
    options: [
      { id: 'opt1', label: '同意更换', count: 189, area: 15230 },
      { id: 'opt2', label: '不同意', count: 35, area: 2890 },
      { id: 'opt3', label: '弃权', count: 10, area: 800 }
    ],
    createdBy: '张主任',
    createdAt: '2026-04-03 10:30',
    resultHash: null
  },
  {
    voteId: 'V20260410002',
    title: '关于绿化改造方案的投票',
    description: '为提升小区环境品质，拟对中心花园区域进行绿化升级改造，增加休闲座椅和儿童游乐设施。预算15万元。',
    verificationLevel: 2,
    voteType: 'double_majority',
    status: 'ended',
    startTime: '2026-03-20 08:00',
    endTime: '2026-03-30 18:00',
    totalProperties: 512,
    participatedCount: 389,
    participatedArea: 34200,
    totalArea: 45600,
    options: [
      { id: 'opt1', label: '同意改造', count: 356, area: 31200 },
      { id: 'opt2', label: '不同意', count: 25, area: 2200 },
      { id: 'opt3', label: '弃权', count: 8, area: 800 }
    ],
    createdBy: '李副主任',
    createdAt: '2026-03-18 14:00',
    resultHash: '0xabc123def456',
    result: 'passed',
    resultSummary: '参与户数76%（389/512），参与面积75%（34,200/45,600㎡）。同意户数92%（356/389），同意面积91%（31,200/34,200㎡）。达到双过半标准，投票通过。'
  },
  {
    voteId: 'V20260410003',
    title: '关于物业费调整的投票',
    description: '鉴于人力成本上涨及服务升级需求，拟将物业费从2.5元/㎡调整为3.0元/㎡，同时增加以下服务：24小时安保巡逻、公共区域WiFi覆盖、垃圾分类指导。',
    verificationLevel: 4,
    voteType: 'double_three_quarters',
    status: 'active',
    startTime: '2026-04-08 08:00',
    endTime: '2026-04-22 18:00',
    totalProperties: 512,
    participatedCount: 156,
    participatedArea: 12800,
    totalArea: 45600,
    options: [
      { id: 'opt1', label: '同意调整', count: 98, area: 8100 },
      { id: 'opt2', label: '不同意', count: 48, area: 3900 },
      { id: 'opt3', label: '弃权', count: 10, area: 800 }
    ],
    createdBy: '王委员',
    createdAt: '2026-04-06 09:00',
    resultHash: null
  }
]

const mockOrders = [
  {
    orderId: 'WR20260410001',
    category: 'access',
    subCategory: '门禁故障',
    description: '小区东门门禁系统故障，业主无法刷卡进出，已持续2天。门禁屏幕显示离线状态，刷卡无反应。',
    photos: [],
    status: 'processing',
    propertyId: 'P20260410001',
    propertyName: '3栋1单元502',
    contactPhone: '138****5678',
    createdAt: '2026-04-10 14:23',
    acceptedAt: '2026-04-10 14:30',
    acceptedBy: '张师傅',
    acceptorPhone: '139****1234',
    estimatedTime: '15:00',
    timeline: [
      { time: '14:23', content: '业主提交报修', type: 'submitted' },
      { time: '14:30', content: '物业已接单，张师傅预计15:00上门', type: 'accepted' },
      { time: '14:55', content: '开始维修，正在更换门禁控制模块', type: 'processing' }
    ],
    slaDeadline: '2026-04-11 14:23',
    slaLevel: 24 // hours
  },
  {
    orderId: 'WR20260408003',
    category: 'water_elec',
    subCategory: '漏水',
    description: '5栋地下车库入口处天花板漏水，雨水天气尤为严重，影响车辆通行。',
    photos: [],
    status: 'completed',
    propertyId: 'P20260410001',
    propertyName: '3栋1单元502',
    contactPhone: '138****5678',
    createdAt: '2026-04-08 09:15',
    acceptedAt: '2026-04-08 09:45',
    acceptedBy: '李师傅',
    acceptorPhone: '139****5678',
    completedAt: '2026-04-08 16:30',
    completionPhotos: [],
    completionNote: '已重新做防水处理并修补裂缝',
    rating: 5,
    ratingComment: '处理及时，效果不错',
    timeline: [
      { time: '09:15', content: '业主提交报修', type: 'submitted' },
      { time: '09:45', content: '李师傅已接单', type: 'accepted' },
      { time: '10:30', content: '开始维修', type: 'processing' },
      { time: '16:30', content: '维修完成，已重新做防水处理', type: 'completed' },
      { time: '17:00', content: '业主验收通过，评价5星', type: 'verified' }
    ],
    slaDeadline: '2026-04-09 09:15',
    slaLevel: 24
  },
  {
    orderId: 'WR20260407005',
    category: 'facility',
    subCategory: '电梯',
    description: '7栋2单元电梯运行时有异响，且偶尔出现停顿，存在安全隐患。',
    photos: [],
    status: 'pending_check',
    propertyId: 'P20260410001',
    propertyName: '3栋1单元502',
    contactPhone: '138****5678',
    createdAt: '2026-04-07 20:10',
    acceptedAt: '2026-04-07 20:30',
    acceptedBy: '王师傅',
    acceptorPhone: '139****9012',
    completedAt: '2026-04-08 11:00',
    completionPhotos: [],
    completionNote: '更换电梯钢丝绳和导轨滑块，已通过安全检测',
    timeline: [
      { time: '20:10', content: '业主提交报修', type: 'submitted' },
      { time: '20:30', content: '王师傅已接单，明早处理', type: 'accepted' },
      { time: '08:00', content: '开始维修，联系电梯维保公司', type: 'processing' },
      { time: '11:00', content: '维修完成，更换钢丝绳和导轨', type: 'completed' }
    ],
    slaDeadline: '2026-04-08 20:10',
    slaLevel: 24
  }
]

const mockFinanceRecords = [
  {
    reportId: 'F2026030001',
    month: '2026-03',
    title: '2026年3月物业收支报表',
    status: 'published',
    submittedBy: '陈会计',
    submittedAt: '2026-04-05 10:00',
    approvedBy: '张主任',
    approvedAt: '2026-04-06 09:00',
    totalIncome: 128560.00,
    totalExpense: 95230.50,
    balance: 33329.50,
    items: [
      { itemType: 'income', category: '物业费', amount: 102400.00, description: '3月物业费收缴' },
      { itemType: 'income', category: '停车费', amount: 18600.00, description: '地下车库停车费' },
      { itemType: 'income', category: '广告位收入', amount: 5600.00, description: '电梯广告位出租' },
      { itemType: 'income', category: '公共收益', amount: 1960.00, description: '快递柜场地费' },
      { itemType: 'expense', category: '人员工资', amount: 52000.00, description: '物业人员3月工资' },
      { itemType: 'expense', category: '维修费', amount: 12800.00, description: '电梯维保+门禁维修' },
      { itemType: 'expense', category: '绿化费', amount: 8600.50, description: '绿化养护+春季补种' },
      { itemType: 'expense', category: '水电费', amount: 12600.00, description: '公共区域水电费' },
      { itemType: 'expense', category: '保洁费', amount: 5230.00, description: '保洁服务费' },
      { itemType: 'expense', category: '办公费', amount: 4000.00, description: '办公用品+打印' }
    ]
  },
  {
    reportId: 'F2026020001',
    month: '2026-02',
    title: '2026年2月物业收支报表',
    status: 'published',
    submittedBy: '陈会计',
    submittedAt: '2026-03-05 10:00',
    approvedBy: '张主任',
    approvedAt: '2026-03-06 14:00',
    totalIncome: 115200.00,
    totalExpense: 88650.00,
    balance: 26550.00,
    items: [
      { itemType: 'income', category: '物业费', amount: 96000.00, description: '2月物业费收缴' },
      { itemType: 'income', category: '停车费', amount: 15200.00, description: '地下车库停车费' },
      { itemType: 'income', category: '广告位收入', amount: 4000.00, description: '电梯广告位出租' },
      { itemType: 'expense', category: '人员工资', amount: 52000.00, description: '物业人员2月工资' },
      { itemType: 'expense', category: '维修费', amount: 8500.00, description: '路灯维修+管道疏通' },
      { itemType: 'expense', category: '绿化费', amount: 3200.00, description: '冬季绿化维护' },
      { itemType: 'expense', category: '水电费', amount: 18500.00, description: '公共区域水电费(含春节照明)' },
      { itemType: 'expense', category: '保洁费', amount: 5450.00, description: '保洁服务费' },
      { itemType: 'expense', category: '办公费', amount: 1000.00, description: '办公用品' }
    ]
  },
  {
    reportId: 'F2026040001',
    month: '2026-04',
    title: '2026年4月物业收支报表',
    status: 'pending',
    submittedBy: '陈会计',
    submittedAt: '2026-04-10 16:00',
    approvedBy: null,
    approvedAt: null,
    totalIncome: 0,
    totalExpense: 0,
    balance: 0,
    items: []
  }
]

const mockAnnouncements = [
  {
    id: 'A20260410001',
    title: '关于小区大门更换投票的通知',
    content: '各位业主：\n\n根据《民法典》相关规定，现就小区大门更换事宜发起业主投票。投票时间为4月5日至4月15日，请各位业主积极参与。\n\n本次投票需完成L3身份核验后方可参与，请提前完成核验。\n\n详情请点击首页"投票"查看。',
    type: 'vote',
    publisher: '业委会',
    publisherName: '张主任',
    isTop: true,
    readCount: 356,
    totalUsers: 512,
    createdAt: '2026-04-04 09:00'
  },
  {
    id: 'A20260408002',
    title: '4月小区绿化养护安排通知',
    content: '各位业主：\n\n4月绿化养护工作安排如下：\n1. 4月12日-13日：中心花园春季补种\n2. 4月15日-16日：行道树修剪\n3. 4月20日：病虫害防治喷药\n\n喷药期间请注意关窗，照看好宠物和儿童。如有疑问请联系物业前台。',
    type: 'notice',
    publisher: '物业',
    publisherName: '物业服务中心',
    isTop: false,
    readCount: 289,
    totalUsers: 512,
    createdAt: '2026-04-08 10:00'
  },
  {
    id: 'A20260405003',
    title: '清明假期物业服务时间调整',
    content: '各位业主：\n\n清明假期（4月4日-6日）期间，物业服务中心营业时间调整为：9:00-17:00。\n\n24小时报修热线正常服务：400-XXX-XXXX\n\n祝大家假期愉快！',
    type: 'notice',
    publisher: '物业',
    publisherName: '物业服务中心',
    isTop: false,
    readCount: 412,
    totalUsers: 512,
    createdAt: '2026-04-03 15:00'
  },
  {
    id: 'A20260401004',
    title: '2026年第一季度财务公示',
    content: '各位业主：\n\n2026年第一季度（1-3月）物业财务报表已完成审批并公示。详细收支明细请查看"公示"页面。\n\n如有疑问，可联系业委会或物业前台。',
    type: 'finance',
    publisher: '业委会',
    publisherName: '李副主任',
    isTop: false,
    readCount: 198,
    totalUsers: 512,
    createdAt: '2026-04-01 10:00'
  }
]

// 模拟API延迟
function mockDelay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 模拟API
const mockComplaints = [
  {
    complaintId: 'CP20260410001',
    title: '楼道灯长期不亮',
    category: 'service',
    status: 'replied',
    isImportant: true,
    slaDeadline: '2026-04-14 10:00',
    createdAt: '2026-04-12 10:30',
    replyCount: 2,
    content: '3号楼2单元楼道灯已坏超过两周，夜间出行极不方便，存在安全隐患。',
    photos: [],
    replies: [
      { id: 'CR1', userId: 'U002', content: '已安排维修人员明日上门检查', replyType: 'reply', createdAt: '2026-04-12 14:20' },
      { id: 'CR2', userId: 'U003', content: '请物业本周内解决，业主安全是第一位的', replyType: 'supervise', createdAt: '2026-04-12 16:00' },
    ],
  },
  {
    complaintId: 'CP20260410002',
    title: '物业费收费不透明',
    category: 'fee',
    status: 'submitted',
    isImportant: false,
    slaDeadline: '2026-04-15 08:00',
    createdAt: '2026-04-13 08:00',
    replyCount: 0,
    content: '近期物业费调整未提前公示，账目不清，希望提供详细说明。',
    photos: [],
    replies: [],
  },
]

const mockApi = {
  // 获取投票列表
  async getVoteList(params = {}) {
    await mockDelay()
    let list = [...mockVotes]
    if (params.status && params.status !== 'all') {
      list = list.filter(v => v.status === params.status)
    }
    return { data: list, total: list.length, page: params.page || 1, pageSize: params.pageSize || 20 }
  },

  // 获取投票详情
  async getVoteDetail(voteId) {
    await mockDelay()
    const vote = mockVotes.find(v => v.voteId === voteId)
    return vote || null
  },

  // 提交投票
  async submitVote(voteId, optionId) {
    await mockDelay(800)
    return { success: true, txHash: '0x' + Math.random().toString(16).substr(2, 12) }
  },

  // 获取工单列表
  async getOrderList(params = {}) {
    await mockDelay()
    let list = [...mockOrders]
    if (params.status && params.status !== 'all') {
      list = list.filter(o => o.status === params.status)
    }
    return { data: list, total: list.length, page: params.page || 1, pageSize: params.pageSize || 20 }
  },

  // 获取工单详情
  async getOrderDetail(orderId) {
    await mockDelay()
    const order = mockOrders.find(o => o.orderId === orderId)
    return order || null
  },

  // 提交报修
  async submitRepair(data) {
    await mockDelay(800)
    return { success: true, orderId: 'WR' + Date.now() }
  },

  // 获取财务报表列表
  async getFinanceList(params = {}) {
    await mockDelay()
    return { data: mockFinanceRecords, total: mockFinanceRecords.length, page: params.page || 1, pageSize: params.pageSize || 20 }
  },

  // 获取财务报表详情
  async getFinanceDetail(reportId) {
    await mockDelay()
    const report = mockFinanceRecords.find(r => r.reportId === reportId)
    return report || null
  },

  // 获取公告列表
  async getAnnouncementList(params = {}) {
    await mockDelay()
    return { data: mockAnnouncements, total: mockAnnouncements.length, page: params.page || 1, pageSize: params.pageSize || 20 }
  },

  // 获取公告详情
  async getAnnouncementDetail(id) {
    await mockDelay()
    const announce = mockAnnouncements.find(a => a.id === id)
    return announce || null
  },

  // 身份核验
  async verifyIdentity(level, data) {
    await mockDelay(1500)
    return { success: true, verifiedLevel: level }
  },

  // 评价工单
  async rateOrder(orderId, rating, comment) {
    await mockDelay()
    return { success: true }
  },

  // 验收工单
  async acceptOrder(orderId) {
    await mockDelay()
    return { success: true }
  },

  // 申请复修
  async reworkOrder(orderId, reason) {
    await mockDelay()
    return { success: true }
  },

  // 发起投票
  async createVote(data) {
    await mockDelay(1000)
    return { success: true, voteId: 'V' + Date.now() }
  },

  // 文件上传
  async uploadFile(filePath) {
    await mockDelay()
    return { success: true, url: '/uploads/mock-image.jpg', filename: 'mock-image.jpg' }
  },

  // 社区列表
  async getCommunityList(params = {}) {
    await mockDelay()
    return {
      data: [],
      total: 0,
      page: 1,
      pageSize: 20
    }
  },

  // 社区详情
  async getCommunityDetail(communityId) {
    await mockDelay()
    return null
  },

  // 仪表盘统计
  async getDashboard() {
    await mockDelay()
    return {
      totalUsers: 456,
      totalVotes: 3,
      activeVotes: 2,
      totalOrders: 156,
      pendingOrders: 12,
      processingOrders: 8,
      totalFinance: 6,
      pendingFinance: 1,
      totalAnnouncements: 15
    }
  },

  // 社区概览
  async getOverview() {
    await mockDelay()
    return {
      communityName: '',
      totalUnits: 0,
      totalArea: 0,
      totalOwners: 0,
      recentOrders: 0,
      activeVotes: 0
    }
  },

  // 财务审批
  async approveFinance(reportId) {
    await mockDelay()
    return { success: true }
  },

  // 财务拒绝
  async rejectFinance(reportId, reason) {
    await mockDelay()
    return { success: true }
  },

  // 创建公告
  async createAnnouncement(data) {
    await mockDelay()
    return { success: true, id: 'A' + Date.now() }
  },

  // 编辑公告
  async updateAnnouncement(id, data) {
    await mockDelay()
    return { success: true }
  },

  // 删除公告
  async deleteAnnouncement(id) {
    await mockDelay()
    return { success: true }
  },

  // 完成工单
  async completeOrder(orderId, note, completionPhotos) {
    await mockDelay()
    return { success: true }
  },

  // 开始处理工单
  async processOrder(orderId) {
    await mockDelay()
    return { success: true }
  },

  // 用户列表
  async getUserList(params = {}) {
    await mockDelay()
    return {
      data: [
        { id: 'U001', nickname: '张业主', phone: '138****5678', role: 'owner', verifiedLevel: 3, communityId: 'C20260410001', isActive: true, createdAt: '2026-01-15' },
        { id: 'U002', nickname: '李物业', phone: '139****1234', role: 'property', verifiedLevel: 2, communityId: 'C20260410001', isActive: true, createdAt: '2026-02-20' },
        { id: 'U003', nickname: '王委员', phone: '137****9012', role: 'committee', verifiedLevel: 4, communityId: 'C20260410001', isActive: true, createdAt: '2026-01-10' }
      ],
      total: 3,
      page: 1,
      pageSize: 20
    }
  },

  // 修改用户角色
  async updateUserRole(userId, role) {
    await mockDelay()
    return { success: true }
  },

  // 启用/禁用用户
  async toggleUserActive(userId, isActive) {
    await mockDelay()
    return { success: true }
  },

  // 创建社区
  async createCommunity(data) {
    await mockDelay()
    return { success: true, id: 'C' + Date.now() }
  },

  // 更新社区
  async updateCommunity(communityId, data) {
    await mockDelay()
    return { success: true }
  },

  // 投诉列表
  async getComplaintList(params = {}) {
    await mockDelay()
    let list = [...mockComplaints]
    if (params.status && params.status !== 'all') {
      list = list.filter(c => c.status === params.status)
    }
    return { data: list, total: list.length, page: params.page || 1, pageSize: params.pageSize || 20 }
  },

  // 投诉详情
  async getComplaintDetail(complaintId) {
    await mockDelay()
    const complaint = mockComplaints.find(c => c.complaintId === complaintId)
    return complaint || null
  },

  // 创建投诉
  async createComplaint(data) {
    await mockDelay(800)
    return { success: true, complaintId: 'CP' + Date.now() }
  },

  // 回复投诉
  async replyComplaint(complaintId, content, replyType) {
    await mockDelay()
    return { success: true }
  },

  // 标记投诉重要
  async markComplaintImportant(complaintId, isImportant) {
    await mockDelay()
    return { success: true }
  },

  // 关闭投诉
  async closeComplaint(complaintId) {
    await mockDelay()
    return { success: true }
  },
}

module.exports = {
  mockVotes,
  mockOrders,
  mockFinanceRecords,
  mockAnnouncements,
  mockComplaints,
  mockApi
}
