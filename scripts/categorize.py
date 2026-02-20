#!/usr/bin/env python3
"""
文本清洗与精细化分类脚本 (categorize.py)
用于清理标题和描述中的 Emoji、冗余文本，并基于关键字进行自动细分分类。

用法:
    python3 scripts/categorize.py
"""

import sqlite3
import re
from pathlib import Path
import emoji

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "rectg.db"

# ---------------------------------------------------------------------------
# 0. 有害内容及语言过滤
# ---------------------------------------------------------------------------

HARMFUL_KEYWORDS = [
    "博彩", "赌场", "资金盘", "跑分", "枪支", "迷药", "催情", "迷幻",
    "洗钱", "提现", "查档", "开房记录", "社工库", "呼死你", "轰炸机",
    "菠菜", "嫩模", "外围", "约炮", "迷奸", "代开发票", "黑产", "网赚",
    "色流", "彩票", "赌博", "百家乐", "六合彩", "棋牌", "网赌", "黑客", "破解盗刷",
    "免费节点", "翻墙", "机场", "免流", "梯子", "科学上网", "v2ray", "shadowsocks",
    "莞式", "全套", "品茶", "修车", "同城群", "约妹"
]

# 用于匹配“禁止XXX”的正则，这些词语如果出现在“禁止”、“严禁”之后，则属于正常的群规，不应该被判定为有害频道
PROHIBITED_CONTEXT_REGEX = re.compile(r'(禁止|严禁|不准|拒绝|谢绝).*?(机场|翻墙|梯子|节点|免流|黑产|广告|博彩|赌博|色情|政治)')

def _remove_prohibited_context(text: str) -> str:
    """如果文本中出现 '禁止机场' 等群规声明，将其从特征本中剔除，避免误杀。"""
    # 简单地把匹配到的“禁止XXX”短语替换掉，这样它们就不会触发 subsequent 的关键词匹配
    return PROHIBITED_CONTEXT_REGEX.sub('', text)

def is_harmful(text: str) -> bool:
    text = text.lower()
    # 先剔除掉正常群规声明中的敏感词
    text_to_check = _remove_prohibited_context(text)
    
    for kw in HARMFUL_KEYWORDS:
        if kw in text_to_check:
            return True
    return False

def is_non_simplified_chinese(text: str) -> bool:
    """过滤非简体中文内容：如果中文字符比例极低，视为非目标语言频道。"""
    if not text:
        return True
    
    cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    clean_len = len(re.sub(r'[^\w]', '', text))
    
    if clean_len > 0:
        ratio = cjk_count / clean_len
        # 如果中文字符占比低于 15% 且总有效字符大于 20，判为非中文
        if ratio < 0.15 and clean_len > 20: 
            return True
        # 如果总长大于10但中文字符不到3个
        if cjk_count < 3 and clean_len > 10:
            return True
            
    return False

# ---------------------------------------------------------------------------
# 1. 文本清洁 (Text Optimization)
# ---------------------------------------------------------------------------

def remove_emoji(text: str) -> str:
    """去除文本中的所有 Emoji。"""
    if not text:
        return ""
    return emoji.replace_emoji(text, replace="")

def clean_text_advanced(text: str, title: str = "") -> str:
    """高级文本清洗：去除特定的引流词、网址、多余换行和符号等，并结合名称提炼。"""
    if not text:
        return ""
    
    # 去除 Emoji
    text = remove_emoji(text)
    
    # 去除 URL 链接和 @username
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r't\.me/[^\s]+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'tg://[^\s]+', '', text)
    
    # 去除冗余的引流、广告用语、常见无意义短语
    spam_patterns = [
        r'点击链接', r'加入群组', r'关注我们', r'点此加入',
        r'欢迎来到', r'各位大佬', r'在这里您可以', r'点击关注',
        r'本群规', r'进群请', r'防失联', r'解封说明',
        r'商务合作', r'广告投放', r'联系群主', r'联系管理',
        r'唯一投稿', r'投稿请联系', r'找资源的', r'交流群',
        r'聊天群', r'备用频道', r'官方频道', r'最新地址',
        r'请看置顶', r'进群看', r'获取最新', r'合作：',
        r'联系：', r'客服：', r'TG频道：', r'电报频道',
        r'【.*?】', r'\[.*?\]' # 去除各种括号包围的（往往是标签）如果太空洞，但这里保留，因为可能有有用信息。暂时不删括号。
    ]
    
    for pattern in spam_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
    # 去掉特定的格式词语块
    text = re.sub(r'\[.*?推广.*?\]|【.*?广告.*?】', '', text)
    text = re.sub(r'商务合作.*?\n?', '', text)
    
    # 将长串连续的标点符号截断为单标点
    text = re.sub(r'([。！？…])\1+', r'\1', text)
    text = re.sub(r'([，、：；])\1+', r'\1', text)
    
    # 替换连续的换行符和空格为一个空格
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    # 去除两端或多余的标点
    text = re.sub(r'^[、，。！？：；\-|~= \*\#]+|[、，。！？：；\-|~= \*\#]+$', '', text.strip())
    
    # 截断策略：如果还是太长，则截取 100 字，寻找标点符号断句
    if len(text) > 100:
        trunc = text[:95]
        # 尝试在最后一个句号/叹号/逗号处截断
        match = re.search(r'[。！？，；][^。！？，；]*$', trunc)
        if match and match.start() > 50: # 如果后半段有标点符号
            text = trunc[:match.start()+1] + "..."
        else:
            text = trunc + "..."
            
    # 如果清洗完只剩下极少的字，且与 title 几乎一样，则加上“相关讨论与分享”
    if title and len(text) < 5 and text in title:
        text = f"关于 {title} 的相关讨论与分享频道。"
        
    return text.strip()

def clean_title_advanced(title: str) -> str:
    """专门为 title 清除多余修饰符。"""
    if not title:
        return ""
    title = remove_emoji(title)
    # 常用来装饰名字的特殊符号
    title = re.sub(r'[【】\[\]《》<>|｜～~*✨🌟🔥💥⚡️💯🎯🎁🎉🎊]+', ' ', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


# ---------------------------------------------------------------------------
# 2. 精细化分类 (Categorization) - 17 大类 + 上下文感知
# ---------------------------------------------------------------------------

# 用于剔除群规/声明中的关键词，避免"禁止NSFW"被归入 🔞
_RULE_CONTEXT_RE = re.compile(
    r'(禁止|严禁|不准|不允许|拒绝|谢绝|不发|不开|请勿|莫商|莫开|限制)'
    r'[^，。！？；\n]{0,15}?'
    r'(nsfw|色情|色图|涩图|18\+|开车|r18|adult|porn|sex|福利|政治|黄赌毒|广告|盗版|黑产)',
    re.IGNORECASE
)

def _remove_rule_context(text: str) -> str:
    """剔除群规声明中的敏感词上下文，防止分类误判。"""
    return _RULE_CONTEXT_RE.sub('', text)


# 分类列表（顺序即优先级，越靠前越优先匹配）
# 🔞 放在最后面以降低误分类可能
CATEGORIES = [
    {
        "name": "📰 新闻快讯",
        "keywords": [
            "新闻", "快讯", "报纸", "日报", "早报", "周刊", "时报",
            "媒体", "报道", "爆料", "时政", "内幕", "时事", "环球",
            "端传媒", "rss", "数字时代", "南方周末", "纽约时报",
            "财经", "财新", "华尔街", "金融时报",
        ]
    },
    {
        "name": "🪙 加密货币",
        "keywords": [
            "加密货币", "币圈", "区块链", "btc", "eth", "web3",
            "空投", "挖矿", "炒币", "nft", "交易所", "代币",
            "数字货币", "usdt", "比特币", "以太坊", "合约",
            "defi", "期货", "期权", "投资快讯",
        ]
    },
    {
        "name": "🎬 影视剧集",
        "keywords": [
            "电影", "影视", "影院", "电视剧", "剧集", "网飞",
            "netflix", "4k", "美剧", "韩剧", "日剧", "中文字幕",
            "1080p", "纪录片", "bbc", "nhk", "asmr", "视频频道",
            "流媒体", "emby", "youtube",
        ]
    },
    {
        "name": "🎵 音乐音频",
        "keywords": [
            "音乐", "无损", "flac", "mp3", "音频", "网易云",
            "qq音乐", "歌单", "发烧友", "音响", "播客", "podcast",
            "听众",
        ]
    },
    {
        "name": "🎐 动漫次元",
        "keywords": [
            "动漫", "番剧", "二次元", "acg", "追番", "漫画",
            "轻小说", "里番", "同人", "画师", "cosplay", "漫展",
            "pixiv", "p站", "galgame", "黄油", "萌图", "萌域",
            "嗶咔", "插画", "动画", "酷漫",
        ]
    },
    {
        "name": "🎮 游戏娱乐",
        "keywords": [
            "游戏", "手游", "端游", "主机", "steam", "switch",
            "ps5", "xbox", "原神", "王者荣耀", "吃鸡", "和平精英",
            "电竞", "主机游戏", "单机游戏", "外挂", "破解游戏",
            "开黑", "神魔之塔", "minecraft", "狼人杀",
        ]
    },
    {
        "name": "💻 数码科技",
        "keywords": [
            "科技", "数码", "硬件", "apple", "苹果", "安卓",
            "ios", "mac", "windows", "手机", "测评", "极客",
            "geek", "科技新闻", "软路由", "路由器", "nas",
            "群晖", "openwrt", "google voice", "三星", "小米",
            "键盘", "apple tv", "树莓派", "raspberry",
            "ai", "chatgpt", "deepseek", "gpt", "人工智能",
            "claude", "openai", "aigc", "chromebook",
            "blackberry",
        ]
    },
    {
        "name": "👨‍💻 开发运维",
        "keywords": [
            "开源", "代码", "github", "开发", "程序员", "前端",
            "后端", "python", "linux", "java", "php", "golang",
            "运维", "码农", "编程", "服务器", "vps", "docker",
            "ubuntu", "manjaro", "arch", "debian", "centos",
            "javascript", "typescript", "rust", "scala", "ruby",
            "c语言", "hadoop", "spark", "magisk", "kernelsu",
            "v2fly", "hacker news", "leetcode", "刷题",
            "haskell", "perl", "css", "swiftui", "fedora",
            "vim", "openwrt固件",
        ]
    },
    {
        "name": "🔒 信息安全",
        "keywords": [
            "信息安全", "安全技术", "安防", "隐私", "privacy",
            "安全资源", "渗透", "防护", "加密", "密码学",
            "adguard", "防撤回", "anti revoke", "ddos",
        ]
    },
    {
        "name": "✈️ 科学上网",
        "keywords": [
            "免流", "节点", "代理", "vpn", "机场", "科学上网",
            "翻墙", "v2ray", "clash", "shadowsocks", "trojan",
            "测速", "梯子", "surge", "quantumult", "loon",
            "迷雾通", "搬瓦工",
        ]
    },
    {
        "name": "☁️ 网盘资源",
        "keywords": [
            "网盘", "阿里云盘", "夸克", "百度云", "百度网盘",
            "天翼", "迅雷", "115", "资源分享", "扩容",
            "pt", "tracker", "种子", "磁力", "离线下载",
            "google drive",
        ]
    },
    {
        "name": "🧰 软件工具",
        "keywords": [
            "软件", "app", "破解版", "修改版", "绿色版",
            "安装包", "apk", "mac软件", "win软件", "效率",
            "工具", "神器", "快捷指令", "脚本",
            "翻译", "translate", "simpread", "简悦",
            "notion", "输入法",
        ]
    },
    {
        "name": "📚 学习阅读",
        "keywords": [
            "学习", "外语", "英语", "日语", "电子书", "kindle",
            "epub", "pdf", "公开课", "课程", "教程", "考研",
            "雅思", "托福", "读书", "知乎", "期刊", "杂志",
            "考公", "网课", "博客", "blog", "少数派",
            "值得读", "豆瓣", "经济学", "哲学",
            "维基百科", "wikipedia", "有声", "写作",
        ]
    },
    {
        "name": "📡 社媒搬运",
        "keywords": [
            "推特", "twitter", "微博", "reddit", "饭否",
            "微信搬运", "精选", "翻译推", "公众号",
        ]
    },
    {
        "name": "🎨 创意设计",
        "keywords": [
            "设计", "design", "ui", "ux", "排版",
            "字体", "画室", "美术", "艺术", "art",
            "创意", "品牌",
        ]
    },
    {
        "name": "🏀 体育运动",
        "keywords": [
            "体育", "足球", "篮球", "nba", "cba",
            "运动", "健身", "跑步", "世界杯", "欧冠",
        ]
    },
    {
        "name": "👗 生活消费",
        "keywords": [
            "日常", "购物", "薅羊毛", "羊毛", "优惠", "折扣",
            "淘宝", "京东", "拼多多", "外卖", "求职", "招聘",
            "职场", "旅游", "机票", "美食", "壁纸", "wallpaper",
            "头像", "文案", "摄影", "颜值", "美图",
            "信用卡", "sim卡", "捡漏", "限免", "亚马逊", "amazon",
            "地震", "天气",
        ]
    },
    {
        "name": "🌍 地区社群",
        "keywords": [
            "湖南", "广西", "四川", "西安", "济南", "周口",
            "河南", "北京", "上海", "广东", "深圳", "成都",
            "台湾", "香港", "高雄", "大学联盟", "大学",
        ]
    },
    {
        "name": "💬 闲聊交友",
        "keywords": [
            "交友", "相亲", "闲聊", "水群", "吹水",
            "单身", "聊天", "交际", "互助", "同好", "贴吧",
            "沙雕", "表情包", "贴纸", "sticker", "冷知识",
            "趣事", "段子", "笑话", "猫", "树洞", "电报群",
            "碎碎念", "日记", "拾趣", "怪话", "情话",
            "v2ex",
        ]
    },
    {
        "name": "🗂️ 综合导航",
        "keywords": [
            "导航", "搜群", "索引", "频道大全", "群组大全",
            "机器人大全", "大全", "telegram 中文", "电报中文",
            "新手", "入门", "指南", "语言包", "中文包",
        ]
    },
    {
        # 🔞 放在最后，避免群规声明中的关键词优先匹配到此类
        "name": "🔞 福利吃瓜",
        "keywords": [
            "nsfw", "老司机", "写真", "套图", "色图", "涩图",
            "黑料", "探花", "海角", "绅士", "妹子图",
            "吃瓜",
        ]
    },
]


def determine_category(title: str, desc: str) -> str:
    """根据关键词推断分类，带上下文感知。
    
    1. 先用 title 单独匹配（title 中出现的关键词更可信）
    2. 再用 title + desc 联合匹配
    3. 联合匹配时先剔除群规声明中的关键词上下文
    """
    title_lower = title.lower()
    
    # 第一轮：仅匹配 title（高置信度）
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw.lower() in title_lower:
                return cat["name"]
    
    # 第二轮：匹配 title + desc（先剔除群规声明上下文）
    full_text = f"{title} {desc}".lower()
    full_text_cleaned = _remove_rule_context(full_text)
    
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw.lower() in full_text_cleaned:
                return cat["name"]
    
    return "🌐 综合其他"


def main():
    print("🧹 开始执行高级清洗与精细分类 (22大类)...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("SELECT * FROM entries WHERE keep=1").fetchall()
    print(f"处理保留的 {len(rows)} 条记录...")
    
    changed = 0
    filtered_harmful = 0
    filtered_lang = 0
    cat_counts = {}
    
    for row in rows:
        entry = dict(row)
        title = entry.get("title") or ""
        desc = entry.get("description") or ""
        full_text = title + " " + desc
        
        # 0. 有害内容及语言过滤
        if is_harmful(full_text):
            conn.execute("UPDATE entries SET keep=0, filter_reason='有害内容', updated_at=datetime('now') WHERE id=?", (entry["id"],))
            changed += 1
            filtered_harmful += 1
            print(f"  ❌ 过滤 (有害内容): {title}")
            continue
            
        if is_non_simplified_chinese(full_text):
            conn.execute("UPDATE entries SET keep=0, filter_reason='非简中内容', updated_at=datetime('now') WHERE id=?", (entry["id"],))
            changed += 1
            filtered_lang += 1
            print(f"  ❌ 过滤 (非简中内容): {title}")
            continue

        # 1. & 2. 清洗与分类
        c_title = clean_title_advanced(title) or title  # fallback
        c_desc = clean_text_advanced(desc, title)
        
        # fallback for completely wiped descriptions
        if not c_desc:
            c_desc = "暂无详细简介。"
            
        category = determine_category(title, desc)
        
        conn.execute(
            "UPDATE entries SET clean_title=?, clean_desc=?, category=?, updated_at=datetime('now') WHERE id=?",
            (c_title, c_desc, category, entry["id"])
        )
        changed += 1
        cat_counts[category] = cat_counts.get(category, 0) + 1
        
    conn.commit()
    conn.close()
    
    print(f"✅ 处理完成，共重新分类和清洗 {changed} 条记录！")
    if filtered_harmful > 0 or filtered_lang > 0:
        print(f"   其中排除了 {filtered_harmful} 条有害内容，{filtered_lang} 条非简中内容。")
    print("\n📊 分类统计 (留存项目):")
    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} 条")


if __name__ == "__main__":
    main()
