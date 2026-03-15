# Gist Backend

基于 `FastAPI` 的后端骨架，按项目需求文档拆分为配置、路由、模型、服务、仓储和数据库层，后续可以逐模块补充业务实现。

## 目录结构

```text
backend/
  app/
    api/
    core/
    db/
    models/
    repositories/
    schemas/
    services/
    main.py
  tests/
  requirements.txt
  .env.example
```

## 快速开始

1. 创建虚拟环境并安装依赖
2. 复制 `.env.example` 为 `.env`
3. 按需修改数据库连接
4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 当前状态

- 已完成应用入口、配置、数据库会话和模块化路由注册
- 已预留 `auth / users / projects / items / ai-tasks` 五类业务模块
- 核心三张表 `users / projects / items` 的 SQLAlchemy 模型已按现网 NocoDB 字段名对齐
- `projects / items` 已保留现网实际使用的 `ownerId` 字段
- 已预留 Pydantic Schema、Service、Repository 骨架
- 业务逻辑与数据库迁移脚本后续逐一补齐
