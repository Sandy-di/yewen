#!/bin/bash
# deploy.sh — 业问后端部署脚本
# 在你的 VPS 上运行此脚本，一键部署
#
# 前置条件：
#   1. 服务器已安装 Docker 和 Docker Compose
#   2. 域名 DNS 已解析到服务器 IP
#   3. 用 certbot 获取 SSL 证书
#
# 使用方法：
#   chmod +x deploy.sh
#   ./deploy.sh              # 首次部署
#   ./deploy.sh restart      # 重启服务
#   ./deploy.sh logs         # 查看日志
#   ./deploy.sh update       # 更新代码后重新部署

set -e

cd "$(dirname "$0")"

# ---------- 配置区 ----------
DOMAIN="${DOMAIN:-abc.chinawhw.cn}"
JWT_SECRET="${JWT_SECRET:-}"                 # 生产环境请设置强密钥
WX_APPID="${WX_APPID:-}"                     # 微信小程序 AppID
WX_SECRET="${WX_SECRET:-}"                   # 微信小程序 AppSecret
DB_PASSWORD="${DB_PASSWORD:-yewen_dev_2026}"  # 数据库密码（生产环境请修改）
# ----------------------------

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker 安装完成"
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

case "${1:-deploy}" in
  deploy)
    echo "🚀 开始部署业问后端..."

    # 创建 .env 文件
    cat > .env <<EOF
JWT_SECRET=${JWT_SECRET}
WX_APPID=${WX_APPID}
WX_SECRET=${WX_SECRET}
DB_PASSWORD=${DB_PASSWORD}
EOF

    # 更新 Nginx 配置中的域名
    if [ "$DOMAIN" != "abc.chinawhw.cn" ]; then
      sed -i.bak "s/your-domain.com/$DOMAIN/g" nginx/default.conf
      echo "✅ Nginx 域名已设置为: $DOMAIN"
    fi

    # 构建并启动
    docker compose up -d --build

    echo ""
    echo "✅ 部署完成！"
    echo "   API 地址: https://$DOMAIN/api/health"
    echo "   管理后台: https://$DOMAIN/admin/"
    echo ""
    echo "⚠️  后续步骤："
    echo "   1. 获取 SSL 证书: certbot certonly --standalone -d $DOMAIN"
    echo "   2. 修改 miniprogram/utils/config.js 中的 API_BASE_URL 为 https://$DOMAIN"
    echo "   3. 在微信后台添加服务器域名: $DOMAIN"
    echo "   4. 设置强 JWT_SECRET: export JWT_SECRET=你的密钥 && ./deploy.sh restart"
    ;;

  restart)
    docker compose restart
    echo "✅ 服务已重启"
    ;;

  logs)
    docker compose logs -f api
    ;;

  update)
    echo "🔄 更新部署..."
    git pull origin main 2>/dev/null || true
    docker compose up -d --build
    echo "✅ 更新完成"
    ;;

  stop)
    docker compose down
    echo "✅ 服务已停止"
    ;;

  ssl)
    if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
      echo "🔒 获取 SSL 证书..."
      apt-get update && apt-get install -y certbot
      certbot certonly --standalone -d "$DOMAIN"
      echo "✅ SSL 证书已获取"
    else
      echo "✅ SSL 证书已存在"
    fi
    echo "   证书路径: /etc/letsencrypt/live/$DOMAIN/"
    echo "   重启 Nginx 生效: docker compose restart nginx"
    ;;

  *)
    echo "用法: $0 {deploy|restart|logs|update|stop|ssl}"
    ;;
esac
