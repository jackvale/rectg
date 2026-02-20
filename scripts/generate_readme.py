#!/usr/bin/env python3
"""
README.md 生成器
从 SQLite 数据库读取已经清洗和分类好的爬虫结果，生成更新后的 README.md。

用法:
    python3 scripts/generate_readme.py
"""
import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "rectg.db"
README_PATH = ROOT_DIR / "README.md"

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
    "🧰 软件工具",
    "☁️ 网盘资源",
    "🎬 影视剧集",
    "🎵 音乐音频",
    "🎐 动漫次元",
    "🎮 游戏娱乐",
    "✈️ 科学上网",
    "🪙 加密货币",
    "📚 学习阅读",
    "👗 生活消费",
    "💬 闲聊交友",
    "🔞 福利吃瓜",
    "🗂️ 综合导航",
    "🌐 综合其他"
]

def format_count(count) -> str:
    """格式化数字为精确数字字符串，带千分位逗号。"""
    if count is None:
        return "-"
    return f"{int(count):,}"

def escape_pipe(text: str) -> str:
    """转义 Markdown 表格中的管道符。"""
    if not text:
        return ""
    return text.replace("|", "\\|")

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

    for row in rows:
        t = row["type"]
        if t not in tree:
            continue
            
        cat = row["category"] or "🌐 综合其他"
        if cat not in tree[t]:
            tree[t][cat] = []
        tree[t][cat].append(dict(row))

    lines = []
    lines.append("# Telegram 优质中文频道与群组精选")
    lines.append("")
    lines.append("> **rectg** 收录 1000+ 优质 Telegram 中文频道与群组。通过自动化脚本持续跟踪，严格过滤僵尸号、低质信息与停更节点，为您提供纯粹、高效的 TG 导航体验。")
    lines.append("> ")
    lines.append("> ⚠️ **免责声明**：本项目仅供技术学习与信息导航使用。严禁中国大陆地区用户使用，所有使用者须严格遵守所在地区法律法规，一切因违规使用产生的法律责任均与本项目无关。")
    lines.append("")

    # 生成各版块
    for t_info in TYPE_ORDER:
        t_id = t_info["id"]
        t_name = t_info["name"]
        
        categories = tree[t_id]
        if not categories:
            continue
            
        lines.append(f"## {t_name}")
        lines.append("")
        
        # 按照预定义的 category 顺序遍历，如果不在预定义里则放到最后
        existing_cats = set(categories.keys())
        sorted_cats = [c for c in CATEGORY_ORDER if c in existing_cats]
        sorted_cats += sorted(list(existing_cats - set(CATEGORY_ORDER)))
        
        for cat in sorted_cats:
            items = categories[cat]
            if not items:
                continue
                
            lines.append("### " + cat)
            lines.append("")
            
            for item in items:
                # 优先使用 cleaned 数据，无需 escape_pipe 因为不再是表格
                title = item.get("clean_title") or item.get("title") or ""
                desc = item.get("clean_desc") or item.get("description") or ""
                
                url = item.get("url", "")
                count = format_count(item.get("count"))
                
                type_id = item.get("type")
                type_label = next((t["name"] for t in TYPE_ORDER if t["id"] == type_id), "未知")
                
                lines.append(f"- {title}")
                lines.append(f"  - {type_label}")
                lines.append(f"  - [{url}]({url})")
                lines.append(f"  - {count}")
                if desc:
                    lines.append(f"  - {desc}")
                
                # 在每个独立的项目块之间增加一个空行，拉开视觉间距
                lines.append("")
                
            lines.append("")

    # Star History 保持在底部
    lines.append("## Star History")
    lines.append("")
    lines.append("[![Star History](https://starchart.cc/jackhawks/rectg.svg?variant=adaptive)](https://starchart.cc/jackhawks/rectg)")
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
