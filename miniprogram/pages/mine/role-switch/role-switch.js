// pages/mine/role-switch/role-switch.js
const { ROLE_MAP } = require('../../../utils/util')

Page({
  data: {
    currentRole: 'owner',
    roles: [
      { key: 'owner', label: '业主', icon: '🏠', desc: '查看投票、参与投票、发起报修、查看公示', identityKey: 'isOwner' },
      { key: 'property', label: '物业工作人员', icon: '🔧', desc: '接收工单、更新工单状态、上报财务报表', identityKey: 'isProperty' },
      { key: 'committee', label: '业委会成员', icon: '📋', desc: '业主全部功能 + 发起投票、审批财务、发布公告', identityKey: 'isCommittee' }
    ]
  },

  onLoad() {
    const app = getApp()
    const identities = app.globalData.userInfo?.identities || {}
    // 根据后端返回的 identities 标记哪些角色可用
    const roles = this.data.roles.map(r => ({
      ...r,
      allowed: !!identities[r.identityKey]
    }))
    this.setData({ currentRole: app.globalData.currentRole, roles })
  },

  onRoleSelect(e) {
    const role = e.currentTarget.dataset.role
    if (role === this.data.currentRole) return

    const roleItem = this.data.roles.find(r => r.key === role)
    if (!roleItem || !roleItem.allowed) {
      wx.showToast({ title: '您没有该角色的权限', icon: 'none' })
      return
    }

    const app = getApp()
    const success = app.switchRole(role)
    if (success) {
      this.setData({ currentRole: role })
      wx.showToast({ 
        title: `已切换为${ROLE_MAP[role].label}视角`, 
        icon: 'success' 
      })
    }
  }
})
