#!/usr/bin/env python3
"""
README.md 生成器
从 SQLite 数据库读取已经清洗和分类好的爬虫结果，生成更新后的 README.md。

用法:
    python3 scripts/generate_readme.py
"""
import argparse
import base64
import sqlite3
import html
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import quote

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "rectg.db"
README_PATH = ROOT_DIR / "README.md"
README_DESC_LIMIT = 88

# 一级大类
TYPE_ORDER = [
    {"id": "channel", "name": "频道"},
    {"id": "group", "name": "群组"},
    {"id": "bot", "name": "机器人"},
]

# 二级分类排序规则（按照这个顺序输出二级分类）
CATEGORY_ORDER = [
    "🆕 新发现频道",
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

def strip_category_icon(category: str) -> str:
    """去掉分类名前的 emoji，生成更干净的查询参数。"""
    return re.sub(r"^\S+\s+", "", category).strip()

def compact_text(text: str) -> str:
    """压缩多余空白，适合表格单元格。"""
    if not text:
        return ""
    return " ".join(text.split())

def truncate_text(text: str, limit: int = README_DESC_LIMIT) -> str:
    """截短 README 中的可见简介，降低表格阅读负担。"""
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."

def encode_hidden_desc(text: str) -> str:
    """把完整简介藏在 HTML 注释里，供网站数据构建使用。"""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")

def render_desc_cell(text: str) -> str:
    """渲染 README 简介单元格，同时保留完整简介给构建脚本。"""
    full_text = compact_text(text)
    if not full_text:
        return "-"

    visible_text = truncate_text(full_text)
    visible = escape_table_text(visible_text) or "-"
    if visible_text == full_text:
        return visible

    return f"{visible} <!-- rectg-desc:{encode_hidden_desc(full_text)} -->"

def sorted_categories(categories: dict[str, list[dict]]) -> list[str]:
    """按照预设顺序输出分类，其余分类稳定追加到最后。"""
    existing_cats = set(categories.keys())
    result = [c for c in CATEGORY_ORDER if c in existing_cats]
    result += sorted(list(existing_cats - set(CATEGORY_ORDER)))
    return result

def build_toc_column(title: str, section_id: str, categories: list[str], counts: dict[str, int]) -> str:
    """构建目录单列 HTML，适配 GitHub README 的多列表现。"""
    links = [f'<a href="#{make_anchor(section_id)}"><strong>{title}</strong></a>']
    for idx, cat in enumerate(categories, start=1):
        links.append(f'<a href="#{make_anchor(section_id, idx)}">{cat}</a> <sub>{counts.get(cat, 0)}</sub>')
    return "<br>".join(links)

def build_stats_table(type_counts: dict[str, int], category_count: int) -> str:
    """构建 README 顶部数据概览。"""
    total = sum(type_counts.values())
    stat_items = [
        ("总收录", format_count(total), "频道与群组"),
        ("分类", format_count(category_count), "主题索引"),
        ("频道", format_count(type_counts.get("channel", 0)), "Channel"),
        ("群组", format_count(type_counts.get("group", 0)), "Group"),
    ]

    cells = []
    for label, value, hint in stat_items:
        cells.append(
            "    "
            f'<td align="center"><strong>{html.escape(value)}</strong><br>'
            f'<sub>{html.escape(label)} · {html.escape(hint)}</sub></td>'
        )

    return "\n".join(["<table>", "  <tr>", *cells, "  </tr>", "</table>"])

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
        {"title": "副业", "url": "https://t.me/sidehustleus", "description": "关注副业赚钱、搞钱经验和独立开发", "count": None},
        {"title": "技术拾荒者", "url": "https://t.me/tech_scavenger", "description": "分享优质技术文章、开源项目与实用工具", "count": None},
        {"title": "一个人的产品", "url": "https://t.me/solo_product", "description": "独立开发者、产品设计与运营经验", "count": None},
        {"title": "深夜博客", "url": "https://t.me/late_night_blog", "description": "深夜阅读文章、个人随笔与精神角落", "count": None},
        {"title": "什么值得看", "url": "https://t.me/worth_read", "description": "推荐值得一读的好文章与好书", "count": None},
        {"title": "程序员日常", "url": "https://t.me/dev_everyday", "description": "程序员的日常工作、吐槽与经验分享", "count": None},
        {"title": "小众软件", "url": "https://t.me/niche_software", "description": "发现与分享好用、新奇的小众软件", "count": None},
        {"title": "酱酱の日报", "url": "https://t.me/jiangdaily", "description": "每天不只是新闻，更是酱酱的发现日常～ 精选有趣、有料、有灵魂的「热饭」", "count": 137},
        {"title": "财经速报", "url": "https://t.me/econ_news_cn", "description": "最新最快的财经新闻与市场动态资讯", "count": None},
        {"title": "AI 工具情报局", "url": "https://t.me/AIGongJuQBJ", "description": "每天更新 AI 工具、软件应用、开源项目和效率产品动态，帮你更快发现真正有用的工具。", "count": 2}
    ]
    custom_urls = {ch["url"] for ch in NEW_CHANNELS}
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

    for row in rows:
        t = row["type"]
        if t not in tree:
            continue
            
        # 过滤掉自定义注入的频道，防止重复
        if row["url"] in custom_urls:
            continue

        cat = row["category"] or "🌐 综合其他"
        if cat not in tree[t]:
            tree[t][cat] = []
        tree[t][cat].append(dict(row))

    # 注入新频道板块
    tree["channel"]["🆕 新发现频道"] = [
        {
            "type": "channel",
            "category": "🆕 新发现频道",
            "clean_title": ch["title"],
            "title": ch["title"],
            "url": ch["url"],
            "count": count_by_url.get(ch["url"], ch["count"]),
            "clean_desc": ch["description"],
            "description": ch["description"]
        } for ch in NEW_CHANNELS
    ]

    type_counts = {}
    for t_id in tree:
        type_counts[t_id] = sum(len(items) for items in tree[t_id].values())

    lines = []
    all_categories = {
        cat
        for categories in tree.values()
        for cat in categories.keys()
    }
    lines.append("<h1 align=\"center\">rectg</h1>")
    lines.append("")
    lines.append("<p align=\"center\">Telegram 中文频道与群组精选索引</p>")
    lines.append("")
    lines.append("<p align=\"center\">")
    lines.append("  <a href=\"https://www.rectg.com/\"><strong>在线浏览</strong></a>")
    lines.append("  ·")
    lines.append("  <a href=\"https://github.com/jackvale/rectg/issues/new\">提交收录</a>")
    lines.append("</p>")
    lines.append("")
    lines.append("> **rectg** 持续收录高质量 Telegram 中文频道与群组，结合自动化抓取与人工整理，帮助你更高效地发现值得关注的 TG 资源。")
    lines.append("> ")
    lines.append("> 本项目基于公开信息整理，仅作导航与研究参考；请自行甄别内容并遵守所在地法律法规。")
    lines.append("")

    lines.append("## 数据概览")
    lines.append("")
    lines.append(build_stats_table(type_counts, len(all_categories)))
    lines.append("")
    lines.append("## 快速导航")
    lines.append("")

    toc_columns = []
    for t_info in TYPE_ORDER:
        t_id = t_info["id"]
        categories = tree[t_id]
        if not categories:
            continue

        ordered_cats = sorted_categories(categories)
        cat_counts = {cat: len(categories[cat]) for cat in ordered_cats}
        toc_columns.append((t_info["name"], build_toc_column(t_info["name"], t_id, ordered_cats, cat_counts)))

    if toc_columns:
        lines.append("<table>")
        lines.append("  <tr>")
        for title, _ in toc_columns:
            lines.append(f"    <th>{title}</th>")
        lines.append("  </tr>")
        lines.append("  <tr>")
        for _, content in toc_columns:
            lines.append(f"    <td valign=\"top\">{content}</td>")
        lines.append("  </tr>")
        lines.append("</table>")
        lines.append("")

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
            site_category_url = f"https://www.rectg.com/?c={quote(strip_category_icon(cat))}"
            lines.append("<details open>")
            lines.append(f"<summary><strong>{len(items)} 个资源</strong> · <a href=\"{site_category_url}\">站内查看</a></summary>")
            lines.append("")
            lines.append("| 资源 | 人数 | 简介 |")
            lines.append("| --- | ---: | --- |")

            for item in items:
                title = escape_table_text(compact_text(item.get("clean_title") or item.get("title") or ""))
                desc = render_desc_cell(item.get("clean_desc") or item.get("description") or "")
                url = item.get("url", "")
                count = format_count(item.get("count"))
                lines.append(f"| [{title}]({url}) | {count} | {desc} |")

            lines.append("")
            lines.append("</details>")
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
