---
name: geektime-article-summarizer
description: Use when extracting or summarizing already-logged-in Geekbang article pages on time.geekbang.org from a URL or the current tab, including title,正文,评论区, or moving to the next article in the column.
---

# Geekbang Article Summarizer

## Overview

Use the current logged-in Chrome session. Accept either a Geekbang article URL or the current selected Geekbang tab. Prefer the page DOM or accessibility snapshot first. If the visible page is incomplete, fall back to same-origin page data from the article and comment APIs.

## Quick Workflow

1. If the user gave a URL, open it in the same logged-in session.
2. If no URL is given, use the current selected Geekbang tab.
3. Confirm the page is on `time.geekbang.org` and logged in.
4. Use `take_snapshot` to read the title, outline,正文, and visible comments.
5. If正文或评论区被折叠、截断或延迟加载，use `evaluate_script` in the same session.
6. For article metadata, use `/serv/v1/article`.
7. For the column order and adjacent article IDs, use `/serv/v1/column/articles`.
8. For comments, use `/serv/v4/comment/list` when the visible thread is incomplete.

## Retrieval Pattern

```js
await fetch('/serv/v1/article', {
  method: 'POST',
  credentials: 'include',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ id, include_neighbors: true, is_freelyread: true })
})
```

Use the returned `article_title`, `article_content`, `article_summary`, `neighbors`, and comment data to build the summary.

## Output Format

- 标题
- 正文核心论点
- 结构化要点
- 评论区高频观点 / 争议点
- 可选：上一篇 / 下一篇
- 默认不贴长段原文，只保留必要短引述

## Guardrails

- Do not paste long verbatim passages.
- Do not use public web search for this task.
- If the page is not logged in or not on `time.geekbang.org`, say so and stop.
- Keep summaries high-density and aimed at experienced developers.
- If the user asked for full text, provide the best extractable正文 plus a compact summary, not a literal mirror of the page.

## Common Mistakes

- Relying only on visible DOM when the article body is partially loaded.
- Ignoring the column API when asked for the next article.
- Mixing正文、评论和个人解读 without clear section labels.
- Returning too much raw text instead of a compact summary.
