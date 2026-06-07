#!/usr/bin/env python3
"""
tg-nav.github.io 链接抓取器
从 tg-nav 的频道页和群组页中提取 Telegram 用户名，导入到 links 表。

注意: tg-nav.github.io 使用 JavaScript 渲染内容，主要内容在静态 HTML 中不可见。
因此本脚本同时使用两种策略：
1. 使用 requests 获取静态 HTML 中的 t.me 链接
2. 内嵌一份从浏览器中预提取的用户名列表作为补充

用法:
    python3 scripts/scrape_tgnav.py
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "rectg.db"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

# 需要排除的用户名（推广/非 TG 内容/通用词）
EXCLUDE_USERNAMES = {
    "s", "joinchat", "proxy", "socks", "share", "iv",
}

# ---------------------------------------------------------------------------
# 从浏览器预提取的用户名（tg-nav 使用 JS 渲染，静态 HTML 获取不到这些）
# 最后更新: 2026-02-20
# ---------------------------------------------------------------------------
BROWSER_EXTRACTED = {
    # 群组
    "simfans", "DocOfCard", "group_shouliumeiyizhifuyou",
    "TGQRYbot", "TeleindexBot", "aiso", "jisouZHbot",
    "PolarisseekBot", "So1234Bot", "zh_secretary_bot",
    "daohangbot", "damosuoyinAdminbot", "TG_index_bot",
    "qunzudaquan_bot", "tg_chs_bot", "SearcheeBot",
    "kuqun_bot", "dh2345_bot", "quannengsobot",
    "TeleSearchMain_bot", "UniversityAlliance_Info",
    "airport_chat", "lilydeyaa", "se_talk", "MFJD99",
    "MoeMeta", "KinhDownChat", "Brahmanjg",
    "OnlineAppleUserGroup", "WeiyouTuwu1", "shufm",
    "sharing_books4u", "shumozyfx", "ReadfineChat",
    "Waikan2023", "paoluqun", "Yiology", "Liyuxuanxue",
    "ubuntuzh", "pythonzh", "P_Y_T_H_O_N",
    "open_source_community", "coder_ot", "V2EXPro",
    "goV2EX", "pan_icu", "GolangCN", "vpschat",
    "dockertutorial", "Clanguagezh", "AndroidDevCn",
    "vpsxinhaoqi", "tgcnx", "haijiaosheque", "tgzhcn",
    "CNderivatives", "hezu1", "wikipedia_zh_n",
    "jichang_user", "gpt_user", "googlevoice", "GVsPbot",
    "zaihuachat", "jianjiaoQUN", "douban_discuss",
    "yummy_best", "NewlearnerGroup", "kejiquchat",
    "hengjiazhihui", "cosplaysharegroup", "xiafengforever",
    "xpyanjiusuo1", "vGiJ3ukDAa80ZDhl", "nekopara",
    "acg_moe", "tsukigroup", "MEME981211", "mio_house",
    "QingjuACG_Chat", "galgame", "abcd13354",
    "RhineDiscussionRoom",
    # 频道 + 群组共有
    "appdododo", "pdcn3", "ruanlu", "lajilao",
    "AppleTVPlus", "KernelSU_group", "ham002",
    "samsung_cn", "xiaomi6666", "cemiuiler", "nasfan",
    "DHDAXCW", "homelab520", "MaoYingShi", "shumeipai",
    "blacktechsharing", "appmiao", "Riocoolapk",
    "ycq_777", "loopdns", "wolfgang88", "LdFriend",
    "plus8889", "youyousharegroup", "nagram_group",
    "Loon0x00", "loveapps", "QuanXApp", "Notionso",
    "netflixchina", "appinn",
    # 频道页
    "Aliyundrive_Share_Group", "Aliyundrive_Share_Channel",
    "photo100percent", "shadiaogenjudi", "xin_jing_bao",
    "yppshare", "alyd_g", "cnphotog", "shadiaoo",
    "xinjingdailychatroom", "shaodiaotu_chat", "ywtrzm",
}


def init_db(db_path: Path) -> sqlite3.Connection:
    """初始化数据库连接。"""
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


def extract_tme_usernames(html: str) -> set[str]:
    """从 HTML 中提取 t.me 用户名。"""
    soup = BeautifulSoup(html, "lxml")
    usernames = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # 模式 1: tg-nav.github.io/detail/{username}
        m = re.search(r'tg-nav\.github\.io/detail/([A-Za-z0-9_]+)', href)
        if m:
            usernames.add(m.group(1))
            continue

        # 模式 2: tg-nav.github.io/go/?username={username}
        m = re.search(r'tg-nav\.github\.io/go/\?username=([A-Za-z0-9_]+)', href)
        if m:
            usernames.add(m.group(1))
            continue

        # 模式 3: t.me/{username}
        parsed = urlparse(href)
        if parsed.hostname in ("t.me", "www.t.me"):
            path = parsed.path.strip("/")
            if not path or path.startswith("joinchat/") or path.startswith("+"):
                continue
            username = path.split("/")[0]
            if username in EXCLUDE_USERNAMES:
                continue
            if re.match(r'^[A-Za-z][A-Za-z0-9_]{3,}$', username):
                usernames.add(username)

    return usernames


def main():
    print("=" * 60)
    print("  tg-nav.github.io 链接抓取器")
    print("=" * 60)

    conn = init_db(DB_PATH)
    session = requests.Session()
    session.headers.update(HEADERS)

    # 合并所有用户名来源
    all_usernames: set[str] = set(BROWSER_EXTRACTED)

    # 尝试从静态 HTML 补充（只能获取推广区的 t.me 链接）
    pages = [
        "https://tg-nav.github.io/",
        "https://tg-nav.github.io/group",
    ]
    for page_url in pages:
        print(f"\n📡 正在抓取: {page_url}")
        try:
            resp = session.get(page_url, timeout=30)
            resp.raise_for_status()
            html_usernames = extract_tme_usernames(resp.text)
            new = html_usernames - all_usernames
            print(f"   静态 HTML 中找到 {len(html_usernames)} 个用户名, 新增 {len(new)} 个")
            all_usernames |= html_usernames
        except requests.RequestException as e:
            print(f"   ⚠️ 请求失败 (将使用预提取数据): {e}")

    print(f"\n📊 合计去重后共 {len(all_usernames)} 个用户名")

    # 写入数据库
    now = datetime.now().isoformat()
    inserted = 0
    skipped = 0

    for username in sorted(all_usernames):
        url = f"https://t.me/{username}"
        name = f"[tg-nav] {username}"

        existing = conn.execute(
            "SELECT id FROM links WHERE url = ? OR username = ?",
            (url, username),
        ).fetchone()

        if existing:
            skipped += 1
            continue

        conn.execute("""
            INSERT INTO links (url, username, name, type_hint, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (url, username, name, None, now, now))
        inserted += 1

    conn.commit()

    # 汇总
    total = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    tgnav_count = conn.execute(
        "SELECT COUNT(*) FROM links WHERE name LIKE '[tg-nav]%'"
    ).fetchone()[0]

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"  📊 汇总")
    print(f"  本次新增: {inserted}")
    print(f"  本次跳过(已存在): {skipped}")
    print(f"  tg-nav 来源总计: {tgnav_count}")
    print(f"  links 表总计: {total}")
    print(f"  数据库: {DB_PATH}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
