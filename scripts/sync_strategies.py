#!/usr/bin/env python3
"""
从 Strategy-Lib 同步策略到博客：每个策略 = 一篇 Hugo Page Bundle。

源：/Volumes/ai/github/Strategy-Lib/{ideas,summaries}/Sn_<slug>/vN/
目标：content/posts/strategies/Sn_<slug>/{index.md, *.png}

运行：python scripts/sync_strategies.py
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STRATEGY_LIB = Path("/Volumes/ai/github/Strategy-Lib")
IDEAS_DIR = STRATEGY_LIB / "ideas"
SUMMARIES_DIR = STRATEGY_LIB / "summaries"
OUTPUT_DIR = REPO_ROOT / "content" / "posts" / "strategies"

# 不同步的策略目录名
SKIP = {"_template", "README.md"}


@dataclass
class Frontmatter:
    fields: dict[str, str | list[str]]
    body: str


def parse_frontmatter(text: str) -> Frontmatter:
    """解析 markdown 顶部 YAML frontmatter，返回 (字段 dict, body)。"""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return Frontmatter({}, text)

    raw, body = m.group(1), m.group(2)
    fields: dict[str, str | list[str]] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            items = [s.strip().strip("'\"") for s in val[1:-1].split(",") if s.strip()]
            fields[key] = items
        else:
            fields[key] = val
    return Frontmatter(fields, body)


def find_latest_version(strategy_dir: Path) -> Path | None:
    """在 Sn_<slug>/ 下找版本号最大的 vN 目录。"""
    versions = sorted(
        (p for p in strategy_dir.iterdir() if p.is_dir() and re.match(r"^v\d+$", p.name)),
        key=lambda p: int(p.name[1:]),
    )
    return versions[-1] if versions else None


def extract_section(body: str, heading: str) -> str:
    """从 markdown body 抽取 `## heading` 直到下一个 `## ` 之间的内容（不含标题）。"""
    pattern = rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)"
    m = re.search(pattern, body, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip().lstrip(">").strip()
        if line and not line.startswith("#"):
            return line
    return ""


def build_post(strategy_id: str, idea_dir: Path, summary_dir: Path) -> tuple[str, list[Path]]:
    """生成 index.md 内容，返回 (markdown, [需拷贝的 artifact 路径])。"""
    idea = parse_frontmatter((idea_dir / "idea.md").read_text(encoding="utf-8"))
    conclusion_path = summary_dir / "conclusion.md"
    conclusion = parse_frontmatter(conclusion_path.read_text(encoding="utf-8"))
    impl_text = (summary_dir / "implementation.md").read_text(encoding="utf-8") if (summary_dir / "implementation.md").exists() else ""
    valid_text = (summary_dir / "validation.md").read_text(encoding="utf-8") if (summary_dir / "validation.md").exists() else ""

    title_raw = idea.fields.get("title") or strategy_id
    title = title_raw if isinstance(title_raw, str) else " ".join(title_raw)
    status = conclusion.fields.get("status") or idea.fields.get("status") or "unknown"
    created = idea.fields.get("created") or "2026-01-01"
    finalized = conclusion.fields.get("finalized") or "TBD"

    idea_tags = idea.fields.get("tags") or []
    tags = ["策略复盘"] + ([idea_tags] if isinstance(idea_tags, str) else idea_tags)

    # 摘要：取 conclusion 的"一句话结论"段落首句
    one_liner_section = extract_section(conclusion.body, "一句话结论")
    summary_line = first_nonempty_line(one_liner_section) or first_nonempty_line(idea.body)
    summary_line = summary_line.replace('"', "'")[:280]

    # 抽取 idea 的关键段落
    idea_one = extract_section(idea.body, "一句话概括")
    idea_what = extract_section(idea.body, "核心逻辑（What）")
    idea_why = extract_section(idea.body, "假设与依据（Why）")
    idea_universe = extract_section(idea.body, "标的与周期")

    # 抽取 conclusion 的关键段落
    concl_one = one_liner_section
    concl_data = extract_section(conclusion.body, "关键数据")
    concl_when = extract_section(conclusion.body, "在什么情况下有效，什么情况下失效")
    if not concl_when:
        concl_when = extract_section(conclusion.body, "在什么情况下有效")
    concl_lesson = extract_section(conclusion.body, "这个策略教会我什么（可迁移的经验）")
    if not concl_lesson:
        concl_lesson = extract_section(conclusion.body, "这个策略教会我什么")

    # 拷贝 artifacts 图片，按拼盘顺序生成 markdown 引用
    artifacts_dir = summary_dir / "artifacts"
    image_files: list[Path] = []
    image_md = ""
    if artifacts_dir.exists():
        # 偏好顺序：净值/回撤/权重/现金/分布等等，剩下的按字典序补
        preferred = ["equity_curve", "drawdown", "cash_vs_risk", "weights_stack"]
        all_imgs = sorted(p for p in artifacts_dir.glob("*.png"))
        ordered: list[Path] = []
        for key in preferred:
            for p in all_imgs:
                if key in p.stem and p not in ordered:
                    ordered.append(p)
        for p in all_imgs:
            if p not in ordered:
                ordered.append(p)
        image_files = ordered
        image_md = "\n\n".join(f"![{p.stem}]({p.name})" for p in image_files)

    # 折叠区块的内容（去掉自带 frontmatter）
    impl_body = parse_frontmatter(impl_text).body.strip() if impl_text else ""
    valid_body = parse_frontmatter(valid_text).body.strip() if valid_text else ""

    fm_lines = [
        "---",
        f'title: "{title}"',
        f"date: {created}T09:00:00+08:00",
        "draft: false",
        f'summary: "{summary_line}"',
        f"tags: {tags}",
        'categories: ["策略复盘"]',
        "ShowToc: true",
        "TocOpen: false",
        "---",
    ]

    parts = ["\n".join(fm_lines), ""]
    parts.append(f"> **状态**：`{status}` · **最终化**：`{finalized}`  ")
    parts.append(f"> 来源：`Strategy-Lib/ideas/{strategy_id}/{idea_dir.name}` + `Strategy-Lib/summaries/{strategy_id}/{summary_dir.name}`")
    parts.append("")

    if idea_one:
        parts.append("## 想法（Why）")
        parts.append("")
        parts.append("**一句话概括**")
        parts.append("")
        parts.append(idea_one)
        if idea_what:
            parts.append("")
            parts.append("**核心逻辑**")
            parts.append("")
            parts.append(idea_what)
        if idea_why:
            parts.append("")
            parts.append("**假设与依据**")
            parts.append("")
            parts.append(idea_why)
        if idea_universe:
            parts.append("")
            parts.append("**标的与周期**")
            parts.append("")
            parts.append(idea_universe)
        parts.append("")

    if concl_one:
        parts.append("## 一句话结论")
        parts.append("")
        parts.append(concl_one)
        parts.append("")

    if concl_data:
        parts.append("## 关键数据")
        parts.append("")
        parts.append(concl_data)
        parts.append("")

    if concl_when:
        parts.append("## 在什么情况下有效，什么情况下失效")
        parts.append("")
        parts.append(concl_when)
        parts.append("")

    if concl_lesson:
        parts.append("## 这个策略教会我什么")
        parts.append("")
        parts.append(concl_lesson)
        parts.append("")

    if image_md:
        parts.append("## 关键图表")
        parts.append("")
        parts.append(image_md)
        parts.append("")

    if impl_body:
        parts.append("## 实现要点")
        parts.append("")
        parts.append("<details>")
        parts.append("<summary>展开完整实现记录</summary>")
        parts.append("")
        parts.append(impl_body)
        parts.append("")
        parts.append("</details>")
        parts.append("")

    if valid_body:
        parts.append("## 验证过程")
        parts.append("")
        parts.append("<details>")
        parts.append("<summary>展开完整验证记录</summary>")
        parts.append("")
        parts.append(valid_body)
        parts.append("")
        parts.append("</details>")
        parts.append("")

    parts.append("---")
    parts.append("")
    parts.append("*本文由 [`scripts/sync_strategies.py`](https://github.com/lizhao903/0xBroleez/blob/main/scripts/sync_strategies.py) 从 Strategy-Lib 同步生成。*")
    parts.append("")

    return "\n".join(parts), image_files


def sync() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SUMMARIES_DIR.exists():
        raise SystemExit(f"未找到 {SUMMARIES_DIR}")

    synced = []
    skipped = []
    for strategy_path in sorted(SUMMARIES_DIR.iterdir()):
        if not strategy_path.is_dir() or strategy_path.name in SKIP:
            continue
        strategy_id = strategy_path.name

        summary_v = find_latest_version(strategy_path)
        if not summary_v or not (summary_v / "conclusion.md").exists():
            skipped.append(f"{strategy_id} — summaries 没有 conclusion.md")
            continue

        idea_strategy_dir = IDEAS_DIR / strategy_id
        idea_v = find_latest_version(idea_strategy_dir) if idea_strategy_dir.exists() else None
        if not idea_v or not (idea_v / "idea.md").exists():
            skipped.append(f"{strategy_id} — ideas 没有 idea.md")
            continue

        post_dir = OUTPUT_DIR / strategy_id
        post_dir.mkdir(parents=True, exist_ok=True)

        # 清空旧图片（保留可能的手工添加文件不在范围内）
        for old_png in post_dir.glob("*.png"):
            old_png.unlink()

        index_md, images = build_post(strategy_id, idea_v, summary_v)
        (post_dir / "index.md").write_text(index_md, encoding="utf-8")

        for img in images:
            shutil.copy2(img, post_dir / img.name)

        synced.append(f"{strategy_id} ({idea_v.name}, {len(images)} 张图)")

    print("=" * 60)
    print(f"已同步 {len(synced)} 个策略：")
    for s in synced:
        print(f"  ✓ {s}")
    if skipped:
        print(f"\n跳过 {len(skipped)} 个：")
        for s in skipped:
            print(f"  · {s}")


if __name__ == "__main__":
    sync()
