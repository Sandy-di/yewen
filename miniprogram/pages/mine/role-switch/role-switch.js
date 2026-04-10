// pages/mine/role-switch/role-switch.js
const { ROLE_MAP } = require('../../../utils/util')

Page({
  data: {
    currentRole: 'owner',
    roles: [
      { key: 'owner', label: '业主', icon: '🏠', desc: '查看投票、参与投票、发起报修、查看公示' },
      { key: 'property', label: '物业工作人员', icon: '🔧', desc: '接收工单、更新工单状态、上报财务报表' },
      { key: 'committee', label: '业委会成员', icon: '📋', desc: '发起投票、审批财务、查看所有数据、发布公告' }
    ]
  },

  onLoad() {
    const app = getApp()
    this.setData({ currentRole: app.globalData.currentRole })
  },

  onRoleSelect(e) {
    const role = e.currentTarget.dataset.role
    if (role === this.data.currentRole) return

    const app = getApp()
    app.switchRole(role)
    this.setData({ currentRole: role })
    
    wx.showToast({ 
      title: `已切换为${ROLE_MAP[role].label}视角`, 
      icon: 'success' 
    })
  }
})
