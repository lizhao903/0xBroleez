---
title: "用 Hugo + GitHub Pages 搭建个人博客的过程复盘"
date: 2026-05-08T11:00:00+08:00
draft: false
summary: "记录从空仓库到上线第一篇博客的完整过程：技术选型、目录设计、与 Obsidian 写作流的衔接，以及 GitHub Actions 自动部署。"
tags: ["博客", "Hugo", "GitHub Pages", "Obsidian"]
categories: ["复盘"]
ShowToc: true
TocOpen: true
cover:
    image: ""
    alt: ""
    caption: ""
    relative: true
    hidden: true
---

## 为什么写这篇

这是这个站点的第一篇文章。本身也是一次完整的「项目实施」——选型、动手、复盘——所以适合作为示范，把这套流程的形态固定下来。

## 选型上的几个关键判断

### 为什么不是 Notion / 语雀

托管型工具的写作体验不错，但有两个硬伤：

1. **数据不在自己手里**。文章是 markdown 文件，本来就该是可移植的纯文本。
2. **无法版本化**。`git log` 是博客最自然的修订史。

### 为什么不是 Quartz / Obsidian Publish

我的 Obsidian 用法是「散点笔记」，里面 80% 的内容并不打算公开。如果直接发布整个 vault，需要花精力做可见性管理。把博客和笔记本物理隔开，反而更省心：

- **Obsidian** 留给自己看的散点笔记
- **博客仓库** 是经过整理、明确要发布的内容

### 为什么是 Hugo + PaperMod

| 维度 | 选择理由 |
|---|---|
| 构建速度 | Go 写的，毫秒级，写得多了不会退化 |
| 中文社区 | 中文文档完整，主题选择多 |
| 部署 | GitHub Actions 一键搞定，免费 |
| 写作 | 标准 markdown，无任何专有语法 |
| 图片 | Page Bundle 模式支持文章+图片同目录 |

PaperMod 是技术博客最常见的主题之一：暗色模式、首页时间线、标签、归档、搜索都开箱即用。

## 目录设计的取舍

最关键的决定是：**每篇文章是一个文件夹**（Hugo 称之为 Page Bundle）。

```
content/posts/
└── 2026-05-08-博客搭建过程/
    ├── index.md          ← 正文
    ├── 架构图.png         ← 同目录引用
    └── 部署流程.png
```

这样做的好处：

- 一篇文章的所有资源（图片、附件、子页面）都在自己的目录里，**移动/删除文章不会留下孤儿图片**
- Markdown 里直接用 `![](架构图.png)` 引用，**Obsidian 和 Hugo 都能正确解析**
- 在 Obsidian 里把这个文件夹当作 vault 打开，所见即所得

## 与 Obsidian 的衔接方式

我没有把整个仓库当 vault，而是**按需**把要写的那一篇文章的目录用 Obsidian 打开。这样：

- 写作时在 Obsidian 里专注一篇
- 图片直接拖进 Obsidian，会保存到当前目录
- 写完 commit、push，GitHub Actions 自动部署

## 部署链路

```
本地写作 (Obsidian/任意编辑器)
   │
   ▼
git commit + git push origin main
   │
   ▼
GitHub Actions: hugo --minify
   │
   ▼
GitHub Pages: lizhao903.github.io/0xBroleez/
```

整个链路无人工介入，从 push 到上线大约 1 分钟。

## 接下来想做什么

- [ ] 写第二篇真正的项目复盘
- [ ] 配置评论系统（giscus 用 GitHub Discussions 当后端，零运维）
- [ ] 加个统计：访问量、阅读时长

## 小结

技术决策的关键不是「哪个最先进」，而是「哪个最匹配我的工作流」。对我来说：
- 我用 Obsidian 写 markdown → 就用支持 page bundle 的框架
- 我代码托管在 GitHub → 就用 GitHub Pages
- 我想专注写作不想运维 → 就让 Actions 自动部署

每个决策都顺着已有习惯走，阻力最小。
