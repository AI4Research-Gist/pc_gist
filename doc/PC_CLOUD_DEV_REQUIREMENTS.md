# Gist PC 端云开发需求设计文档

## 1. 文档目的

本文档用于指导 `Gist / 研简` 项目的 PC 端云开发工作，目标是基于现有移动端能力，完成一套可独立运行、可持续扩展、可与 Android 客户端对接的云端系统与 Web 管理端方案。

本文档重点覆盖：

- PC 端开发范围定义
- 云端数据库重建设计
- FastAPI 后端接口设计
- Vue3 Web 端功能设计
- 与当前 Android 客户端的兼容与迁移方案
- 开发排期、验收标准与风险控制

## 2. 项目背景

根据现有项目计划书与接口说明，`Gist` 当前定位为面向科研调研与竞赛备赛的信息采集与结构化整理工具，核心价值是把用户在手机端看到的链接、截图、语音灵感等碎片化内容，转化为可复用的知识卡片。

当前实际状态：

- Android 客户端已完成主要业务能力
- 移动端当前仍大量直连 NocoDB
- 用户登录目前本质上是直接查询 `users` 表
- 项目数据模型已稳定为 `users / projects / items`
- 现网已引入按用户隔离的数据归属字段 `ownerId`

因此，PC 端云开发的目标不是简单“复制一套页面”，而是要补足正式服务端，建立统一数据库和业务 API，承接后续 Web 端、管理端与移动端的共同访问需求。

## 3. 建设目标

### 3.1 总体目标

建设一套基于 `Vue3 + FastAPI` 的 PC 端云服务系统，完成：

- 重建与移动端兼容的正式数据库
- 统一用户、项目、条目三类核心业务数据
- 对外提供稳定的业务 API
- 提供 PC Web 端管理与操作界面
- 为后续 Android 从“直连 NocoDB”平滑迁移到“直连业务后端”做好准备

### 3.2 本期目标

本期建议按“MVP 可对接优先”落地：

- 优先完成核心表与核心 CRUD API
- 保持对 Android 当前字段契约兼容
- 优先实现账号、项目、条目、搜索、筛选、状态更新
- 预留 AI 异步解析、文件上传、团队协作接口

### 3.3 非目标

本期暂不作为强制目标：

- 完整替换所有第三方 AI 服务
- 做复杂权限中心或企业级 RBAC
- 做复杂消息中心、评论系统、组织架构系统
- 做桌面客户端

## 4. PC 端开发范围定义

这里的“PC 端”建议定义为两部分：

1. 云端服务端
   - 使用 `FastAPI`
   - 负责认证、业务逻辑、数据库访问、AI 任务编排、文件存储接入

2. Web 管理与使用端
   - 使用 `Vue3`
   - 负责用户在浏览器中的登录、项目管理、条目管理、检索、详情查看、后台维护

即：本期是“云端 + Web”的 PC 方案，而不是本地桌面软件方案。

## 5. 总体架构设计

## 5.1 推荐技术栈

### 后端

- `FastAPI`
- `SQLAlchemy 2.x`
- `Pydantic v2`
- `Alembic`
- `MySQL 8.0` 或 `PostgreSQL 15`
- `Redis`（缓存、任务状态、验证码或限流）
- `Celery` 或 `RQ`（异步 AI 解析任务，可第二阶段接入）
- `Nginx`（反向代理）

### 前端

- `Vue3`
- `Vite`
- `TypeScript`
- `Pinia`
- `Vue Router`
- `Axios`
- `Element Plus` 或 `Naive UI`
- `MarkdownIt` / `md-editor-v3`（Markdown 查看与编辑）

### 存储与部署

- 数据库：`MySQL / PostgreSQL`
- 对象存储：本地 `MinIO` 或云 OSS
- 部署：Docker Compose

## 5.2 分层结构

### 后端分层

- `api`：路由定义
- `service`：业务逻辑
- `repository`：数据库访问
- `model`：ORM 模型
- `schema`：请求/响应模型
- `task`：异步任务
- `core`：配置、日志、鉴权、中间件

### 前端分层

- `pages`：页面级视图
- `components`：通用组件
- `stores`：状态管理
- `api`：接口请求封装
- `types`：类型定义
- `utils`：工具方法

## 5.3 业务架构图

```text
Vue3 Web
   |
   v
FastAPI Gateway
   |
   +-- Auth Service
   +-- User Service
   +-- Project Service
   +-- Item Service
   +-- Search Service
   +-- AI Task Service
   |
   +-- MySQL/PostgreSQL
   +-- Redis
   +-- Object Storage
   +-- SiliconFlow / 其他模型服务
```

## 6. 核心业务对象

根据现有 Android 代码与接口文档，核心对象保持三类：

- 用户 `users`
- 项目 `projects`
- 研究条目 `items`

其中 `items` 是核心业务实体，当前支持以下类型：

- `paper`
- `competition`
- `insight`
- `voice`

## 7. 数据库设计

## 7.1 设计原则

- 保持与 Android 当前字段尽量兼容
- 去掉对 NocoDB 特定表 ID 的业务依赖
- 支持按用户隔离数据
- 为后续 Web、后台、AI 异步任务留出扩展字段
- 允许当前客户端逐步迁移，不强制一次性改协议

## 7.2 数据库选型建议

优先推荐：

- `MySQL 8.0`

原因：

- 对团队上手成本低
- 与 NocoDB 现有结构迁移更自然
- Docker 部署简单
- 常见云主机支持成熟

如后续更强调 JSON 查询和全文检索，可考虑 `PostgreSQL`。

## 7.3 表结构总览

本期至少建设以下表：

- `users`
- `projects`
- `items`
- `item_ai_tasks`
- `login_logs`
- `operation_logs`

MVP 必须表：

- `users`
- `projects`
- `items`

## 7.4 users 表

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  email VARCHAR(128) UNIQUE,
  phone VARCHAR(32) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(255) NULL,
  biometric_enabled TINYINT(1) DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  last_login_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

字段映射说明：

- Android 的 `Phonenumber` 建议在正式库中统一为 `phone`
- Android 的明文 `password` 在正式库中改为 `password_hash`
- 对外兼容层可继续接受 `username / email / phone` 作为登录标识

## 7.5 projects 表

```sql
CREATE TABLE projects (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_id BIGINT NOT NULL,
  name VARCHAR(128) NOT NULL,
  title VARCHAR(128) NULL,
  description TEXT NULL,
  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_projects_owner FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

说明：

- `name` 保留主展示名
- `title` 用于兼容 Android 当前 `Title`
- 增加 `owner_id` 实现用户隔离
- 建议逻辑删除，避免项目删除导致条目关系混乱

## 7.6 items 表

```sql
CREATE TABLE items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_id BIGINT NOT NULL,
  project_id BIGINT NULL,
  type VARCHAR(32) NOT NULL,
  title VARCHAR(255) NOT NULL,
  summary TEXT NULL,
  content_md LONGTEXT NULL,
  origin_url VARCHAR(500) NULL,
  audio_url VARCHAR(500) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'processing',
  read_status VARCHAR(32) NOT NULL DEFAULT 'unread',
  is_starred TINYINT(1) NOT NULL DEFAULT 0,
  tags VARCHAR(500) NULL,
  meta_json JSON NULL,
  source_platform VARCHAR(64) NULL,
  source_type VARCHAR(64) NULL,
  parse_error TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at DATETIME NULL,
  CONSTRAINT fk_items_owner FOREIGN KEY (owner_id) REFERENCES users(id),
  CONSTRAINT fk_items_project FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

说明：

- `owner_id` 对应现网概念 `ownerId`
- `is_starred` 建议正式落库，补齐 Android 仅本地星标的问题
- `meta_json` 保持 JSON 对象语义
- `deleted_at` 用于软删除

## 7.7 item_ai_tasks 表

```sql
CREATE TABLE item_ai_tasks (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  item_id BIGINT NULL,
  owner_id BIGINT NOT NULL,
  task_type VARCHAR(32) NOT NULL,
  input_type VARCHAR(32) NOT NULL,
  input_payload JSON NOT NULL,
  output_payload JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  error_message TEXT NULL,
  started_at DATETIME NULL,
  finished_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

用途：

- 记录链接解析、截图 OCR、语音转写等异步任务
- 支撑 Web 端查看解析进度
- 后续支持失败重试与审计

## 7.8 索引设计

建议至少建立以下索引：

- `users(username)`
- `users(email)`
- `users(phone)`
- `projects(owner_id, is_deleted)`
- `items(owner_id, type, created_at)`
- `items(owner_id, project_id, created_at)`
- `items(owner_id, read_status, created_at)`
- `items(owner_id, status, created_at)`
- `items(title)`

如使用 MySQL，可在第二阶段补充全文检索；如使用 PostgreSQL，可直接引入 `GIN + tsvector`。

## 8. 与 Android 当前字段契约的兼容要求

## 8.1 当前必须兼容字段

后端对移动端兼容时，需继续支持以下语义：

- `type`：`paper / competition / insight / voice`
- `status`：至少保持 `processing / done / failed` 前缀稳定
- `read_status`：至少保持 `unread / reading / read` 前缀稳定
- `meta_json`：返回 JSON 对象，不要变成字符串
- `projects`：兼容 `name` 与 `Title`

## 8.2 字段映射建议

| Android / NocoDB 字段 | 新库字段 | 说明 |
|---|---|---|
| `Id` | `id` | 主键 |
| `Phonenumber` | `phone` | 正式字段统一 |
| `ownerId` | `owner_id` | 统一蛇形命名 |
| `CreatedAt` | `created_at` | 响应时可兼容转换 |
| `UpdatedAt` | `updated_at` | 响应时可兼容转换 |
| `Title` | `title` / `name` | projects 保留兼容 |

## 8.3 兼容策略

建议分两层：

1. 数据库存正式命名
2. API 响应层兼容旧字段

这样可以避免数据库继续绑定历史脏命名，同时不阻塞 Android 对接。

## 9. 后端 API 设计

## 9.1 API 设计原则

- RESTful 为主
- 移动端与 Web 端共用业务 API
- 对旧客户端提供兼容接口或兼容响应结构
- 所有写操作必须经过业务后端，不再让客户端直连数据库

## 9.2 模块划分

- 认证模块
- 用户模块
- 项目模块
- 条目模块
- AI 任务模块
- 文件上传模块
- 管理后台模块

## 9.3 认证接口

### 注册

`POST /api/v1/auth/register`

请求体：

```json
{
  "username": "tester",
  "email": "user@example.com",
  "phone": "13800000000",
  "password": "plain_password"
}
```

返回：

```json
{
  "user": {
    "id": 1,
    "username": "tester",
    "email": "user@example.com",
    "phone": "13800000000"
  },
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### 登录

`POST /api/v1/auth/login`

请求体：

```json
{
  "identifier": "tester",
  "password": "plain_password"
}
```

说明：

- `identifier` 兼容用户名、邮箱、手机号
- 登录成功返回 JWT，不再返回用户 ID 充当 token

### 获取当前用户

`GET /api/v1/auth/me`

### 退出登录

`POST /api/v1/auth/logout`

## 9.4 用户接口

- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `GET /api/v1/users/check-username?username=tester`

建议更新字段：

- `avatar_url`
- `biometric_enabled`
- `username`

## 9.5 项目接口

### 查询项目列表

`GET /api/v1/projects`

支持参数：

- `keyword`
- `page`
- `page_size`

### 新建项目

`POST /api/v1/projects`

```json
{
  "name": "项目名",
  "title": "项目名",
  "description": "项目描述"
}
```

### 项目详情

`GET /api/v1/projects/{project_id}`

### 修改项目

`PATCH /api/v1/projects/{project_id}`

### 删除项目

`DELETE /api/v1/projects/{project_id}`

建议行为：

- 默认逻辑删除
- 删除时检查是否存在关联 `items`
- 提供“转移到未分组”策略

## 9.6 条目接口

### 条目列表

`GET /api/v1/items`

支持参数：

- `type`
- `project_id`
- `status`
- `read_status`
- `is_starred`
- `keyword`
- `page`
- `page_size`
- `sort_by`
- `sort_order`

### 条目详情

`GET /api/v1/items/{item_id}`

### 新建条目

`POST /api/v1/items`

```json
{
  "title": "示例标题",
  "type": "paper",
  "summary": "摘要",
  "content_md": "Markdown 正文",
  "origin_url": "https://example.com",
  "audio_url": null,
  "status": "processing",
  "read_status": "unread",
  "tags": "tag1,tag2",
  "project_id": 1,
  "meta_json": {
    "authors": ["A", "B"],
    "conference": "ACL",
    "year": 2025
  }
}
```

### 更新条目

`PATCH /api/v1/items/{item_id}`

要求：

- 支持部分字段更新
- 支持兼容 Android “近全量 PATCH”

### 删除条目

`DELETE /api/v1/items/{item_id}`

建议：

- 默认软删除
- 提供后台恢复能力

## 9.7 AI 任务接口

### 提交链接解析任务

`POST /api/v1/ai/parse-link`

```json
{
  "url": "https://example.com/article",
  "target_type": "paper"
}
```

### 提交图片解析任务

`POST /api/v1/ai/parse-image`

### 提交音频转写任务

`POST /api/v1/ai/transcribe-audio`

### 查询任务状态

`GET /api/v1/ai/tasks/{task_id}`

## 9.8 兼容接口层建议

为了尽快接住当前 Android，建议提供一层兼容路由，例如：

- `/compat/items`
- `/compat/projects`
- `/compat/users`

兼容层职责：

- 输出旧字段名
- 保留 NocoDB 风格响应结构
- 便于 Android 低成本改造

不建议长期暴露兼容层作为正式 API。

## 10. Vue3 Web 端功能设计

## 10.1 角色定位

Web 端建议同时承担两种用途：

1. 用户使用端
   - 用户在 PC 浏览器查看、搜索、编辑、归档自己的条目

2. 轻量后台端
   - 管理员查看用户、数据概览、任务状态、日志

如时间紧，可先只做“用户使用端”，后台端第二阶段补齐。

## 10.2 用户端页面

建议优先实现：

- 登录页
- 注册页
- 首页仪表盘
- 条目列表页
- 条目详情页
- 项目管理页
- 收藏/星标页
- 搜索结果页
- 个人设置页

## 10.3 页面功能说明

### 登录与注册

- 支持用户名/邮箱/手机号登录
- 登录后保存 JWT

### 条目列表

- 按类型筛选
- 按项目筛选
- 按阅读状态筛选
- 关键字搜索
- 批量删除
- 批量移动项目
- 标星

### 条目详情

- Markdown 正文展示
- 摘要查看与编辑
- 标签维护
- 项目归属切换
- 阅读状态变更
- AI 结构化信息展示

### 项目管理

- 创建项目
- 编辑项目
- 删除项目
- 查看项目下条目统计

### 个人设置

- 用户名
- 头像
- 密码修改
- 生物识别开关同步展示

## 10.4 后台管理页

建议第二阶段实现：

- 用户列表
- 项目总览
- 条目总览
- AI 任务队列
- 系统日志
- 失败任务重试

## 11. 前后端对接规范

## 11.1 统一返回格式

建议正式 API 使用统一响应体：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

分页格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

## 11.2 错误码建议

- `0`：成功
- `40001`：参数错误
- `40101`：未登录
- `40301`：无权限
- `40401`：资源不存在
- `40901`：资源冲突
- `50001`：服务器内部错误

## 11.3 鉴权方式

推荐：

- `Authorization: Bearer <JWT>`

不再使用：

- 客户端硬编码 `xc-token`
- 用户 ID 直接作为 token

## 12. Android 对接与迁移方案

## 12.1 现状问题

当前 Android 存在以下对接风险：

- 直连 NocoDB，不利于安全与扩展
- 明文密码查询
- 静态 Token 暴露在客户端
- 星标仅本地保存
- 远端删除/更新策略不统一

## 12.2 迁移目标

将 Android 访问路径逐步改为：

```text
Android -> FastAPI -> Database / AI Service
```

## 12.3 建议迁移步骤

### 第一阶段：兼容落地

- FastAPI 重建正式数据库
- 提供与旧结构兼容的接口
- Android 仅替换 Base URL 和认证方式

### 第二阶段：业务收口

- Android 改用正式业务 API
- 停止直连 NocoDB
- 用户登录切换为 JWT
- 星标、删除、状态变更全部走服务端

### 第三阶段：能力增强

- AI 任务异步化
- 文件上传与对象存储接入
- 管理后台与日志体系补齐

## 13. 非功能需求

## 13.1 安全性

- 密码必须哈希存储
- JWT 设置过期时间
- 敏感接口鉴权
- 关键写操作记录日志
- 接口限流
- 输入内容做校验与过滤

## 13.2 性能

- 列表接口支持分页
- 搜索接口支持索引
- AI 任务必须异步
- 高频查询可使用 Redis 缓存

## 13.3 可维护性

- 使用 Alembic 管理数据库迁移
- 使用 OpenAPI 自动生成接口文档
- 拆分环境配置
- 日志统一化

## 13.4 可观测性

- 记录请求日志
- 记录错误日志
- 记录 AI 调用耗时
- 记录任务成功率与失败原因

## 14. 部署方案

## 14.1 推荐部署结构

```text
Nginx
  |- Vue3 Static Files
  |- FastAPI App
  |- MySQL
  |- Redis
  |- Worker
  |- MinIO (optional)
```

## 14.2 环境划分

- `dev`
- `test`
- `prod`

## 14.3 配置管理

建议使用环境变量：

- `APP_ENV`
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `SILICONFLOW_API_KEY`
- `OSS_ENDPOINT`
- `OSS_ACCESS_KEY`
- `OSS_SECRET_KEY`

## 15. 开发排期建议

## 15.1 第一阶段：基础对接版

周期建议：`1-2 周`

交付物：

- 数据库建表
- 认证模块
- users/projects/items 核心 CRUD
- Swagger 文档
- Vue3 登录页与列表页

## 15.2 第二阶段：完整业务版

周期建议：`2-3 周`

交付物：

- 条目详情编辑
- 搜索与筛选
- 项目管理
- 星标与阅读状态同步
- Android 兼容接口层

## 15.3 第三阶段：增强版

周期建议：`2 周`

交付物：

- AI 异步任务
- 文件上传
- 管理后台
- 操作日志
- 失败任务重试

## 16. 验收标准

本期至少满足以下验收条件：

- 用户可注册、登录、退出
- 用户只能看到自己的项目与条目
- 可创建、查询、更新、删除项目
- 可创建、查询、更新、删除条目
- 条目支持按类型、项目、状态筛选
- Web 端可查看并编辑条目详情
- API 文档完整可联调
- Android 可按兼容接口完成最小对接

## 17. 风险与应对

## 17.1 兼容风险

风险：

- Android 当前字段命名不规范
- 状态值存在“英文 + 中文说明”混合格式

应对：

- 增加兼容响应层
- 服务端内部统一标准值，输出时按客户端需求适配

## 17.2 AI 任务风险

风险：

- 三方模型耗时高、失败率不稳定

应对：

- 引入任务表
- 前后端采用异步轮询
- 记录错误并支持重试

## 17.3 数据迁移风险

风险：

- 旧 NocoDB 数据字段历史包袱多

应对：

- 先建立正式库
- 编写一次性迁移脚本
- 迁移后以正式库为主

## 18. 建议的项目目录结构

## 18.1 后端

```text
backend/
  app/
    api/
    core/
    models/
    repositories/
    schemas/
    services/
    tasks/
    main.py
  alembic/
  tests/
  requirements.txt
```

## 18.2 前端

```text
frontend/
  src/
    api/
    components/
    layouts/
    pages/
    router/
    stores/
    types/
    utils/
  public/
  package.json
```

## 19. 结论

对你当前负责的云端开发来说，最合理的路径不是继续围绕 NocoDB 追加临时接口，而是以 `FastAPI + MySQL + Vue3` 为核心，建立一套正式业务后端与 Web 端体系。

本方案的关键落点是：

- 数据库层重建正式表结构，但保留 Android 兼容映射
- 接口层优先完成 users/projects/items 的稳定 CRUD
- Web 层先实现用户可用的管理与编辑能力
- 通过兼容层让移动端逐步从 NocoDB 迁移到业务后端

如果按这个方案推进，你的 PC 端工作既能满足当前“完成对接”的短期目标，也能成为后续整个项目正式交付时的后端基础。

