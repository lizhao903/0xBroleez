#!/usr/bin/env python3
"""
从 Strategy-Lib 同步策略到博客：每个 (策略, 版本) = 一篇 Hugo Page Bundle。

源：/Volumes/ai/github/Strategy-Lib/{ideas,summaries}/Sn_<slug>/vN/
目标：content/posts/strategies/Sn_<slug>_vN/{index.md, *.png}

每篇文章顶部会自动生成「本策略其他版本」的链接区块，把 v1/v2/v3 串起来。

只生成 summaries 里有 conclusion.md 的版本（v2 work-in-progress 没结论时不发布）。

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

SKIP = {"_template", "README.md"}


@dataclass
class Frontmatter:
    fields: dict[str, str | list[str]]
    body: str


@dataclass
class VersionEntry:
    """一个 (策略, 版本) 的全部源信息。"""

    strategy_id: str   # e.g. S1_cn_etf_dca_basic
    version: str       # e.g. v1
    idea_dir: Path
    summary_dir: Path
    title: str
    one_liner: str     # 一句话结论
    status: str
    created: str       # YYYY-MM-DD


def parse_frontmatter(text: str) -> Frontmatter:
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return Frontmatter({}, text)
    raw, body = m.group(1), m.group(2)
    fields: dict[str, str | list[str]] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        # 去掉 YAML 行内注释（# 之后的部分），但要避免误伤引号里的 #
        val = val.strip()
        if val and not (val.startswith('"') or val.startswith("'") or val.startswith("[")):
            hash_pos = val.find(" #")
            if hash_pos == -1 and val.startswith("#"):
                hash_pos = 0
            if hash_pos != -1:
                val = val[:hash_pos].rstrip()
        if val.startswith("[") and val.endswith("]"):
            items = [s.strip().strip("'\"") for s in val[1:-1].split(",") if s.strip()]
            fields[key] = items
        else:
            fields[key] = val.strip("'\"")
    return Frontmatter(fields, body)


def list_versions(strategy_dir: Path) -> list[Path]:
    """按版本号升序列出所有 vN 目录。"""
    return sorted(
        (p for p in strategy_dir.iterdir() if p.is_dir() and re.match(r"^v\d+$", p.name)),
        key=lambda p: int(p.name[1:]),
    )


def extract_section(body: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)"
    m = re.search(pattern, body, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip().lstrip(">").strip()
        if line and not line.startswith("#"):
            return line
    return ""


def collect_versions() -> list[VersionEntry]:
    """扫描 Strategy-Lib，返回所有可发布的 (策略, 版本) 条目。"""
    if not SUMMARIES_DIR.exists():
        raise SystemExit(f"未找到 {SUMMARIES_DIR}")

    entries: list[VersionEntry] = []
    skipped: list[str] = []

    for strategy_path in sorted(SUMMARIES_DIR.iterdir()):
        if not strategy_path.is_dir() or strategy_path.name in SKIP:
            continue
        strategy_id = strategy_path.name

        for summary_v in list_versions(strategy_path):
            version = summary_v.name
            conclusion_path = summary_v / "conclusion.md"
            if not conclusion_path.exists():
                skipped.append(f"{strategy_id}/{version} — 没有 conclusion.md")
                continue

            # 找对应版本的 idea；如果没有同版本，回退到该策略最新有 idea.md 的版本
            idea_strategy_dir = IDEAS_DIR / strategy_id
            idea_v: Path | None = None
            same = idea_strategy_dir / version
            if same.exists() and (same / "idea.md").exists():
                idea_v = same
            else:
                # 从最新往旧找一个有 idea.md 的版本
                if idea_strategy_dir.exists():
                    for candidate in reversed(list_versions(idea_strategy_dir)):
                        if (candidate / "idea.md").exists():
                            idea_v = candidate
                            break
            if idea_v is None:
                skipped.append(f"{strategy_id}/{version} — 找不到对应的 idea.md")
                continue

            idea_fm = parse_frontmatter((idea_v / "idea.md").read_text(encoding="utf-8"))
            concl_fm = parse_frontmatter(conclusion_path.read_text(encoding="utf-8"))
            title_raw = idea_fm.fields.get("title") or strategy_id
            title = title_raw if isinstance(title_raw, str) else " ".join(title_raw)

            one_liner_section = extract_section(concl_fm.body, "一句话结论")
            one_liner = first_nonempty_line(one_liner_section) or first_nonempty_line(idea_fm.body)
            # 截断到 280 字符并清理不匹配的 markdown 标记，避免渲染串行
            one_liner = one_liner.replace('"', "'")[:280]
            # 去掉首尾不成对的 ** / * / ` 等
            one_liner = re.sub(r"\*\*", "", one_liner) if one_liner.count("**") % 2 else one_liner
            one_liner = re.sub(r"(?<!\*)\*(?!\*)", "", one_liner) if one_liner.count("*") % 2 else one_liner
            one_liner = re.sub(r"`", "", one_liner) if one_liner.count("`") % 2 else one_liner

            status_raw = concl_fm.fields.get("status") or idea_fm.fields.get("status") or "unknown"
            status = status_raw if isinstance(status_raw, str) else " ".join(status_raw)

            created_raw = idea_fm.fields.get("created") or "2026-01-01"
            created = created_raw if isinstance(created_raw, str) else "2026-01-01"

            entries.append(
                VersionEntry(
                    strategy_id=strategy_id,
                    version=version,
                    idea_dir=idea_v,
                    summary_dir=summary_v,
                    title=title,
                    one_liner=one_liner,
                    status=status,
                    created=created,
                )
            )

    if skipped:
        for s in skipped:
            print(f"  · 跳过 {s}")
    return entries


def classify_status(status: str) -> str:
    """把 status 字段分类成 positive / negative / neutral，用于颜色编码。"""
    s = status.lower()
    if "shelved" in s or "negative" in s or "rejected" in s:
        return "negative"
    if "shipped" in s:
        return "positive"
    return "neutral"


STATUS_EMOJI = {"positive": "✅", "negative": "❌", "neutral": "⏳"}


def render_versions_nav(current: VersionEntry, siblings: list[VersionEntry]) -> str:
    """生成「本策略其他版本」区块的 markdown（包含 HTML 包装以便 CSS 美化）。

    用空行分隔 HTML 容器与内部 markdown，让 Goldmark 渲染内部列表。
    """
    if len(siblings) <= 1:
        return ""
    lines = ['<div class="versions-nav">', '<div class="versions-nav-title">本策略的其他版本</div>', ""]
    for sib in siblings:
        kind = classify_status(sib.status)
        emoji = STATUS_EMOJI[kind]
        if sib.version == current.version:
            lines.append(
                f'- <span class="version-tag version-tag-current">{sib.version}</span>'
                f' **本文** {emoji} — {sib.one_liner}'
            )
        else:
            target = f"{sib.strategy_id}_{sib.version}"
            link = f'[{sib.version}]({{{{< relref "/posts/strategies/{target}/index.md" >}}}})'
            lines.append(
                f'- <span class="version-tag version-tag-{kind}">{link}</span>'
                f' {emoji} — {sib.one_liner}'
            )
    lines.append("")
    lines.append("</div>")
    return "\n".join(lines)


def build_post(entry: VersionEntry, siblings: list[VersionEntry]) -> tuple[str, list[Path]]:
    idea_text = (entry.idea_dir / "idea.md").read_text(encoding="utf-8")
    conclusion_text = (entry.summary_dir / "conclusion.md").read_text(encoding="utf-8")
    impl_text = (entry.summary_dir / "implementation.md").read_text(encoding="utf-8") if (entry.summary_dir / "implementation.md").exists() else ""
    valid_text = (entry.summary_dir / "validation.md").read_text(encoding="utf-8") if (entry.summary_dir / "validation.md").exists() else ""

    idea_fm = parse_frontmatter(idea_text)
    concl_fm = parse_frontmatter(conclusion_text)

    finalized_raw = concl_fm.fields.get("finalized") or "TBD"
    finalized = finalized_raw if isinstance(finalized_raw, str) else " ".join(finalized_raw)

    idea_tags = idea_fm.fields.get("tags") or []
    if isinstance(idea_tags, str):
        idea_tags = [idea_tags]
    tags = ["策略复盘"] + idea_tags

    # 多版本时把版本号加进 title 里区分
    display_title = entry.title if len(siblings) <= 1 else f"{entry.title} · {entry.version}"

    idea_one = extract_section(idea_fm.body, "一句话概括")
    idea_what = extract_section(idea_fm.body, "核心逻辑（What）")
    idea_why = extract_section(idea_fm.body, "假设与依据（Why）")
    idea_universe = extract_section(idea_fm.body, "标的与周期")

    concl_one = extract_section(concl_fm.body, "一句话结论")
    concl_data = extract_section(concl_fm.body, "关键数据")
    concl_when = extract_section(concl_fm.body, "在什么情况下有效，什么情况下失效")
    if not concl_when:
        concl_when = extract_section(concl_fm.body, "在什么情况下有效")
    concl_lesson = extract_section(concl_fm.body, "这个策略教会我什么（可迁移的经验）")
    if not concl_lesson:
        concl_lesson = extract_section(concl_fm.body, "这个策略教会我什么")

    artifacts_dir = entry.summary_dir / "artifacts"
    image_files: list[Path] = []
    image_md = ""
    if artifacts_dir.exists():
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

    impl_body = parse_frontmatter(impl_text).body.strip() if impl_text else ""
    valid_body = parse_frontmatter(valid_text).body.strip() if valid_text else ""

    status_kind = classify_status(entry.status)
    status_emoji = STATUS_EMOJI[status_kind]
    summary_with_emoji = f"{status_emoji} {entry.one_liner}"

    fm_lines = [
        "---",
        f'title: "{display_title}"',
        f"date: {entry.created}T09:00:00+08:00",
        "draft: false",
        f'summary: "{summary_with_emoji}"',
        f"tags: {tags}",
        'categories: ["策略复盘"]',
        f'series: ["{entry.strategy_id}"]',
        f'status_kind: {status_kind}',
        f'status_label: "{entry.status}"',
        "ShowToc: true",
        "TocOpen: false",
        "---",
    ]

    parts = ["\n".join(fm_lines), ""]
    # 状态 callout：用 HTML 容器配合 CSS 上色，区分好策略 / 差策略
    parts.append(f'<div class="post-callout post-callout-{status_kind}">')
    parts.append(
        f'<span class="status-badge status-{status_kind}">{status_emoji} {entry.status}</span>'
        f' · 最终化：<code>{finalized}</code>'
    )
    parts.append(
        f'<br>来源：<code>Strategy-Lib/ideas/{entry.strategy_id}/{entry.idea_dir.name}</code>'
        f' + <code>Strategy-Lib/summaries/{entry.strategy_id}/{entry.version}</code>'
    )
    parts.append("</div>")
    parts.append("")

    nav = render_versions_nav(entry, siblings)
    if nav:
        parts.append(nav)
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
    parts.append(
        "*本文由 [`scripts/sync_strategies.py`]"
        "(https://github.com/lizhao903/0xBroleez/blob/main/scripts/sync_strategies.py) "
        "从 Strategy-Lib 同步生成。*"
    )
    parts.append("")

    return "\n".join(parts), image_files


def sync() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    entries = collect_versions()
    if not entries:
        print("没有可同步的策略版本（缺 conclusion.md 或 idea.md）")
        return

    # 按 strategy_id 分组
    by_strategy: dict[str, list[VersionEntry]] = {}
    for e in entries:
        by_strategy.setdefault(e.strategy_id, []).append(e)
    for siblings in by_strategy.values():
        siblings.sort(key=lambda x: int(x.version[1:]))

    # 删除目标目录中所有不再属于本次同步集的旧 bundle
    valid_dirs = {f"{e.strategy_id}_{e.version}" for e in entries}
    if OUTPUT_DIR.exists():
        for old in OUTPUT_DIR.iterdir():
            if old.is_dir() and old.name not in valid_dirs:
                shutil.rmtree(old)
                print(f"  · 删除已废弃的 bundle: {old.name}")

    synced: list[str] = []
    for entry in entries:
        siblings = by_strategy[entry.strategy_id]
        bundle_name = f"{entry.strategy_id}_{entry.version}"
        post_dir = OUTPUT_DIR / bundle_name
        post_dir.mkdir(parents=True, exist_ok=True)

        for old_png in post_dir.glob("*.png"):
            old_png.unlink()

        index_md, images = build_post(entry, siblings)
        (post_dir / "index.md").write_text(index_md, encoding="utf-8")

        for img in images:
            shutil.copy2(img, post_dir / img.name)

        synced.append(f"{bundle_name} ({len(images)} 张图)")

    print("=" * 60)
    print(f"已同步 {len(synced)} 篇文章（{len(by_strategy)} 个策略）：")
    for s in synced:
        print(f"  ✓ {s}")


if __name__ == "__main__":
    sync()
