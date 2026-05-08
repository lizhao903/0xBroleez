# 0xBroleez 的博客

> 用 Hugo + GitHub Pages 搭建的个人博客，记录项目实施的思考与实践。

**线上地址**：<https://lizhao903.github.io/0xBroleez/>

---

## 目录结构

```
.
├── content/
│   └── posts/                          ← 所有文章在这里
│       └── 2026-05-08-博客搭建过程/      ← 一篇文章 = 一个文件夹（Page Bundle）
│           ├── index.md                ← 正文
│           ├── 架构图.png               ← 文章引用的图片放在同目录
│           └── 流程图.png
├── archetypes/
│   └── default.md                      ← `hugo new` 用的模板
├── static/                             ← 全站共用的静态资源（favicon 等）
├── themes/PaperMod/                    ← 主题（git submodule）
├── hugo.toml                           ← 站点配置
└── .github/workflows/deploy.yml        ← 自动部署到 GitHub Pages
```

---

## 写一篇新文章

### 方法一：命令行（推荐）

```bash
hugo new posts/2026-05-15-我的项目复盘/index.md
```

会自动用 `archetypes/default.md` 生成 frontmatter，文章状态默认是 `draft: true`，发布前改成 `false`。

### 方法二：手动建文件夹

1. 在 `content/posts/` 下新建文件夹，命名建议 `YYYY-MM-DD-标题`
2. 文件夹里建 `index.md`
3. 头部加 frontmatter（参考已有文章）

---

## 在文章里插入图片

**约定**：图片放在与 `index.md` 相同的文件夹。

```markdown
![架构总览](架构图.png)
```

这种相对路径写法 **同时被 Obsidian 和 Hugo 正确解析**，本地预览和发布后的网页表现一致。

> 不要用绝对路径或 `/static/...` 引用文章配图。`/static/` 留给全站共用资源（favicon、社交分享图等）。

---

## 与 Obsidian 协作

推荐用法：**按需打开单篇文章的文件夹作为 Obsidian vault**，不要把整个仓库当 vault。

```
File → Open folder as vault → 选择 content/posts/2026-05-15-我的项目复盘/
```

好处：

- 写作时不被其他文章分心
- 拖图片到 Obsidian 会自动保存到当前目录，符合本仓库约定
- Obsidian 的预览效果和 Hugo 渲染基本一致

---

## 本地预览

```bash
hugo server -D       # -D 表示包含 draft 文章
```

访问 <http://localhost:1313/0xBroleez/>。

> 注意 baseURL 包含子路径 `/0xBroleez/`，本地预览也要带上。

---

## 发布

```bash
git add .
git commit -m "post: 我的项目复盘"
git push origin main
```

push 到 main 分支后，GitHub Actions 自动构建并部署，约 1 分钟后线上可见。

可以在 GitHub 仓库的 Actions 页面查看构建状态。

---

## 首次部署前的一次性配置

仓库需要在 GitHub 网页上启用 Pages：

1. 仓库 → Settings → Pages
2. **Source** 选 `GitHub Actions`（**不是** Deploy from a branch）
3. 保存

之后每次 push 都会自动部署，不需要再动这里。

---

## Frontmatter 字段速查

```yaml
---
title: "文章标题"                # 必填
date: 2026-05-08T11:00:00+08:00  # 必填，发布日期
draft: false                     # true=草稿，不会发布
summary: "首页/列表页显示的摘要"  # 建议填，否则用正文开头
tags: ["标签1", "标签2"]
categories: ["分类"]
ShowToc: true                    # 是否显示目录
TocOpen: false                   # 目录默认是否展开
cover:
    image: "封面图.png"            # 留空表示无封面
    relative: true               # 相对当前文章目录
    hidden: true                 # 列表页隐藏封面
---
```

---

## 常见问题

**Q: 改了文章怎么不更新？**
A: GitHub Pages 有 CDN 缓存，强制刷新（Cmd+Shift+R）通常能看到最新版本。如果还不行，去 Actions 页面确认部署成功。

**Q: 图片显示不出来？**
A: 检查图片是否真的和 `index.md` 在同一目录，文件名大小写是否一致（macOS 不敏感、Linux 敏感）。

**Q: 想换主题？**
A: 把 `hugo.toml` 里的 `theme = "PaperMod"` 改掉，并在 `themes/` 下添加新主题（推荐用 git submodule）。

---

## 主题更新

```bash
git submodule update --remote --merge themes/PaperMod
git add themes/PaperMod
git commit -m "chore: bump PaperMod"
```

---

## 从 Strategy-Lib 同步策略复盘

`/Volumes/ai/github/Strategy-Lib` 是策略研发的单一真相源。每个策略（`Sn_<slug>`）的 `ideas/` + `summaries/` 内容会被合并成博客里的一篇文章。

**同步**：

```bash
python3 scripts/sync_strategies.py
```

脚本会做：

1. 扫描 `Strategy-Lib/summaries/Sn_*/`，对每个策略找最新版本（`v1`、`v2` 中最大编号）
2. 读取该版本的 `idea.md` + `conclusion.md`（必需）和 `implementation.md` + `validation.md`（可选）
3. 抽取关键段落（一句话概括 / 核心逻辑 / 假设依据 / 关键数据 / 教会我什么 / 图表）合并为单篇
4. 长内容（`implementation.md` / `validation.md` 全文）放到 `<details>` 折叠
5. 生成 `content/posts/strategies/Sn_<slug>/index.md`，并把 `artifacts/*.png` 拷贝到同目录

**写作约定**：

- 在 `Strategy-Lib` 里写源文件（idea / implementation / validation / conclusion）
- 提交到 Strategy-Lib 后，回这里跑一次同步脚本
- `git add content/posts/strategies/ && git commit && git push` 触发部署

**修改了哪个文件需要重新同步？**

| 改动 | 需要同步 |
|---|---|
| `ideas/Sn_xxx/vN/idea.md` | ✓ |
| `summaries/Sn_xxx/vN/conclusion.md` | ✓ |
| `summaries/Sn_xxx/vN/implementation.md` | ✓ |
| `summaries/Sn_xxx/vN/validation.md` | ✓ |
| `summaries/Sn_xxx/vN/artifacts/*.png` | ✓ |
| `ideas/Sn_xxx/vN/notes.md` | ✗（脚本不读 notes） |

**新增策略**：在 `Strategy-Lib` 里按 `Sn_<slug>/vN/` 结构建好文件，跑一次脚本即可，无需改博客代码。

**临时不同步某个策略**：在该策略的 `summaries/Sn_*/vN/conclusion.md` 改名或删除，脚本会跳过。
