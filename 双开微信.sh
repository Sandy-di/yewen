#!/bin/bash
# 双开微信脚本
# 如果微信已运行，再启动一个新实例；如果未运行，先启动再开第二个

WECHAT_PATH="/Applications/WeChat.app"

if pgrep -x WeChat > /dev/null; then
    echo "检测到微信已在运行，正在启动第二个实例..."
else
    echo "微信未运行，先启动第一个实例..."
    open "$WECHAT_PATH"
    sleep 3
fi

# 使用 -n 参数强制打开一个新的应用实例
open -n "$WECHAT_PATH"
echo "第二个微信已启动！请在弹出的窗口中登录你的第二个账号。"
