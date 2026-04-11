#!/bin/bash
# 业问后端启动脚本
# 使用方法: ./start.sh

cd "$(dirname "$0")"

# 检查 venv 是否存在
if [ ! -d "venv" ]; then
    echo "🔧 首次运行，创建虚拟环境..."
    PYTHON312=$(find /opt/homebrew -name "python3.12" -type f 2>/dev/null | head -1)
    if [ -z "$PYTHON312" ]; then
        echo "❌ 未找到 python3.12，请先运行: brew install python@3.12"
        exit 1
    fi
    $PYTHON312 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 初始化数据库（如果不存在）
if [ ! -f "yewen.db" ]; then
    echo "🌱 初始化种子数据..."
    python seed.py
fi

echo ""
echo "🚀 启动业问 API 服务..."
echo "   地址: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"
echo "   按 Ctrl+C 停止"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
