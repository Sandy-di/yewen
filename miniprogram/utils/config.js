/**
 * config.js — 全局配置
 * API_BASE_URL: 后端服务地址，部署后替换为你的 HTTPS 域名
 * 
 * 使用方式：
 *   开发环境：设为 http://localhost:8000（需开启本地调试）
 *   生产环境：设为 https://your-domain.com
 * 
 * 注意：小程序要求正式环境必须使用 HTTPS 域名，
 *       并在微信后台「开发管理→开发设置→服务器域名」中添加 request 合法域名
 */

const ENV = 'prod'  // 'dev' | 'prod'

const CONFIG = {
  dev: {
    API_BASE_URL: 'http://localhost:8000',   // 本地开发
  },
  prod: {
    API_BASE_URL: 'https://abc.chinawhw.cn',
  },
}

function getConfig() {
  return CONFIG[ENV] || CONFIG.dev
}

module.exports = {
  getConfig,
  ENV,
  // 方便直接引用
  get API_BASE_URL() { return getConfig().API_BASE_URL },
}
