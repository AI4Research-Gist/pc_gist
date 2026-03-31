# Gist Research Desk Backend

`pc_gist_back/backend` 是 `Gist Research Desk` 的后端服务，基于 `FastAPI + SQLAlchemy + Alembic + Pydantic` 构建，负责提供认证、用户资料、项目管理、条目管理和 AI 任务处理接口。

这个服务当前主要面向本地开发、前后端联调和后续功能扩展，已经具备清晰的分层结构和基础测试用例，适合作为一个持续演进中的业务后端工程。

## 项目能力

- 提供统一的 `/api/v1` 版本化接口
- 用户注册、登录、获取当前用户、修改密码、登出
- 用户资料查询与更新、用户名可用性检查
- 项目 CRUD 与分页查询
- 条目 CRUD、筛选、排序与分页查询
- AI 任务创建与状态查询
- Alembic 数据库迁移
- 基础接口测试

## 技术栈

- Python `3.12+`
- FastAPI
- SQLAlchemy `2.x`
- Alembic
- Pydantic `2.x`
- MySQL + PyMySQL
- HTTPX

## 目录结构

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

## 本地运行

### 运行要求

- Python `3.12+`
- MySQL `8.x` 或兼容版本

### 1. 创建虚拟环境

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
pip install pytest
```

说明：

- 当前 `pytest` 还未写入 `requirements.txt`，因此测试环境需要额外安装

### 3. 配置环境变量

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

常用变量如下：

| 变量 | 说明 |
| --- | --- |
| `APP_NAME` | 应用名称 |
| `APP_ENV` | 运行环境，例如 `development` |
| `APP_HOST` | 服务监听地址 |
| `APP_PORT` | 服务端口 |
| `APP_DEBUG` | 是否开启调试模式 |
| `API_V1_PREFIX` | API 前缀，默认 `/api/v1` |
| `SECRET_KEY` | JWT 签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） |
| `DATABASE_URL` | 数据库连接串 |
| `ALLOWED_ORIGINS` | CORS 白名单，JSON 数组格式 |
| `SILICONFLOW_API_KEY` | SiliconFlow API Key，启用 AI 任务时需要 |
| `SILICONFLOW_BASE_URL` | SiliconFlow 接口地址 |
| `SILICONFLOW_TEXT_MODEL` | 文本模型 |
| `SILICONFLOW_VISION_MODEL` | 视觉模型 |
| `SILICONFLOW_AUDIO_MODEL` | 音频转写模型 |
| `SILICONFLOW_REQUEST_TIMEOUT` | AI 请求超时秒数 |

数据库连接示例：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/gist_backend
```

### 4. 创建数据库

先在本地 MySQL 中创建数据库：

```sql
CREATE DATABASE gist_backend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 执行迁移

```powershell
alembic upgrade head
```

当前迁移会创建的核心表包括：

- `users`
- `projects`
- `items`
- `item_ai_tasks`

### 6. 启动服务

推荐开发命令：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

也可以直接运行入口文件：

```powershell
python app\main.py
```

服务启动后可访问：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`

## 接口概览

所有业务接口默认挂载在 `API_V1_PREFIX` 下，默认值为 `/api/v1`。

### Health

- `GET /api/v1/health`

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

说明：

- 登录支持用户名、邮箱、手机号三种标识
- `change-password`、`logout`、`me` 需要 `Bearer Token`

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

支持：

- 关键字搜索
- 分页：`page`、`page_size`

### Items

- `GET /api/v1/items`
- `POST /api/v1/items`
- `GET /api/v1/items/{item_id}`
- `PATCH /api/v1/items/{item_id}`
- `DELETE /api/v1/items/{item_id}`

支持：

- 按 `type`、`project_id`、`status`、`read_status` 过滤
- `keyword` 搜索
- 分页：`page`、`page_size`
- 排序：`sort_by`、`sort_order`

### AI Tasks

- `POST /api/v1/ai-tasks`
- `GET /api/v1/ai-tasks/{task_id}`

支持的任务类型：

- `parse-link`
- `structure-text`
- `parse-image`
- `transcribe-audio`

## 认证说明

项目当前使用 JWT Bearer Token。

### 登录示例

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "demo_user",
    "password": "secret123"
  }'
```

成功后会返回：

- `user`
- `access_token`
- `token_type`

### 鉴权请求示例

```bash
curl "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your_access_token>"
```

## AI 任务示例

### 创建文本结构化任务

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ai-tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "task_type": "structure-text",
    "input_type": "text",
    "input_payload": {
      "text": "这是一个关于科研工具的文章摘要。",
      "target_type": "article"
    }
  }'
```

### 查询任务状态

```bash
curl "http://127.0.0.1:8000/api/v1/ai-tasks/1" \
  -H "Authorization: Bearer <your_access_token>"
```

说明：

- AI 任务通过 FastAPI `BackgroundTasks` 异步调度
- 创建任务后通常会先返回 `pending`
- 前端会继续轮询任务状态并展示结果

## 测试

运行测试：

```powershell
pytest tests
```

当前测试特点：

- 大多数测试使用内存 SQLite，不依赖本地 MySQL
- AI 任务测试会 mock `AITaskProcessor`
- 已覆盖健康检查、认证、用户、项目、条目、AI 任务等主链路

## 开发说明

### 配置加载

配置会优先从以下位置读取 `.env`：

- `backend/.env`
- 仓库根目录 `.env`

### 数据库迁移

创建新迁移：

```powershell
alembic revision --autogenerate -m "your message"
```

回滚一步：

```powershell
alembic downgrade -1
```

### 分层约定

- `api/`：路由、依赖注入、HTTP 层
- `schemas/`：请求和响应模型
- `services/`：业务逻辑
- `repositories/`：数据库访问抽象
- `models/`：ORM 模型
- `clients/`：外部 AI 服务调用

## 当前限制与注意事项

这部分建议在 GitHub 页面保留，方便协作者快速理解项目边界：

- `projects` 和 `items` 当前仍处于开发阶段，尚未完全绑定到当前登录用户
- `projects` 和 `items` 的创建逻辑目前会优先关联 ID 为 `1` 的用户
- `logout` 当前是无状态 JWT 语义，服务端不会主动失效已签发 token
- AI 功能依赖 `SILICONFLOW_API_KEY`，未配置时相关接口会无法正常工作

如果准备进一步对外公开或上线，建议优先补齐：

- 更严格的资源归属校验
- 更完整的鉴权边界
- 生产环境配置说明
- CI / 测试自动化
- Docker 化部署方案

## 常见问题

### `alembic upgrade head` 失败

优先检查：

- MySQL 是否已启动
- `DATABASE_URL` 是否正确
- 数据库 `gist_backend` 是否已提前创建

### 跨域不生效

请确认 `ALLOWED_ORIGINS` 使用 JSON 数组字符串，例如：

```env
ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

### AI 任务报错 `SILICONFLOW_API_KEY is not configured`

说明当前环境没有配置 AI 服务密钥。只要需要调用 AI 任务，这个变量就是必填项。

