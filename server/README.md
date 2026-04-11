# 业问后端 — 智慧社区业主微信小程序

FastAPI + SQLAlchemy 2.0 + PostgreSQL/SQLite

## 快速开始

### 方式一：一键启动（推荐）

```bash
cd /Users/a99/WorkBuddy/20260410121727/server
./start.sh
```

脚本会自动创建 Python 3.12 虚拟环境、安装依赖、初始化种子数据、启动服务。

访问 http://localhost:8000/docs 查看 Swagger API 文档

### 方式二：手动启动

> ⚠️ 需要 Python 3.12+（Python 3.14 暂不兼容部分依赖）
> 
> 如未安装：`brew install python@3.12`

```bash
cd /Users/a99/WorkBuddy/20260410121727/server

# 创建虚拟环境（首次）
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate

# 安装依赖 + 种子数据 + 启动
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

### 方式二：Docker Compose（PostgreSQL）

```bash
cd server
cp .env.example .env    # 修改微信 appid/secret
docker-compose up -d
```

## API 概览

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/login` | 微信登录（code → JWT） |
| 认证 | `GET /api/auth/profile` | 获取当前用户信息 |
| 用户 | `PUT /api/users/profile` | 更新用户信息 |
| 用户 | `POST /api/users/verify` | 身份核验（L1-L4） |
| 用户 | `GET /api/users/properties` | 获取房产列表 |
| 投票 | `GET /api/votes` | 投票列表 |
| 投票 | `GET /api/votes/{id}` | 投票详情 |
| 投票 | `POST /api/votes` | 创建投票（业委会） |
| 投票 | `POST /api/votes/{id}/submit` | 提交投票 |
| 工单 | `GET /api/orders` | 工单列表 |
| 工单 | `GET /api/orders/{id}` | 工单详情 |
| 工单 | `POST /api/orders` | 提交报修 |
| 工单 | `POST /api/orders/{id}/accept` | 接单（物业） |
| 工单 | `POST /api/orders/{id}/rate` | 评价 |
| 工单 | `POST /api/orders/{id}/rework` | 申请复修 |
| 财务 | `GET /api/finance` | 报表列表 |
| 财务 | `GET /api/finance/{id}` | 报表详情 |
| 财务 | `POST /api/finance` | 上报报表（物业） |
| 财务 | `POST /api/finance/{id}/approve` | 审批（业委会） |
| 公告 | `GET /api/announcements` | 公告列表 |
| 公告 | `GET /api/announcements/{id}` | 公告详情（自动记录阅读） |
| 公告 | `POST /api/announcements` | 发布公告 |

## 数据库结构

```
communities → users → user_properties
            ↙        ↘
votes → vote_options + vote_records
repair_orders → order_timelines
finance_reports → finance_items
announcements → announcement_reads
```

## 开发模式

未配置微信 appid/secret 时，登录接口支持开发模式：
- 传入任意 code，系统将 `dev_{code}` 作为 openid
- 自动创建用户并返回 token

## 种子数据

运行 `python seed.py` 创建：
- 社区：翠湖花园（512户，45600㎡）
- 3个测试用户：业主(张先生) / 物业(物业服务中心) / 业委会(张主任)
- 3个投票（2个进行中，1个已结束）
- 3个工单（不同状态）
- 3个财务报表（2个已发布，1个待审批）
- 4个公告
