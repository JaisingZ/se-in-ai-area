# se-in-ai-area

项目设计文档见：

- [AI 编程热点新闻聚合站设计](docs/ai-news-aggregator-design.md)

## Reddit 热点抓取（已可用）

执行以下命令抓取 Reddit 热门帖子（默认 AI+编程相关子版块）：

```bash
python scripts/fetch_reddit_hot.py --limit 20 --output data/reddit_hot.json
```

可选参数：

- `--subreddits`：逗号分隔子版块，默认 `MachineLearning,LocalLLaMA,programming,learnprogramming,OpenAI`
- `--limit`：每个子版块抓取数量
- `--output`：输出文件路径
- `--user-agent`：自定义 User-Agent


## GitHub 自动构建（CI）

已新增自动构建流程：`.github/workflows/ci-build.yml`。

触发条件：

- push 到 `main`/`master`
- Pull Request
- 手动触发（workflow_dispatch）

流程内容：

1. 检出代码
2. 使用 Python 3.11
3. 安装依赖（如存在 `requirements.txt`）
4. 执行“构建”（`python -m compileall ingestion scripts tests`）
5. 运行测试（`python -m unittest discover -s tests -v`）

## 背景与目标

本项目用于**每天定时爬取并聚合网络上的 AI 热点信息**，当前阶段聚焦于 Reddit 热门内容，优先确保数据准确与信息可追溯。

MVP 的目标是：

- 先爬取 Reddit 上的热点信息；
- 保证聚合后的信息与源信息一致、准确；
- 提供简洁直接的热点浏览与预览体验。

## 用户与核心场景

### 目标用户

- 我自己（项目维护者）；
- 其他持续关注 AI 领域变化的开发者。

### 核心场景

- 每天查看当日 AI 热点，快速了解社区讨论重点；
- 点击热点后可追溯到原始来源，完成准确性核对；
- 在尽量少交互步骤下完成“发现热点 -> 预览摘要 -> 访问原帖”。

## MVP 功能范围

### In Scope（本期范围）

- 热点可预览（标题、摘要、来源链接、时间）；
- 热点可接入（来源内容可被抓取并落库/展示）；
- 数据需准确（聚合信息与源地址语义一致）。

### Out of Scope（暂不纳入）

- 多热点源爬取（如 Hacker News、X、YouTube 等）——后期实现；
- 复杂个性化推荐与排序策略；
- 多语言内容翻译与重写。

## 验收标准（可测试）

1. **信息准确性验证**
   - 从聚合结果中随机抽样热点；
   - 对照热点源地址（Reddit 原帖）逐条核对标题、发布时间、核心语义；
   - 判定标准：聚合信息与源信息一致，不出现关键事实错误。

2. **时效与更新验证**
   - 确认每天有热点被爬取并更新到网站上；
   - 新抓取内容按时间轴排序展示（由新到旧或由旧到新，需固定一致）；
   - 判定标准：同一热点在同一时间窗口内不重复展示。

## 里程碑与优先级

### P0（最高优先级）

- 热点爬取（定时任务 + Reddit 数据拉取）；
- 热点识别与聚合（去重、结构化、落库）；
- 基础准确性校验（源链接可追溯、字段一致）。

### P1

- 热点展示效果优化（列表可读性、预览信息层次、跳转体验）；
- 前端交互简化（更少点击完成信息消费）。

## 风险与假设

### 关键假设

- Reddit 热点能够代表当日 AI 领域较高价值讨论；
- Reddit 源数据可稳定获取并满足准确性比对需求；
- 聚合流程不会引入显著语义偏差。

### 风险点

- Reddit 接口或页面结构变化导致抓取失败；
- 热点原帖删除/编辑导致比对结果波动；
- 摘要生成或字段映射错误导致语义偏差。

### 验证方式

- 保留每条聚合信息的源数据 URL；
- 通过“数据源 URL 与聚合后信息”的语义比对，确认无差异；
- 建立抽样核查记录（每天/每周）并统计准确率、重复率与抓取成功率。

---

## 技术架构文档

- MVP 技术架构：`docs/mvp-technical-architecture.md`


## 部署（基于 GitHub）

该方案适合当前 MVP：

- 使用 **GitHub Actions** 定时抓取 Reddit 热点；
- 将结果写入仓库中的 `data/hotspots.json`；
- 前端（GitHub Pages / Vercel）直接读取该 JSON 做展示。

### 已提供内容

- 定时任务：`.github/workflows/update-hotspots.yml`（每 6 小时执行一次）
- 抓取脚本：`scripts/fetch_reddit_hotspots.py`
- 数据文件：`data/hotspots.json`

### 启用步骤

1. 推送仓库到 GitHub。
2. 打开仓库 **Settings -> Actions -> General**，确认允许 Workflow 读写仓库内容。
3. （可选）在 **Settings -> Secrets and variables -> Actions -> Variables** 配置：
   - `REDDIT_USER_AGENT`（建议自定义，便于限流与追踪）
   - `REDDIT_SUBREDDITS`（如 `MachineLearning,artificial,LocalLLaMA,AI_Agents`）
   - `REDDIT_LIMIT`（每个 subreddit 抓取条数，默认 20）
4. 在 Actions 页面手动执行一次 `Update Reddit hotspots`，确认 `data/hotspots.json` 被更新。
5. 前端部署时读取 `data/hotspots.json`（静态文件）并按字段渲染列表。

### 注意事项

- 该方案没有独立数据库，适合轻量 MVP；
- Git 历史会保留每次 JSON 变更，便于回溯；
- 后续若需要更高稳定性与查询能力，可迁移到“后端 API + DB + Worker”架构。

