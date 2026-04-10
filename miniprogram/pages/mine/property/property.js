// pages/mine/property/property.js
Page({
  data: {
    properties: [],
    showAddForm: false,
    form: { building: '', unit: '', roomNo: '', area: '' }
  },

  onLoad() {
    const app = getApp()
    const properties = app.globalData.userInfo?.properties || []
    this.setData({ properties })
  },

  onAddProperty() {
    this.setData({ showAddForm: true })
  },

  onFormInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },

  onSubmitProperty() {
    const { form } = this.data
    if (!form.building || !form.unit || !form.roomNo || !form.area) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }
    const newProp = {
      propertyId: 'P' + Date.now(),
      building: form.building,
      unit: form.unit,
      roomNo: form.roomNo,
      usableArea: Number(form.area),
      isDefault: this.data.properties.length === 0
    }
    const properties = [...this.data.properties, newProp]
    this.setData({ properties, showAddForm: false, form: { building: '', unit: '', roomNo: '', area: '' } })
    
    // 更新全局
    const app = getApp()
    if (app.globalData.userInfo) {
      app.globalData.userInfo.properties = properties
      wx.setStorageSync('userInfo', app.globalData.userInfo)
    }
    wx.showToast({ title: '添加成功', icon: 'success' })
  },

  onSetDefault(e) {
    const idx = e.currentTarget.dataset.idx
    const properties = this.data.properties.map((p, i) => ({
      ...p,
      isDefault: i === idx
    }))
    this.setData({ properties })
    const app = getApp()
    if (app.globalData.userInfo) {
      app.globalData.userInfo.properties = properties
      wx.setStorageSync('userInfo', app.globalData.userInfo)
    }
  },

  onCloseForm() {
    this.setData({ showAddForm: false })
  }
})
