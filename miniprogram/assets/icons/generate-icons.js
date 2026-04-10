// 图标生成脚本 - 运行此脚本生成TabBar所需的图标
// 使用方法：node generate-icons.js
// 生成后替换 assets/icons/ 下的占位文件

const fs = require('fs')
const path = require('path')

// 由于微信小程序tabBar不支持SVG，这里生成简单的说明文件
// 实际项目中需要使用设计好的PNG图标（81x81px推荐）

const iconsDir = path.join(__dirname)

const iconList = [
  'home.png', 'home-active.png',
  'repair.png', 'repair-active.png',
  'finance.png', 'finance-active.png',
  'mine.png', 'mine-active.png'
]

// 创建1x1透明PNG作为占位
const PNG_1x1 = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
  'base64'
)

// 创建81x81纯色PNG占位图标
// 实际项目中请替换为设计师提供的图标
iconList.forEach(name => {
  const filePath = path.join(iconsDir, name)
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, PNG_1x1)
    console.log(`Created placeholder: ${name}`)
  }
})

console.log('\n⚠️  注意：当前图标为1x1透明占位符，实际发布前请替换为81x81px的设计图标！')
console.log('图标要求：')
console.log('  - 格式：PNG')
console.log('  - 尺寸：81x81px（推荐）')
console.log('  - 未选中状态：灰色 #999999')
console.log('  - 选中状态：主题蓝 #0052D9')
