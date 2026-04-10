# Gist Research Desk Backend

面向科研资料管理场景的后端服务，负责认证鉴权、项目管理、资料条目存储，以及异步 AI 任务处理。

[GitHub 仓库](https://github.com/AI4Research-Gist/pc_gist) · [Swagger 文档](http://127.0.0.1:8000/docs) · [OpenAPI JSON](http://127.0.0.1:8000/openapi.json)

## 项目定位

`pc_gist_back/backend` 是 `Gist Research Desk` 的后端服务，承担整个系统的数据中枢与业务编排职责，主要提供：

- 统一的 `/api/v1` REST API
- 用户注册、登录、资料维护与鉴权能力
- 项目与资料条目的增删改查
- 异步 AI 任务创建、状态流转与结果回写
- 面向前端工作台的稳定数据读写服务

这个仓库既适合继续开发，也适合直接作为公开展示项目使用。它已经具备一条完整的产品主线：用户登录后，可以创建项目、导入资料、发起 AI 处理、查看结构化结果，并把结果保存为知识条目。

## 展示亮点

- 基于 FastAPI、SQLAlchemy、Alembic 的清晰分层架构
- 已实现认证、用户、项目、条目、AI 任务五类核心模块
- 支持 URL、文本、图片、音频等多种 AI 任务入口
- 自带 Swagger / ReDoc，适合现场演示 API
- 具备本地测试覆盖，便于答辩和代码说明
- 能够与前端仓库配合形成完整的端到端展示链路

## 仓库入口

- 后端仓库：<https://github.com/AI4Research-Gist/pc_gist>
- 前端仓库：<https://github.com/AI4Research-Gist/pc_gist_front>

如果用于项目展览，推荐的展示方式是：

1. 先展示前端界面与业务流程
2. 再展示后端 API 分组与 AI 任务处理逻辑
3. 最后串联一次完整的端到端演示

## 后端解决的问题

科研资料整理通常会分散在多个环节中：

- 从网页、笔记、截图、音频中收集信息
- 把原始内容转成结构化摘要
- 按项目归档资料
- 为后续阅读、复盘和同步保留结果

这个后端的价值，就是把这些分散流程收束到统一服务层中。它接收前端请求，校验业务规则，持久化到数据库，并驱动较长耗时的 AI 任务执行。

## 核心业务模块

### 1. 认证模块

- 用户注册
- 用户登录
- 获取当前用户信息
- 修改密码
- 登出接口响应

### 2. 用户资料模块

- 查询当前用户资料
- 更新个人资料
- 检查用户名是否可用

### 3. 项目管理模块

- 项目列表、筛选与分页
- 项目详情查询
- 创建项目
- 更新项目信息
- 删除项目

### 4. 条目管理模块

- 管理论文、文章、竞赛、洞察、语音等资料条目
- 条目列表与筛选
- 条目详情查询
- 创建、更新、删除条目
- 支持标签、摘要、状态、阅读状态与项目归属

### 5. AI 任务模块

- 创建 AI 任务
- 查询任务状态
- 解析网页链接
- 整理原始文本
- 解析图片内容
- 转写音频内容

## 支持的 AI 任务类型

| 任务类型 | 输入类型 | 说明 |
| --- | --- | --- |
| `parse-link` | `url` | 抓取网页正文并生成结构化内容 |
| `structure-text` | `text` | 将原始文本整理成统一条目数据 |
| `parse-image` | `image` | 对图片执行 OCR / 视觉信息提取 |
| `transcribe-audio` | `audio` | 对语音进行转写并输出结构化摘要 |

这些任务的输出会被统一规范化，便于前端直接预览、保存，或回填到已有条目中。

## 系统架构

后端采用清晰直接的分层结构：

```text
客户端请求
  -> API Router
  -> Schema 校验
  -> Service 业务层
  -> Repository 数据访问层
  -> SQLAlchemy Models
  -> Database

AI 任务链路
  -> 创建任务记录
  -> 标记为 pending
  -> BackgroundTasks 执行处理
  -> 更新 processing / done / failed
  -> 前端轮询获取结果
```

### 架构特点

- 使用 `FastAPI` 提供类型化接口与自动生成文档
- 使用 `Pydantic` 处理请求与响应校验
- 使用 `SQLAlchemy` 负责 ORM 与持久化
- 使用 `Alembic` 管理数据库迁移
- 使用 `httpx` 处理外部 AI 与网页抓取请求
- 使用 `item_ai_tasks` 表记录异步任务状态与结果

## 项目结构

```text
pc_gist_back/
├─ backend/
│  ├─ alembic/
│  │  ├─ env.py
│  │  └─ versions/
│  ├─ app/
│  │  ├─ api/
│  │  │  ├─ deps.py
│  │  │  ├─ router.py
│  │  │  └─ v1/
│  │  ├─ clients/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ models/
│  │  ├─ repositories/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  └─ main.py
│  ├─ tests/
│  ├─ .env.example
│  ├─ alembic.ini
│  └─ requirements.txt
├─ doc/
└─ README.md
```

## 数据模型概览

当前迁移已经覆盖以下核心表：

- `users`
- `projects`
- `items`
- `item_ai_tasks`

### 表职责说明

- `users`：账户身份与用户基础资料
- `projects`：项目容器，用于组织主题化资料
- `items`：统一存储论文、文章、竞赛、洞察、语音等条目
- `item_ai_tasks`：记录 AI 任务状态、结果与错误信息

## API 分组

当前已经暴露如下接口分组：

| 分组 | 路径前缀 | 说明 |
| --- | --- | --- |
| Health | `/api/v1/health` | 服务健康检查 |
| Auth | `/api/v1/auth/*` | 注册、登录、登出、修改密码、当前用户 |
| Users | `/api/v1/users/*` | 用户资料与用户名检查 |
| Projects | `/api/v1/projects/*` | 项目管理 |
| Items | `/api/v1/items/*` | 条目管理 |
| AI Tasks | `/api/v1/ai-tasks/*` | AI 任务创建与状态查询 |

## 接口示例

### 登录

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "demo_user",
    "password": "secret123"
  }'
```

### 创建文本 AI 任务

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

### 查询任务状态

```bash
curl "http://127.0.0.1:8000/api/v1/ai-tasks/1" \
  -H "Authorization: Bearer <access_token>"
```

## AI 任务处理流程

当前 AI 链路采用异步风格的任务生命周期：

1. 前端发起创建任务请求。
2. 后端写入 `item_ai_tasks` 记录，状态为 `pending`。
3. 后台任务将状态改为 `processing`。
4. 根据任务类型处理 URL、文本、图片或音频输入。
5. 最终将状态更新为 `done` 或 `failed`。
6. 前端通过轮询接口读取结果或失败原因。

这种设计能够保持同步接口简单，同时支持相对耗时的 AI 处理流程。

## 技术栈

- Python `3.12+`
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic v2
- Alembic
- MySQL
- httpx
- python-jose
- passlib

## 运行要求

- Python `3.12+`
- MySQL `8.x` 或兼容数据库
- 如果需要启用 AI 任务，必须提供有效的 `SILICONFLOW_API_KEY`

## 快速开始

### 1. 创建虚拟环境

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. 安装依赖

```powershell
pip install -r backend\requirements.txt
pip install pytest
```

### 3. 创建环境变量文件

```powershell
Copy-Item backend\.env.example backend\.env
```

### 4. 创建数据库

```sql
CREATE DATABASE gist_backend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 执行迁移

```powershell
cd backend
alembic upgrade head
```

### 6. 启动服务

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>
- OpenAPI JSON：<http://127.0.0.1:8000/openapi.json>

## 环境变量说明

请基于 `backend/.env.example` 创建 `backend/.env`。常用变量如下：

| 变量名 | 说明 |
| --- | --- |
| `APP_NAME` | 服务名称 |
| `APP_ENV` | 运行环境 |
| `APP_HOST` | 监听地址 |
| `APP_PORT` | 监听端口 |
| `APP_DEBUG` | 调试模式 |
| `API_V1_PREFIX` | API 前缀 |
| `SECRET_KEY` | JWT 签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期 |
| `DATABASE_URL` | MySQL 连接串 |
| `ALLOWED_ORIGINS` | CORS 白名单 |
| `SILICONFLOW_API_KEY` | AI 服务密钥 |
| `SILICONFLOW_BASE_URL` | AI 服务地址 |
| `SILICONFLOW_TEXT_MODEL` | 文本模型 |
| `SILICONFLOW_VISION_MODEL` | 视觉模型 |
| `SILICONFLOW_AUDIO_MODEL` | 音频模型 |
| `SILICONFLOW_REQUEST_TIMEOUT` | AI 请求超时 |
| `WEBPAGE_FETCH_CONNECT_TIMEOUT` | URL 抓取连接超时 |
| `WEBPAGE_FETCH_READ_TIMEOUT` | URL 抓取读取超时 |
| `WEBPAGE_FETCH_MAX_BYTES` | 单次网页最大抓取字节数 |
| `WEBPAGE_FETCH_RETRIES` | 网页抓取重试次数 |

示例：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/gist_backend
ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
SILICONFLOW_API_KEY=your_api_key_here
```

## 测试

执行后端测试：

```powershell
cd backend
pytest tests
```

当前测试覆盖包括：

- 健康检查
- 认证流程
- 用户资料
- 项目 CRUD
- 条目 CRUD
- AI 任务创建与查询
- URL 抓取超时处理

## 展示建议

如果你要把这个仓库用于答辩、作品集或项目展览，建议按下面顺序演示：

1. 打开 Swagger 展示接口分组
2. 说明 `users / projects / items / ai-tasks` 四类核心数据
3. 演示创建文本 AI 任务并轮询结果
4. 结合前端展示结果如何回存为条目

## 当前边界说明

这个仓库已经具备完整展示价值，但 README 也应如实说明当前边界：

- AI 能力依赖外部服务可用性
- `logout` 采用无状态 JWT 语义
- 若用于公开开源，建议补充 `LICENSE`
- 如果后续要上生产，还需要继续完善部署、监控与安全配置

## 为什么适合展览

- 有清晰的产品场景，不只是单点工具接口
- Swagger 页面非常适合现场演示
- AI 任务状态流转直观，容易解释
- 架构清晰，评审能快速理解代码组织
- 能和前端仓库自然组成完整作品展示

## License

当前仓库尚未附带许可证文件。如果需要公开展示或对外分发，建议在仓库根目录补充 `LICENSE`。
