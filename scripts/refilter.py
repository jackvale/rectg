#!/usr/bin/env python3
"""重新评估所有 entries 的过滤规则（含 OpenCC 繁体检测）。"""
import sys
sys.stdout.reconfigure(line_buffering=True)

import sqlite3
from pathlib import Path

from filter_rules import evaluate_entry

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "rectg.db"


def main():
    print("🔄 重新评估过滤规则（含 OpenCC 繁体检测）...")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT * FROM entries").fetchall()
    print(f"📊 总条目: {len(rows)}")

    changed = 0
    trad_count = 0

    for i, row in enumerate(rows):
        entry = dict(row)
        new_keep, new_reason = evaluate_entry(entry)

        old_keep = entry["keep"]
        old_reason = entry["filter_reason"] or ""

        if new_keep != old_keep or new_reason != old_reason:
            conn.execute(
                "UPDATE entries SET keep=?, filter_reason=? WHERE id=?",
                (new_keep, new_reason, entry["id"]),
            )
            if new_keep != old_keep:
                old_s = "✅保留" if old_keep else "❌过滤"
                new_s = "✅保留" if new_keep else "❌过滤"
                print(f"  {old_s} → {new_s}: {entry['title'] or '?'} | {new_reason}")
                changed += 1

        if new_reason == "繁体中文内容":
            trad_count += 1

        if (i + 1) % 500 == 0:
            print(f"  已处理 {i + 1}/{len(rows)}...")

    conn.commit()

    s = conn.execute("""
        SELECT
            SUM(keep),
            SUM(CASE WHEN keep=0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN type='channel' AND keep=1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN type='group' AND keep=1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN type='bot' AND keep=1 THEN 1 ELSE 0 END)
        FROM entries
    """).fetchone()
    conn.close()

    print()
    print(f"✅ 完成！状态变更: {changed} 条")
    print(f"   繁体中文过滤: {trad_count} 条")
    print(f"   保留: {s[0]} | 过滤: {s[1]}")
    print(f"   ├ 频道: {s[2]} | 群组: {s[3]} | 机器人: {s[4]}")


if __name__ == "__main__":
    main()
