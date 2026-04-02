# Gist Research Desk Backend

Structured backend service for authentication, research items, project organization, and AI task processing.

`pc_gist_back/backend` 是 `Gist Research Desk` 的后端服务，负责提供统一的业务 API、数据存储能力和 AI 任务处理入口。当前实现已经覆盖认证、用户资料、项目管理、资料条目管理和异步 AI 任务，是整个工作台的数据与业务中枢。

## Overview

这个后端服务围绕四类核心对象工作：

- 用户
- 项目
- 条目
- AI 任务

它承担的主要职责包括：

- 提供统一的 `/api/v1` 接口
- 维护用户登录态和账户信息
- 管理项目和资料条目
- 接收并执行 AI 处理任务
- 为前端页面提供稳定的数据读取与写入能力

## Service Capabilities

### 1. Authentication

- 用户注册
- 用户登录
- 获取当前用户信息
- 修改密码
- 登出

### 2. User Profile

- 读取当前用户资料
- 更新当前用户资料
- 检查用户名是否可用

### 3. Project Management

- 项目列表
- 项目详情
- 创建项目
- 更新项目
- 删除项目
- 关键字搜索和分页

### 4. Item Management

- 条目列表
- 条目详情
- 创建条目
- 更新条目
- 删除条目
- 类型筛选
- 项目筛选
- 状态筛选
- 阅读状态筛选
- 关键字搜索
- 分页和排序

### 5. AI Task Processing

- 创建 AI 任务
- 查询任务状态
- 异步执行链接解析
- 异步执行文本结构化
- 异步执行图片 OCR 解析
- 异步执行音频转写和整理

### 6. Database Migration

- 使用 Alembic 管理数据库结构
- 已包含基础表结构和 AI 任务表迁移

### 7. Basic Test Coverage

- 健康检查
- 认证流程
- 用户资料
- 项目 CRUD
- 条目 CRUD
- AI 任务接口

## API Groups

当前实际挂载的接口分组如下：

| Group | Base Path | Description |
| --- | --- | --- |
| Health | `/api/v1/health` | 服务健康检查 |
| Auth | `/api/v1/auth/*` | 注册、登录、登出、修改密码、当前用户 |
| Users | `/api/v1/users/*` | 用户资料和用户名检查 |
| Projects | `/api/v1/projects/*` | 项目管理 |
| Items | `/api/v1/items/*` | 资料条目管理 |
| AI Tasks | `/api/v1/ai-tasks/*` | AI 任务创建与状态查询 |

## Supported AI Tasks

当前支持的 AI 任务类型包括：

- `parse-link`
- `structure-text`
- `parse-image`
- `transcribe-audio`

这些任务分别面向：

- 网页内容抓取与结构化
- 原始文本整理
- 图片 OCR 与信息抽取
- 音频转写与结构化整理

## Architecture

后端当前采用清晰的分层结构：

```text
HTTP API
  -> Schemas
  -> Services
  -> Repositories
  -> SQLAlchemy Models
  -> Database

AI Task Flow
  -> Create task
  -> Save as pending
  -> Run in BackgroundTasks
  -> Update status
  -> Return output payload
```

主要目录如下：

```text
backend/
├─ alembic/
│  ├─ env.py
│  └─ versions/
├─ app/
│  ├─ api/
│  │  ├─ deps.py
│  │  ├─ router.py
│  │  └─ v1/
│  ├─ clients/
│  ├─ core/
│  ├─ db/
│  ├─ models/
│  ├─ repositories/
│  ├─ schemas/
│  ├─ services/
│  └─ main.py
├─ tests/
├─ .env.example
├─ alembic.ini
├─ requirements.txt
└─ README.md
```

## Core Data Model

当前数据库迁移已经覆盖以下核心表：

- `users`
- `projects`
- `items`
- `item_ai_tasks`

四类数据对象分别负责：

- `users`：用户信息和登录基础数据
- `projects`：资料归档容器
- `items`：论文、文章、竞赛、洞察、语音等资料条目
- `item_ai_tasks`：AI 处理任务及其结果

## Local Setup

### Requirements

- Python `3.12+`
- MySQL `8.x` or compatible

### 1. Create a virtual environment

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
pip install pytest
```

## Configuration

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

常用变量如下：

| Variable | Description |
| --- | --- |
| `APP_NAME` | 应用名称 |
| `APP_ENV` | 运行环境 |
| `APP_HOST` | 服务监听地址 |
| `APP_PORT` | 服务端口 |
| `APP_DEBUG` | 调试模式开关 |
| `API_V1_PREFIX` | API 前缀 |
| `SECRET_KEY` | JWT 签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间 |
| `DATABASE_URL` | 数据库连接串 |
| `ALLOWED_ORIGINS` | CORS 白名单 |
| `SILICONFLOW_API_KEY` | AI 服务密钥 |
| `SILICONFLOW_BASE_URL` | AI 服务地址 |
| `SILICONFLOW_TEXT_MODEL` | 文本模型 |
| `SILICONFLOW_VISION_MODEL` | 视觉模型 |
| `SILICONFLOW_AUDIO_MODEL` | 音频模型 |
| `SILICONFLOW_REQUEST_TIMEOUT` | 请求超时 |

示例：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/gist_backend
ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

## Database Migration

### Create database

```sql
CREATE DATABASE gist_backend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Run migrations

```powershell
alembic upgrade head
```

### Create a new migration

```powershell
alembic revision --autogenerate -m "your message"
```

### Roll back one step

```powershell
alembic downgrade -1
```

## Run the Server

推荐开发命令：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

也可以直接运行入口文件：

```powershell
python app\main.py
```

服务启动后可访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## API Summary

### Health

- `GET /api/v1/health`

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### Users

- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `GET /api/v1/users/check-username`

### Projects

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`

### Items

- `GET /api/v1/items`
- `POST /api/v1/items`
- `GET /api/v1/items/{item_id}`
- `PATCH /api/v1/items/{item_id}`
- `DELETE /api/v1/items/{item_id}`

### AI Tasks

- `POST /api/v1/ai-tasks`
- `GET /api/v1/ai-tasks/{task_id}`

## Example Usage

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "demo_user",
    "password": "secret123"
  }'
```

### Create an AI text task

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai-tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "task_type": "structure-text",
    "input_type": "text",
    "input_payload": {
      "text": "example content",
      "target_type": "article"
    }
  }'
```

### Query task status

```bash
curl "http://127.0.0.1:8000/api/v1/ai-tasks/1" \
  -H "Authorization: Bearer <access_token>"
```

## Testing

运行测试：

```powershell
pytest tests
```

当前测试覆盖范围包括：

- 健康检查
- 认证流程
- 用户资料
- 项目 CRUD
- 条目 CRUD
- AI 任务接口

测试特点：

- 大多数测试基于内存 SQLite
- AI 任务测试会 mock `AITaskProcessor`

## Current Implementation Notes

以下内容属于当前代码的真实边界，适合在公开仓库中保留说明：

- `projects` 和 `items` 当前尚未完全切换到基于当前登录用户的严格资源隔离
- `projects` 和 `items` 创建时会优先绑定 `Id = 1` 的用户
- `logout` 当前是无状态 JWT 语义，服务端不会主动失效已签发 token
- AI 任务依赖 `SILICONFLOW_API_KEY`
- 未配置 AI 服务密钥时，AI 相关接口无法正常工作

## License

仓库当前未附带许可证文件。对外发布时，可在仓库根目录补充 `LICENSE`。
