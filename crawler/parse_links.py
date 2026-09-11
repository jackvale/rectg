#!/usr/bin/env python3
"""
README 链接提取器
从 README.md 中提取所有 t.me 链接，保存到 SQLite 的 links 表中。

用法:
    python3 crawler/parse_links.py
    python3 crawler/parse_links.py --clear   # 清空后重新导入
"""
from __future__ import annotations

import argparse
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
README_PATH = ROOT_DIR / "README.md"
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "rectg.db"


def init_db(db_path: Path) -> sqlite3.Connection:
    """初始化数据库，创建 links 表。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            url             TEXT NOT NULL UNIQUE,
            username        TEXT,
            name            TEXT,
            type_hint       TEXT,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def extract_username(url: str):
    """从 t.me URL 中提取用户名。"""
    parsed = urlparse(url.rstrip("/"))
    path = parsed.path.strip("/")
    if not path:
        return None
    if path.startswith("joinchat/"):
        return None
    if path.startswith("+"):
        return None
    parts = path.split("/")
    username = parts[0]
    if username in ("s",):
        return None
    return username


def parse_readme(readme_path: Path) -> list:
    """解析 README.md，提取所有 t.me 链接。"""
    text = readme_path.read_text(encoding="utf-8")
    entries = []

    current_section = ""

    for line in text.splitlines():
        if line.startswith("## "):
            heading = line.lstrip("# ").strip()
            if heading in ("频道", "群组", "机器人"):
                current_section = heading
            else:
                current_section = ""
            continue

        if not current_section:
            continue

        m = re.match(
            r"\|\s*(.+?)\s*\|\s*\[([^\]]*)\]\(([^)]+)\)\s*\|",
            line,
        )
        if m:
            name = m.group(1).strip()
            url = m.group(3).strip()
            if name in ("名称", "---"):
                continue

            type_map = {"频道": "channel", "群组": "group", "机器人": "bot"}
            entry_type = type_map.get(current_section)

            entries.append({
                "name": name,
                "url": url,
                "username": extract_username(url),
                "type_hint": entry_type,
            })

    return entries


def main():
    parser = argparse.ArgumentParser(description="README 链接提取器")
    parser.add_argument("--clear", action="store_true", help="清空 links 表后重新导入")
    args = parser.parse_args()

    print("=" * 60)
    print("  README 链接提取器")
    print("=" * 60)

    conn = init_db(DB_PATH)

    if args.clear:
        conn.execute("DELETE FROM links")
        conn.commit()
        print("🗑️  已清空 links 表")

    # 解析 README
    print(f"\n📄 解析 {README_PATH}...")
    entries = parse_readme(README_PATH)
    print(f"   共找到 {len(entries)} 个链接")

    # 写入数据库
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0

    for entry in entries:
        existing = conn.execute(
            "SELECT id FROM links WHERE url = ?", (entry["url"],)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE links SET
                    username = ?, name = ?, type_hint = ?, updated_at = ?
                WHERE url = ?
            """, (entry["username"], entry["name"], entry["type_hint"], now, entry["url"]))
            updated += 1
        else:
            conn.execute("""
                INSERT INTO links (url, username, name, type_hint, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entry["url"], entry["username"], entry["name"], entry["type_hint"], now, now))
            inserted += 1

    conn.commit()

    # 统计
    total = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    by_type = conn.execute("""
        SELECT type_hint, COUNT(*) as cnt
        FROM links GROUP BY type_hint ORDER BY cnt DESC
    """).fetchall()

    conn.close()

    print(f"\n  📊 完成")
    print(f"  新增: {inserted}")
    print(f"  更新: {updated}")
    print(f"  总计: {total}")
    for row in by_type:
        label = {"channel": "频道", "group": "群组", "bot": "机器人"}.get(row["type_hint"], row["type_hint"])
        print(f"    {label}: {row['cnt']}")
    print(f"\n  数据库: {DB_PATH}")


if __name__ == "__main__":
    main()
