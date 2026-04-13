# 业问后端 — 智慧社区业主微信小程序

FastAPI + SQLAlchemy 2.0 + PostgreSQL/SQLite

## 快速开始

### 方式一：一键启动（推荐）

```bash
cd server
./start.sh
```

脚本会自动创建 Python 3.12 虚拟环境、安装依赖、初始化种子数据、启动服务。

访问 http://localhost:8000/docs 查看 Swagger API 文档

### 方式二：手动启动

> ⚠️ 需要 Python 3.12+（Python 3.14 暂不兼容部分依赖）
> 
> 如未安装：`brew install python@3.12`

```bash
cd server

# 创建虚拟环境（首次）
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate

# 安装依赖 + 种子数据 + 启动
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

### 方式三：Docker Compose（PostgreSQL）

```bash
cd server
cp .env.example .env    # 修改微信 appid/secret 和 JWT_SECRET
docker-compose up -d
```

## 环境变量

复制 `.env.example` 为 `.env`，按需修改：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEBUG` | 调试模式 | `true` |
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./yewen.db` |
| `JWT_SECRET` | JWT签名密钥 | ⚠️ 生产环境必须修改 |
| `JWT_EXPIRE_HOURS` | Token过期时间 | `168`（7天） |
| `WX_APPID` | 微信小程序AppID | 空（开发模式） |
| `WX_SECRET` | 微信小程序Secret | 空（开发模式） |
| `CORS_ORIGINS` | CORS允许域名 | `*` |
| `UPLOAD_DIR` | 上传文件目录 | `./uploads` |
| `MAX_UPLOAD_SIZE_MB` | 上传大小限制 | `10` |

## API 概览

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/login` | 微信登录（code → JWT） |
| 认证 | `GET /api/auth/profile` | 获取当前用户信息 |
| 用户 | `PUT /api/users/profile` | 更新用户信息 |
| 用户 | `POST /api/users/verify` | 身份核验（L1-L4） |
| 用户 | `GET /api/users/properties` | 获取房产列表 |
| 投票 | `GET /api/votes` | 投票列表（分页+搜索） |
| 投票 | `GET /api/votes/{id}` | 投票详情 |
| 投票 | `POST /api/votes` | 创建投票（业委会） |
| 投票 | `POST /api/votes/{id}/submit` | 提交投票 |
| 工单 | `GET /api/orders` | 工单列表（分页+搜索） |
| 工单 | `GET /api/orders/{id}` | 工单详情 |
| 工单 | `POST /api/orders` | 提交报修 |
| 工单 | `POST /api/orders/{id}/accept` | 接单（物业） |
| 工单 | `POST /api/orders/{id}/process` | 开始处理（物业） |
| 工单 | `POST /api/orders/{id}/complete` | 完成维修（物业） |
| 工单 | `POST /api/orders/{id}/rate` | 评价 |
| 工单 | `POST /api/orders/{id}/rework` | 申请复修 |
| 财务 | `GET /api/finance` | 报表列表（分页） |
| 财务 | `GET /api/finance/{id}` | 报表详情 |
| 财务 | `POST /api/finance` | 上报报表（物业） |
| 财务 | `POST /api/finance/{id}/approve` | 审批（业委会） |
| 公告 | `GET /api/announcements` | 公告列表（分页+搜索） |
| 公告 | `GET /api/announcements/{id}` | 公告详情（自动记录阅读） |
| 公告 | `POST /api/announcements` | 发布公告 |
| 社区 | `GET /api/communities` | 社区列表 |
| 社区 | `GET /api/communities/{id}` | 社区详情 |
| 社区 | `POST /api/communities` | 创建社区（业委会） |
| 社区 | `PUT /api/communities/{id}` | 更新社区（业委会） |
| 上传 | `POST /api/upload` | 上传文件 |
| 统计 | `GET /api/stats/dashboard` | 仪表盘统计 |
| 统计 | `GET /api/stats/overview` | 社区概览 |
| 系统 | `GET /api/health` | 健康检查 |

### 分页参数

所有列表接口支持以下查询参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `page` | 页码 | `1` |
| `pageSize` | 每页数量 | `20`（最大100） |

### 搜索/筛选参数

| 接口 | 参数 | 说明 |
|------|------|------|
| 投票列表 | `status` | 按状态筛选 |
| 投票列表 | `keyword` | 按标题搜索 |
| 工单列表 | `status` | 按状态筛选 |
| 工单列表 | `category` | 按分类筛选 |
| 工单列表 | `keyword` | 按描述搜索 |
| 财务列表 | `status` | 按状态筛选 |
| 公告列表 | `type` | 按类型筛选 |
| 公告列表 | `keyword` | 按标题搜索 |

## 数据库结构

```
communities → users → user_properties
            ↙        ↘
votes → vote_options + vote_records
repair_orders → order_timelines
finance_reports → finance_items
announcements → announcement_reads
```

## 数据库迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 开发模式

未配置微信 appid/secret 时，登录接口支持开发模式：
- 传入任意 code，系统将 `dev_{code}` 作为 openid
- 自动创建用户并返回 token

## 种子数据

运行 `python seed.py` 创建：
- 社区：黑金时代广场（512户，45600㎡）
- 3个测试用户：业主(张先生) / 物业(物业服务中心) / 业委会(张主任)
- 3个投票（2个进行中，1个已结束）
- 3个工单（不同状态）
- 3个财务报表（2个已发布，1个待审批）
- 4个公告

## 项目结构

```
server/
├── app/
│   ├── main.py           # FastAPI入口
│   ├── config.py          # 配置管理（pydantic-settings）
│   ├── database.py        # 数据库连接
│   ├── middleware/         # 中间件（认证/异常/限流）
│   ├── models/            # ORM模型
│   ├── routers/           # API路由
│   ├── schemas/           # Pydantic Schema
│   ├── services/          # 业务逻辑层
│   └── utils/             # 工具函数（日志/微信）
├── alembic/               # 数据库迁移
├── uploads/               # 上传文件目录
├── .env.example           # 环境变量模板
└── seed.py                # 种子数据
```
