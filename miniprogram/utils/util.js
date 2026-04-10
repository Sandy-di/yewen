// utils/util.js - 通用工具函数

/**
 * 标准化日期字符串（iOS 不支持 "YYYY-MM-DD HH:mm" 空格格式）
 */
function normalizeDate(date) {
  if (!date || typeof date !== 'string') return date
  // 把空格替换为 T，使其符合 ISO 8601 格式
  return date.replace(' ', 'T')
}

/**
 * 格式化日期
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm') {
  if (!date) return ''
  const d = new Date(normalizeDate(date))
  const map = {
    'YYYY': d.getFullYear(),
    'MM': String(d.getMonth() + 1).padStart(2, '0'),
    'DD': String(d.getDate()).padStart(2, '0'),
    'HH': String(d.getHours()).padStart(2, '0'),
    'mm': String(d.getMinutes()).padStart(2, '0'),
    'ss': String(d.getSeconds()).padStart(2, '0')
  }
  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, matched => map[matched])
}

/**
 * 格式化金额
 */
function formatMoney(amount, prefix = '¥') {
  if (amount === null || amount === undefined) return '--'
  return prefix + Number(amount).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/**
 * 计算剩余时间
 */
function formatRemainTime(endTime) {
  const now = new Date().getTime()
  const end = new Date(normalizeDate(endTime)).getTime()
  const diff = end - now
  if (diff <= 0) return '已结束'
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  if (days > 0) return `剩余${days}天${hours}小时`
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  return `剩余${hours}小时${minutes}分钟`
}

/**
 * 投票状态映射
 */
const VOTE_STATUS_MAP = {
  draft: { label: '草稿', type: 'grey' },
  active: { label: '进行中', type: 'primary' },
  ended: { label: '已结束', type: 'grey' },
  archived: { label: '已归档', type: 'grey' }
}

/**
 * 工单状态映射
 */
const ORDER_STATUS_MAP = {
  submitted: { label: '已提交', type: 'warning', icon: '📋' },
  accepted: { label: '已接单', type: 'primary', icon: '✅' },
  processing: { label: '处理中', type: 'primary', icon: '🔧' },
  pending_check: { label: '待验收', type: 'warning', icon: '⏳' },
  completed: { label: '已完结', type: 'success', icon: '✅' },
  rework: { label: '待复修', type: 'error', icon: '🔄' }
}

/**
 * 核验等级映射
 */
const VERIFY_LEVEL_MAP = {
  1: { label: 'L1 手机核验', desc: '短信验证码验证', color: '#52C41A' },
  2: { label: 'L2 房产核验', desc: '手机号+房产信息匹配', color: '#1890FF' },
  3: { label: 'L3 双重核验', desc: '姓名+身份证+房产证', color: '#722ED1' },
  4: { label: 'L4 人脸核验', desc: '微信人脸核身', color: '#CF1322' }
}

/**
 * 报修类型映射
 */
const REPAIR_CATEGORIES = [
  { value: 'access', label: '门禁系统', icon: '🚪', children: ['门禁故障', '门锁损坏', '访客系统', '梯控'] },
  { value: 'facility', label: '公共设施', icon: '🏢', children: ['电梯', '照明', '消火栓', '公共座椅'] },
  { value: 'water_elec', label: '水电维修', icon: '💧', children: ['漏水', '排水', '电路故障'] },
  { value: 'green', label: '环境绿化', icon: '🌿', children: ['绿化破坏', '虫害', '灌溉系统'] },
  { value: 'other', label: '其他', icon: '📌', children: ['公共区域卫生', '噪音投诉'] }
]

/**
 * 角色映射
 */
const ROLE_MAP = {
  owner: { label: '业主', icon: '🏠' },
  property: { label: '物业', icon: '🔧' },
  committee: { label: '业委会', icon: '📋' }
}

/**
 * 显示Toast
 */
function showToast(title, icon = 'none', duration = 2000) {
  wx.showToast({ title, icon, duration })
}

/**
 * 显示Loading
 */
function showLoading(title = '加载中...') {
  wx.showLoading({ title, mask: true })
}

function hideLoading() {
  wx.hideLoading()
}

/**
 * 显示确认弹窗
 */
function showConfirm(content, title = '提示') {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      confirmColor: '#1890FF',
      success: (res) => resolve(res.confirm)
    })
  })
}

/**
 * 检查手机号格式
 */
function isValidPhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 防抖
 */
function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * 获取状态标签样式类
 */
function getTagClass(type) {
  const map = {
    primary: 'tag-primary',
    success: 'tag-success',
    warning: 'tag-warning',
    error: 'tag-error',
    grey: 'tag-grey'
  }
  return map[type] || 'tag-grey'
}

module.exports = {
  formatDate,
  formatMoney,
  formatRemainTime,
  VOTE_STATUS_MAP,
  ORDER_STATUS_MAP,
  VERIFY_LEVEL_MAP,
  REPAIR_CATEGORIES,
  ROLE_MAP,
  showToast,
  showLoading,
  hideLoading,
  showConfirm,
  isValidPhone,
  debounce,
  getTagClass
}
