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
