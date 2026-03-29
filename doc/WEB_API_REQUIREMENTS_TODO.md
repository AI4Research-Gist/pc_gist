# Cloud / Web API 集成需求清单

## 1. 文档目的

基于你提供的 `Cloud / Web API Integration Guide`，将当前 Web / 后端需要实现的能力整理成一份可直接执行的需求清单，便于开发、联调和验收。

## 2. 总体目标

当前需要完成的不是复刻安卓 UI，而是完成以下三件核心事情：

1. 对齐 `items / projects / users` 的数据契约与接口行为。
2. 对齐 `meta_json` 在 `paper / article / competition / insight / voice` 下的结构化字段。
3. 为 Web 端和后端补齐当前安卓端已经依赖、或即将依赖的接口与展示支持。

## 3. 外部服务集成需求

### 3.1 NocoDB 集成

需要支持以下能力：

1. 对 `items` 表进行增删改查。
2. 对 `projects` 表进行增删改查。
3. 对 `users` 表进行注册、登录、更新。
4. 所有请求统一携带以下请求头：
   - `xc-token: <NOCO_TOKEN>`
   - `Accept: application/json`
   - `Content-Type: application/json`

当前固定 Base URL：

```text
http://8.152.222.163:8080/api/v1/db/data/v1/p8bhzq1ltutm8zr/
```

### 3.2 SiliconFlow 集成

需要支持以下 AI 能力：

1. 文本结构化解析。
2. 链接解析。
3. 视觉识别 / OCR。
4. 语音转写。

当前固定 Base URL：

```text
https://api.siliconflow.cn/v1/
```

### 3.3 模型配置要求

当前默认模型口径如下：

| 能力 | Provider | 当前模型 |
|---|---|---|
| 文本结构化解析 | SiliconFlow | `Qwen/Qwen3.5-397B-A17B` |
| 视觉识别 / OCR | SiliconFlow | `Pro/moonshotai/Kimi-K2.5` |
| 语音转写 | SiliconFlow | `FunAudioLLM/SenseVoiceSmall` |

实现要求：

1. 后端不要按 Qwen / Moonshot 官方 SDK 直连设计。
2. 所有模型请求统一通过 SiliconFlow。
3. OCR 能力应作为资料模块的基础兜底能力保留。

## 4. NocoDB 路径映射需求

当前 Web / 后端必须兼容以下路径映射：

| 业务对象 | NocoDB 路径 |
|---|---|
| `items` | `/mez4qicxcudfwnc` |
| `projects` | `/m14rejhia8w9cf7` |
| `users` | `/m1j18kc9fkjhcio` |

## 5. items 接口与字段需求

### 5.1 items 基础字段

`items` 至少需要支持并正确返回以下字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Id` | Int | 主键 |
| `ownerId` | String | 条目所属用户 |
| `title` | String | 标题 |
| `type` | String | 条目类型 |
| `summary` | String | 主摘要 |
| `content_md` | String | Markdown 正文 |
| `origin_url` | String? | 原始链接 |
| `audio_url` | String? | 音频地址 |
| `status` | String | 条目状态 |
| `read_status` | String | 阅读状态 |
| `tags` | String? | 逗号分隔字符串 |
| `project_id` | Int? | 项目外键 |
| `meta_json` | JSON / String | 结构化扩展字段 |
| `CreatedAt` | String | 创建时间 |
| `UpdatedAt` | String | 更新时间 |

### 5.2 type 枚举支持

当前必须兼容：

1. `paper`
2. `article`
3. `competition`
4. `insight`
5. `voice`

### 5.3 items 需要实现的接口能力

1. 条目列表查询。
2. 条目详情查询。
3. 条目创建。
4. 条目更新。
5. 条目删除。
6. 支持 `project_id` 关联项目。
7. 支持 `meta_json` 原样透传与结构化消费。

## 6. meta_json 结构化支持需求

这是当前最关键的实现部分。

### 6.1 paper 类型

需要支持以下字段：

- `authors`
- `conference`
- `year`
- `source`
- `identifier`
- `domain_tags`
- `keywords`
- `method_tags`
- `dedup_key`
- `summary_short`
- `summary_zh`
- `summary_en`
- `tags`
- `note`

### 6.2 article 类型

需要支持以下字段：

- `platform`
- `account_name`
- `author`
- `publish_date`
- `summary_short`
- `keywords`
- `topic_tags`
- `core_points`
- `referenced_links`
- `paper_candidates`
- `note`

其中 `paper_candidates` 需要支持以下结构：

- `url`
- `label`
- `kind`

### 6.3 competition 类型

需要支持以下字段：

- `organizer`
- `prizePool`
- `deadline`
- `theme`
- `competitionType`
- `website`
- `registrationUrl`
- `timeline`

### 6.4 insight 类型

需要支持以下字段：

- `source`
- `tags`
- `note`

### 6.5 voice 类型

需要支持以下字段：

- `duration`
- `transcription`
- `note`

## 7. meta_json 兼容性需求

Web / 后端需要同时兼容以下两种返回形式：

### 7.1 对象形式

```json
{
  "meta_json": {
    "identifier": "1706.03762",
    "year": "2017"
  }
}
```

### 7.2 字符串形式

```json
{
  "meta_json": "{\"identifier\":\"1706.03762\",\"year\":\"2017\"}"
}
```

实现要求：

1. 后端读取时要能识别这两种格式。
2. Web 展示时要统一解析成对象后再消费。
3. 不要因为 `meta_json` 是字符串就直接原样渲染。

## 8. Web 展示与消费需求

### 8.1 Paper 展示需求

列表页优先展示：

1. `title`
2. 作者
3. `conference/source + year`
4. `identifier`
5. `summary_short`
6. `note`

详情页优先展示：

1. 论文索引卡
2. `summary_short`
3. `summary_zh / summary_en`
4. `note`
5. 正文内容

### 8.2 Article 展示需求

当前资料方向需要支持：

1. 独立的 article 入口。
2. article 列表页基础结构。
3. article 详情页基础信息卡。
4. `paper_candidates` 展示。

## 9. Web 端字段消费要求

### 9.1 不要只消费 `summary`

Web 端不能只读取：

1. `title`
2. `summary`

必须优先消费结构化字段。

### 9.2 Paper 重点消费字段

必须重点支持：

1. `meta_json.identifier`
2. `meta_json.conference`
3. `meta_json.year`
4. `meta_json.domain_tags`
5. `meta_json.keywords`
6. `meta_json.method_tags`
7. `meta_json.dedup_key`
8. `meta_json.summary_short`
9. `meta_json.summary_zh`
10. `meta_json.summary_en`
11. `meta_json.note`

### 9.3 Article 重点消费字段

必须重点支持：

1. `meta_json.platform`
2. `meta_json.account_name`
3. `meta_json.author`
4. `meta_json.publish_date`
5. `meta_json.summary_short`
6. `meta_json.keywords`
7. `meta_json.topic_tags`
8. `meta_json.core_points`
9. `meta_json.referenced_links`
10. `meta_json.paper_candidates`
11. `meta_json.note`

### 9.4 机器字段与用户字段分离

语义上必须明确区分：

机器字段：

1. 索引
2. 标签
3. 候选链接
4. 短摘要

用户字段：

1. `note`

实现要求：

1. 不要把 `note` 当摘要。
2. 不要让自动生成内容覆盖用户 `note`。

## 10. 已知边界与容错需求

### 10.1 非强确定字段

以下字段允许缺失：

1. `year`
2. `keywords`
3. `method_tags`

实现要求：

1. 前端不能假设这些字段必有值。
2. 后端不能强制校验这些字段必填。

### 10.2 article 方向尚未完全收尾

当前已经有：

1. 类型定义。
2. 元数据结构。
3. 列表页骨架。
4. 详情页骨架。
5. 候选论文字段。

当前仍需继续实现：

1. 首页“最近资料”区块。
2. 候选论文交互。
3. 一键导入论文。

## 11. 当前建议的开发任务拆分

### 11.1 后端接口侧

需要实现：

1. `items / projects / users` 标准 CRUD。
2. NocoDB 请求封装层。
3. NocoDB token 注入。
4. `meta_json` 的统一解析与序列化。
5. SiliconFlow 调用封装。
6. 文本解析、OCR、语音转写任务接口。

### 11.2 Web 前端侧

需要实现：

1. `paper` 列表页。
2. `paper` 详情页。
3. `article` 列表页。
4. `article` 详情页。
5. 项目筛选或项目归属展示。
6. `meta_json` 结构化字段展示组件。
7. 候选论文展示与交互入口。

### 11.3 联调与兼容侧

需要实现：

1. 兼容 NocoDB 原始字段命名。
2. 兼容 `meta_json` 对象 / 字符串两种格式。
3. 兼容 `paper / article / competition / insight / voice` 五类数据。
4. 对空字段、缺字段做容错展示。

## 12. 优先级建议

### P0

1. 打通 `items / projects / users` 的基础读写接口。
2. 打通 `meta_json` 的统一解析能力。
3. 完成 paper 类型的列表和详情消费。
4. 完成 article 类型的基础列表和详情消费。

### P1

1. 接入 SiliconFlow 文本解析。
2. 接入 OCR。
3. 接入语音转写。
4. 展示 `paper_candidates`。

### P2

1. 首页“最近资料”区块。
2. 候选论文复制 / 打开。
3. 一键导入论文。

## 13. 验收标准

以下能力完成后，可认为本阶段需求基本达标：

1. Web 能正确读取并展示 `items` 的结构化信息，而不是只显示 `summary`。
2. `paper` 和 `article` 两类数据都能正常渲染关键字段。
3. `meta_json` 无论是对象还是字符串都能被正常解析。
4. `projects` 能用于项目归类和筛选。
5. 后端能稳定对接 NocoDB 与 SiliconFlow 两类服务。
6. 缺失字段不会导致页面报错或接口失败。

## 14. 本阶段最重要的结论

当前最应该优先实现的是：

1. `items / projects / users` 的稳定接口与字段契约。
2. `meta_json` 的 paper / article 结构化支持。
3. article 方向的基础展示与候选论文联动能力。

这三部分完成后，Web / 后端就能真正承接安卓端当前的数据能力，而不是只做一个浅层的摘要展示壳子。
