#!/usr/bin/env python3
"""重新评估所有 entries 的过滤规则（含 OpenCC 繁体检测）。"""
import sys
sys.stdout.reconfigure(line_buffering=True)

import re
import sqlite3
from datetime import datetime
from pathlib import Path

import opencc

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "rectg.db"

converter = opencc.OpenCC('t2s')
CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')

MIN_CH_SUB = 1000
MIN_GR_MEM = 200
INACTIVE_DAYS = 90
TRAD_RATIO = 0.10


def contains_chinese(text):
    return bool(CJK.search(text)) if text else False


def is_traditional(text):
    if not text:
        return False
    cjk = CJK.findall(text)
    if len(cjk) < 5:
        return False
    simplified = converter.convert(text)
    diff = sum(1 for a, b in zip(text, simplified) if a != b)
    return diff / max(len(text), 1) >= TRAD_RATIO


def evaluate(entry):
    if not entry["valid"]:
        return 0, "链接无效"
    if entry["private"]:
        return 0, "私密频道/群组"
    if not entry["type"]:
        return 0, "无法识别类型"

    txt = (entry["title"] or "") + (entry["description"] or "")
    if not contains_chinese(txt):
        return 0, "非中文内容"
    if is_traditional(txt):
        return 0, "繁体中文内容"

    t = entry["type"]
    c = entry["count"] or 0

    if t == "channel":
        if c < MIN_CH_SUB:
            return 0, f"订阅数不足 ({c} < {MIN_CH_SUB})"
        la = entry.get("last_active")
        if la:
            try:
                dt_str = la.replace("+00:00", "").replace("Z", "")
                dt = datetime.fromisoformat(dt_str)
                days = (datetime.now() - dt).days
                if days > INACTIVE_DAYS:
                    return 0, f"频道不活跃 ({days}天未更新)"
            except (ValueError, TypeError):
                pass
    elif t == "group":
        if c < MIN_GR_MEM:
            return 0, f"成员数不足 ({c} < {MIN_GR_MEM})"
    elif t == "bot":
        if c is None or c == 0:
            return 0, "无月活用户数据"

    return 1, ""


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
        new_keep, new_reason = evaluate(entry)

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
