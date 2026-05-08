---
title: "跑步"
url: "/running/"
description: "跑步训练、比赛、装备、复盘的记录。"
ShowToc: false
hideMeta: true
---

跑步相关的全部内容都在这里 — 训练日志、比赛复盘、装备评测、伤病/恢复笔记。

## 怎么写新一篇跑步文章

在 `content/running/` 下建文件夹（推荐 `YYYY-MM-DD-标题`）：

```
content/running/
└── 2026-05-15-周末长距离/
    ├── index.md          # 正文
    ├── 路线图.png        # 同目录引用 ![](路线图.png)
    └── 心率曲线.png
```

`index.md` frontmatter 模板：

```yaml
---
title: "周末 15K 长距离"
date: 2026-05-15T19:00:00+08:00
draft: false
summary: "测试新鞋子 + 配速控制。"
tags: ["训练", "长距离"]
categories: ["跑步"]
---
```

写完 `git push`，约 1 分钟后线上可见。
