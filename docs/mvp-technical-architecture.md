# MVP 技术架构文档

## 1. 文档目标

本文档用于将当前需求落地为可执行的最小可行架构（MVP）：

- 每日定时抓取 Reddit AI 热点；
- 保证数据可追溯、可核对；
- 以静态 JSON 为数据出口，支撑轻量前端展示；
- 低成本运行在 GitHub 体系（Actions + Pages/Vercel）。

## 2. 架构概览

### 2.1 系统组件

1. **Scheduler（GitHub Actions）**
   - 文件：`.github/workflows/update-hotspots.yml`
   - 触发方式：每 6 小时定时 + 手动触发

2. **Fetcher（Python 脚本）**
   - 文件：`scripts/fetch_reddit_hotspots.py`
   - 功能：调用 Reddit `hot.json`，清洗字段，去重，排序，输出结构化数据

3. **Data Store（Git 仓库 JSON）**
   - 文件：`data/hotspots.json`
   - 功能：作为前端可直接消费的数据源与历史变更记录载体

4. **Frontend（静态站点）**
   - 部署建议：GitHub Pages 或 Vercel
   - 功能：读取 `data/hotspots.json` 渲染热点列表与源链接

### 2.2 数据流

`GitHub Actions -> fetch_reddit_hotspots.py -> data/hotspots.json -> Frontend`

更新策略：
- 每次抓取后仅在 `data/hotspots.json` 发生变化时自动 commit/push；
- 通过 Git 历史追踪每次数据变化。

## 3. 数据模型（JSON）

`data/hotspots.json` 顶层结构：

- `updated_at`: 数据更新时间（UTC ISO8601）
- `count`: 热点数量
- `items`: 热点数组

每条热点字段：

- `source`: 数据源（固定 `reddit`）
- `source_post_id`: 源帖子 ID
- `subreddit`: 所属子版块
- `title`: 标题
- `summary`: 摘要（优先正文截断，否则标题）
- `source_url`: 源帖子链接
- `author`: 作者
- `score`: 点赞分
- `num_comments`: 评论数
- `published_at`: 源发布时间（UTC ISO8601）
- `fetched_at`: 本次抓取时间（UTC ISO8601）

## 4. 关键设计决策

1. **先用 Git JSON，暂不引入数据库**
   - 优点：零额外基础设施，部署快，回滚简单；
   - 代价：不适合复杂查询和高并发写入。

2. **去重策略采用 `source_post_id` 集合**
   - 可避免跨 subreddit 重复计入同一帖子。

3. **排序策略采用 `(score, num_comments)` 降序**
   - 快速得到“热度优先”结果，满足 MVP 浏览诉求。

4. **工作流只在数据变化时提交**
   - 避免无意义提交，控制仓库噪音。

## 5. 配置项与运行参数

工作流可读取 Actions Variables：

- `REDDIT_USER_AGENT`：请求 User-Agent（推荐自定义）
- `REDDIT_SUBREDDITS`：子版块列表，逗号分隔
- `REDDIT_LIMIT`：每个 subreddit 抓取条数（默认 20）

默认子版块：
- `MachineLearning`
- `artificial`
- `LocalLLaMA`
- `AI_Agents`

## 6. 可靠性与异常处理

当前已实现：
- 请求超时（30s）与异常捕获（URLError/JSONDecodeError 等）；
- 脚本失败时 workflow fail-fast，便于告警定位；
- 数据变更检测后再 commit。

建议后续增强：
- 增加重试（指数退避）；
- 失败通知（邮件/Slack/Webhook）；
- 抓取结果指标上报（成功率、耗时、重复率）。

## 7. 安全与合规

- 使用自定义 `User-Agent`，降低匿名请求被限流风险；
- 不在仓库存储敏感密钥（当前方案无需 API key）；
- 若后续引入第三方 API，统一放入 GitHub Secrets。

## 8. 验收对照（与 README 一致）

1. **准确性**：可抽样核对 `title/published_at/source_url` 与源帖一致性。
2. **时效性**：workflow 周期性执行，JSON 定期更新。
3. **不重复**：同批次按 `source_post_id` 去重。

## 9. 演进路线

### 阶段 A（当前）
- GitHub Actions + JSON + 静态前端。

### 阶段 B
- 接入后端 API（FastAPI）与 PostgreSQL；
- 增加多源抓取（HN/X/YouTube）与统一 schema。

### 阶段 C
- 引入质量评分、主题聚类、个性化订阅与通知。

## 10. 实施清单

- [x] 定时抓取 workflow
- [x] Reddit 抓取脚本
- [x] 标准化 JSON 输出
- [x] README 部署说明
- [x] 本技术架构文档
