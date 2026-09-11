#!/usr/bin/env python3
"""
README.md 生成器
从 SQLite 数据库读取已经清洗和分类好的爬虫结果，生成更新后的 README.md。

用法:
    python3 crawler/generate_readme.py
"""
import argparse
import sqlite3
import re
import sys
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "rectg.db"
README_PATH = ROOT_DIR / "README.md"
README_DESC_LIMIT = 16

# 一级大类
TYPE_ORDER = [
    {"id": "channel", "name": "频道"},
    {"id": "group", "name": "群组"},
    {"id": "bot", "name": "机器人"},
]

# 二级分类排序规则（按照这个顺序输出二级分类）
CATEGORY_ORDER = [
    "📰 新闻快讯",
    "💻 数码科技",
    "👨‍💻 开发运维",
    "🔒 信息安全",
    "🧰 软件工具",
    "☁️ 网盘资源",
    "🎬 影视剧集",
    "🎵 音乐音频",
    "🎐 动漫次元",
    "🎮 游戏娱乐",
    "✈️ 科学上网",
    "🪙 加密货币",
    "📚 学习阅读",
    "🎨 创意设计",
    "📡 社媒搬运",
    "🏀 体育运动",
    "👗 生活消费",
    "🌍 地区社群",
    "💬 闲聊交友",
    "🗂️ 综合导航",
    "🌐 综合其他"
]


def make_anchor(section: str, category_index: Optional[int] = None) -> str:
    """生成稳定锚点，避免依赖 GitHub 对中文/emoji 标题的默认锚点规则。"""
    if category_index is None:
        return f"section-{section}"
    return f"section-{section}-{category_index}"

def format_count(count) -> str:
    """格式化数字为精确数字字符串，带千分位逗号。"""
    if count is None:
        return "-"
    return f"{int(count):,}"

def escape_table_text(text: str) -> str:
    """转义 Markdown 表格中的特殊字符。"""
    if not text:
        return ""
    return (
        text.replace("|", " / ")
        .replace("\n", " ")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .strip()
    )

def compact_text(text: str) -> str:
    """压缩多余空白，适合表格单元格。"""
    if not text:
        return ""
    return " ".join(text.split())

def canonical_url_key(url: str) -> str:
    """生成 Telegram URL 去重键，忽略用户名大小写和末尾斜杠。"""
    value = (url or "").strip()
    match = re.match(r"^(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/([^?#]+)", value, re.IGNORECASE)
    if not match:
        return value.lower().rstrip("/")

    parts = [part for part in match.group(1).split("/") if part]
    if parts and parts[0].lower() not in {"joinchat", "c"} and not parts[0].startswith("+"):
        parts[0] = parts[0].lower()
    return "t.me/" + "/".join(parts)

def rewrite_description(text: str, limit: int = README_DESC_LIMIT) -> str:
    """将原始简介整理为一句短说明，去掉链接和多余分句。"""
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = text.replace("|", "，")
    if text.strip().lower().rstrip(".") == "you can view and join right away":
        return "Telegram 资源入口。"
    clauses = [part.strip(" ，,、:：") for part in re.split(r"[。！？；;]+", text) if part.strip(" ，,、:：")]
    if not clauses:
        return ""

    pieces = [piece.strip(" ，,、:：") for piece in re.split(r"[，,、]+", clauses[0]) if piece.strip(" ，,、:：")]
    sentence_parts = []
    content_limit = max(1, limit - 1)
    for piece in pieces:
        candidate = "，".join(sentence_parts + [piece])
        if sentence_parts and len(candidate) > content_limit:
            break
        sentence_parts.append(piece)
    sentence = "，".join(sentence_parts) or clauses[0]
    if len(sentence) > content_limit:
        sentence = sentence[:content_limit].rstrip(" ，,、")
    return sentence.rstrip(" ，,、") + "。"

def render_desc_cell(text: str) -> str:
    """渲染 README 简介单元格，保持表格原文干净。"""
    full_text = compact_text(text)
    if not full_text:
        return "-"

    return escape_table_text(rewrite_description(full_text)) or "-"

def render_link_cell(url: str) -> str:
    """将 Telegram 地址显示为简洁的 @用户名链接。"""
    value = (url or "").strip()
    match = re.match(r"^(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/([^/?#]+)", value, re.IGNORECASE)
    label = f"@{match.group(1)}" if match and match.group(1) not in {"joinchat", "c"} and not match.group(1).startswith("+") else value
    return f"[{escape_table_text(label)}]({value})" if value else "-"

def sorted_categories(categories: dict[str, list[dict]]) -> list[str]:
    """按照预设顺序输出分类，其余分类稳定追加到最后。"""
    existing_cats = set(categories.keys())
    result = [c for c in CATEGORY_ORDER if c in existing_cats]
    result += sorted(list(existing_cats - set(CATEGORY_ORDER)))
    return result

def generate_readme(conn: sqlite3.Connection) -> str:
    """从数据库生成 README.md 内容。"""
    rows = conn.execute("""
        SELECT type, category, clean_title, clean_desc, url, count, title, description
        FROM entries
        WHERE keep = 1
        ORDER BY count DESC
    """).fetchall()

    # 结构: stats[type_id][cat_name] = [item1, item2, ...]
    tree = {
        "channel": {},
        "group": {},
        "bot": {}
    }
    
    total_kept = len(rows)

    # 手动注入的新频道，在这里记录它们的 URL，避免在后续重复添加
    NEW_CHANNELS = [
        {"title": "副业", "category": "👗 生活消费", "url": "https://t.me/sidehustleus", "description": "关注副业赚钱、搞钱经验和独立开发", "count": None},
        {"title": "技术拾荒者", "category": "👨‍💻 开发运维", "url": "https://t.me/tech_scavenger", "description": "分享优质技术文章、开源项目与实用工具", "count": None},
        {"title": "深夜博客", "category": "📚 学习阅读", "url": "https://t.me/late_night_blog", "description": "深夜阅读文章、个人随笔与精神角落", "count": None},
        {"title": "小众软件", "category": "🧰 软件工具", "url": "https://t.me/niche_software", "description": "发现与分享好用、新奇的小众软件", "count": None},
        {"title": "AI 工具情报局", "category": "🧰 软件工具", "url": "https://t.me/AIGongJuQBJ", "description": "每天更新 AI 工具、软件应用、开源项目和效率产品动态，帮你更快发现真正有用的工具。", "count": 2}
    ]
    custom_urls = {ch["url"] for ch in NEW_CHANNELS}
    custom_url_keys = {canonical_url_key(url) for url in custom_urls}
    custom_rows = conn.execute("""
        SELECT url, count
        FROM entries
        WHERE url IN ({})
    """.format(",".join("?" for _ in custom_urls)), tuple(custom_urls)).fetchall()
    count_by_url = {
        row["url"]: row["count"]
        for row in custom_rows
        if row["count"] is not None
    }

    seen_url_keys = set(custom_url_keys)
    for row in rows:
        t = row["type"]
        if t not in tree:
            continue
            
        # 过滤掉自定义注入的频道，防止重复
        if canonical_url_key(row["url"]) in seen_url_keys:
            continue

        seen_url_keys.add(canonical_url_key(row["url"]))

        cat = row["category"] or "🌐 综合其他"
        if cat not in tree[t]:
            tree[t][cat] = []
        tree[t][cat].append(dict(row))

    # 注入手动收录频道，并归入对应主题分类
    for ch in NEW_CHANNELS:
        category = ch["category"]
        tree["channel"].setdefault(category, []).append({
            "type": "channel",
            "category": category,
            "clean_title": ch["title"],
            "title": ch["title"],
            "url": ch["url"],
            "count": count_by_url.get(ch["url"], ch["count"]),
            "clean_desc": ch["description"],
            "description": ch["description"]
        })

    lines = []

    # 生成各版块
    for t_info in TYPE_ORDER:
        t_id = t_info["id"]
        t_name = t_info["name"]
        
        categories = tree[t_id]
        if not categories:
            continue

        lines.append(f'<a id="{make_anchor(t_id)}"></a>')
        lines.append(f"## {t_name}")
        lines.append("")
        
        # 按照预定义的 category 顺序遍历，如果不在预定义里则放到最后
        ordered_cats = sorted_categories(categories)
        
        for idx, cat in enumerate(ordered_cats, start=1):
            items = categories[cat]
            if not items:
                continue

            lines.append(f'<a id="{make_anchor(t_id, idx)}"></a>')
            lines.append("### " + cat)
            lines.append("")
            lines.append("| 名称 | 链接 | 人数 | 简介 |")
            lines.append("| --- | --- | ---: | --- |")

            for item in items:
                title = escape_table_text(compact_text(item.get("clean_title") or item.get("title") or "")) or "-"
                desc = render_desc_cell(item.get("clean_desc") or item.get("description") or "")
                url = item.get("url", "")
                count = format_count(item.get("count"))
                lines.append(f"| {title} | {render_link_cell(url)} | {count} | {desc} |")

            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="README.md 生成器")
    parser.add_argument("--output", type=str, default=None, help="输出路径（默认覆盖 README.md）")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"❌ 未找到数据库: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    readme_content = generate_readme(conn)
    conn.close()

    out_path = Path(args.output) if args.output else README_PATH
    out_path.write_text(readme_content, encoding="utf-8")
    print(f"✅ README 已生成: {out_path}")


if __name__ == "__main__":
    main()
