import scrapy


class TelegramSpider(scrapy.Spider):
    name = "telegram_1_spider"
    allowed_domains = ["github.com", "t.me"]
    start_urls = [
        "https://github.com/itgoyo/TelegramGroup",
        "https://github.com/jackhawks/rectg",
        "https://github.com/itgoyo/TelegramBot",
        "https://github.com/TG-NAV/tg-nav.github.io",
        "https://github.com/xbosou/TelegramGroups",
        "https://github.com/FandGroup/FandGroup.github.io"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 用于存储分类后的结果
        self.categories = {
            "频道": [],
            "群组": [],
            "机器人": []
        }

    def parse(self, response):
        # 从 GitHub 页面中提取所有以 https://t.me/ 开头的链接，并去重
        links = response.xpath('//a[starts-with(@href, "https://t.me/")]/@href').getall()
        unique_links = list(set(links))
        self.logger.info(f"【{response.url}】共找到 {len(unique_links)} 个唯一链接")

        # 对每个链接发送请求，访问 Telegram 页面
        for link in unique_links:
            yield scrapy.Request(link, callback=self.parse_telegram, meta={'link': link})

    def parse_telegram(self, response):
        url = response.url

        # 如果页面中包含提示信息则跳过该链接
        if "If you have Telegram, you can contact" in response.text:
            self.logger.info("跳过链接（包含联系提示）: " + url)
            return

        # 提取判断依据内容 extra_info
        extra_info = response.xpath('string(//div[contains(@class, "tgme_page_extra")])').get()
        extra_info = extra_info.strip() if extra_info else ""

        # 提取页面标题作为名称
        title = response.xpath('string(//div[contains(@class, "tgme_page_title")])').get()
        title = title.strip() if title else url.split("/")[-1]

        # 根据 extra_info 判断分类：
        # 如果 extra_info 以 "@" 开头，则归为机器人
        # 如果 extra_info 包含 "subscribers"，归为频道
        # 如果 extra_info 包含 "members"，归为群组
        category = None
        if extra_info.startswith("@"):
            category = "机器人"
        elif "subscribers" in extra_info.lower():
            category = "频道"
        elif "members" in extra_info.lower():
            category = "群组"
        else:
            self.logger.info("无法判断分类，跳过链接: " + url)
            return

        # 存储分类结果
        self.categories[category].append((title, url))
        self.logger.info(f"添加 {category}：`{title}` - {url}")

    def closed(self, reason):
        # 计算各分类及总数
        count_channel = len(self.categories["频道"])
        count_group = len(self.categories["群组"])
        count_bot = len(self.categories["机器人"])
        total_count = count_channel + count_group + count_bot

        md_lines = []
        # 第一行添加总体统计信息
        md_lines.append(f"总计: 频道({count_channel}), 群组({count_group}), 机器人({count_bot}) 共({total_count})")
        md_lines.append("")

        # 分别写入各分类信息
        for cat in ["频道", "群组", "机器人"]:
            count = len(self.categories[cat])
            md_lines.append(f"## {cat}({count})")
            for name, url in self.categories[cat]:
                md_lines.append(f"- `{name}`: {url}")
            md_lines.append("")  # 添加空行

        md_content = "\n".join(md_lines)
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        self.logger.info("爬虫执行完毕，结果已写入 output.md")
