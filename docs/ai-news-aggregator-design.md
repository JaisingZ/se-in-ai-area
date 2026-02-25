# AI 编程热点新闻聚合站：方案设计

## 1. 项目目标

构建一个“每日自动更新”的 AI 新闻聚合站，重点覆盖 **AI + 编程/软件工程** 方向，解决以下问题：

- 信息分散：用户要在多个平台来回切换。
- 时效不稳定：缺少固定节奏、结构化的日报/快报。
- 噪音高：营销内容多、技术含量参差。

### 1.1 核心输出

- 首页：当天热点（按“技术价值 + 热度 + 时效”综合排序）。
- 专题页：如 LLM 工程、AI 编程工具、Agent、模型发布、开源项目。
- 日报页：每天固定生成一份摘要（可邮件/Telegram/微信订阅）。
- 趋势页：7 天/30 天关键词与来源趋势。

## 2. MVP 范围（建议 3~4 周）

### 2.1 必做功能

1. **多源抓取（10~20 个高价值源）**
   - 官方博客：OpenAI、Anthropic、Google AI、Meta AI 等。
   - 技术社区：Hacker News、Reddit（MachineLearning / LocalLLaMA / programming）、Dev.to。
   - 开源平台：GitHub Trending（AI、LLM、Agent、Copilot 等关键词）。
   - 中文源：掘金、InfoQ、机器之心（优先有清晰版权与转载规则的来源）。

2. **统一内容模型 + 去重**
   - 将 RSS、HTML、API 返回统一为 `Article` 结构。
   - 用 `URL canonical + 标题向量相似度 + 时间窗口` 做去重。

3. **自动打标签与打分**
   - 标签：模型发布、AI 编程工具、Agent 框架、工程实践、评测对比等。
   - 打分：新鲜度、互动热度、来源权重、技术密度、与“编程”相关性。

4. **网站展示**
   - 热点流 + 标签筛选 + 搜索。
   - 每条内容有“原文链接 + 自动摘要 + 为什么值得看”。

5. **每日定时任务**
   - 每天多轮抓取（如每 2 小时一次）。
   - 每晚生成“今日 AI 编程热点日报”。

### 2.2 暂不做（后续迭代）

- 用户登录、个性化推荐。
- 复杂评论系统。
- 移动端 App（先做响应式 Web）。

## 3. 技术架构建议

## 3.1 架构分层

1. **采集层（Ingestion）**
   - RSS 拉取器（最稳）
   - 网页爬虫（Playwright/Requests + Readability）
   - 平台 API 采集器（GitHub/Reddit/HN 等）

2. **处理层（Processing）**
   - 清洗：正文抽取、语言识别、发布时间标准化。
   - 去重：规则 + 向量（标题/摘要 embedding）。
   - NLP：分类、关键词提取、摘要、质量评分。

3. **存储与检索层（Storage）**
   - PostgreSQL：主数据（文章、来源、标签、分数、任务状态）。
   - Redis：任务队列/缓存。
   - 可选 OpenSearch/Meilisearch：全文检索与快速筛选。

4. **应用层（App/API）**
   - 后端 API：FastAPI / NestJS 均可。
   - 前端：Next.js（SSR + SEO 更好）。
   - 后台管理：来源管理、抓取状态监控、人工置顶与纠错。

5. **调度与运维层**
   - 调度：Celery Beat / APScheduler / GitHub Actions Cron。
   - 监控：Sentry（异常）、Prometheus + Grafana（任务成功率、时延）。

## 3.2 推荐技术栈（实用优先）

- 后端：Python + FastAPI（便于爬虫/NLP/LLM 集成）。
- 异步任务：Celery + Redis。
- 数据库：PostgreSQL。
- 前端：Next.js + Tailwind。
- 部署：Docker Compose 起步，后续可迁移到 K8s。

## 4. 数据模型（核心表）

### 4.1 `sources`

- `id`
- `name`
- `type`（rss / api / crawler）
- `url`
- `language`
- `weight`（来源可信度权重）
- `crawl_interval_minutes`
- `status`

### 4.2 `articles`

- `id`
- `source_id`
- `title`
- `canonical_url`
- `author`
- `published_at`
- `content_raw`
- `content_clean`
- `summary`
- `language`
- `hot_score`
- `quality_score`
- `programming_relevance_score`
- `is_duplicate`
- `duplicate_of`
- `created_at`

### 4.3 `tags` / `article_tags`

- 标签建议：`模型发布`、`AI编程助手`、`Agent工程`、`RAG`、`评测`、`开源项目`、`教程实战`

### 4.4 `daily_digest`

- `date`
- `top_articles`（json）
- `highlights`
- `generated_by`（规则 / LLM）

## 5. 热点评分策略（可迭代）

给每条文章计算总分：

`hot_score = 0.35*recency + 0.25*engagement + 0.2*source_weight + 0.2*programming_relevance`

- `recency`：发布时间越近分越高。
- `engagement`：点赞/评论/转发/HN points/GitHub stars 增速。
- `source_weight`：来源可信度与历史质量。
- `programming_relevance`：是否涉及代码、SDK、框架、工程实践。

> 先用规则评分，数据积累后可升级为学习排序（Learning to Rank）。

## 6. 抓取与处理流程（每日自动化）

1. 调度器触发采集任务。
2. 各采集器拉取增量内容。
3. 清洗正文并标准化字段。
4. 去重与近重复聚类。
5. 打标签、摘要、计算评分。
6. 入库并更新索引。
7. 生成日报（top N + 重点摘要）。
8. 缓存刷新并前端可见。

## 7. 质量与合规设计

- 仅聚合摘要 + 跳转原文，避免全文转载侵权。
- 对来源站点遵守 `robots.txt` 与访问频率限制。
- 为每条内容保留 `source_url` 与抓取时间，支持溯源。
- 增加人工审核入口（删除侵权/低质内容）。

## 8. 迭代路线图

### Phase 1（MVP，0~1 月）

- 完成 10~20 来源接入。
- 完成去重、标签、基础评分。
- 上线首页 + 标签页 + 日报页。

### Phase 2（1~2 月）

- 引入搜索与高级筛选。
- 增加“为什么上榜”解释模块（可解释推荐）。
- 接入邮件/Telegram 订阅。

### Phase 3（2~3 月）

- 用户个性化兴趣画像。
- 增加“开发者工具榜单”（周榜/月榜）。
- 引入多语言（中英）聚合与翻译摘要。

## 9. 你可以立刻开始的落地清单

1. 初始化项目结构：`api/`、`worker/`、`web/`、`infra/`。
2. 先接入 5 个稳定 RSS 源，跑通全链路。
3. 建立 `articles`、`sources`、`tags` 三张核心表。
4. 做一个最小首页：列表 + 标签 + 原文跳转。
5. 加一个每日 21:00 生成日报的定时任务。

---

如果你愿意，我下一步可以直接给你一版：

- **目录结构模板**（含 FastAPI + Celery + Next.js），
- **数据库建表 SQL**，
- **首批 20 个推荐信源清单**（中英文分组），
- 以及 **MVP 的两周开发计划**。
