---
title: "图集"
url: "/gallery/"
description: "按主题分组的图片相册。"
ShowToc: false
hideMeta: true
---

## 怎么新建一个图集

在 `content/gallery/` 下建一个文件夹，把图片直接放进去，加一个 `index.md` 写标题：

```
content/gallery/
└── 2026-05-15-周末跑步路线/
    ├── index.md
    ├── photo1.jpg       # 不需要在 markdown 里手动引用
    ├── photo2.jpg       # 文件夹里的所有图片自动按文件名排序展示
    ├── photo3.jpg
    └── ...
```

`index.md` 模板：

```yaml
---
title: "周末跑步路线"
date: 2026-05-15T08:00:00+08:00
summary: "10K 江边路线，4 张图。"
---

可以在这里写一段说明文字（可选）。下面会自动把同目录的图片按文件名排序展示成网格，点图片可在新窗口看原图。
```

> 不需要写任何 `![](...)`，模板会自动扫描同目录的图片资源（jpg/jpeg/png/gif/webp）。
