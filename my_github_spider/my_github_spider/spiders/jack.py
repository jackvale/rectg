from typing import Any, Iterable

import scrapy
from scrapy import Request
from scrapy.http import Response
import re
from my_github_spider.items import MyGithubSpiderItem


class JackSpider(scrapy.Spider):
    name = "jack"
    allowed_domains = ["github.com", "t.me"]
    start_urls = ["https://github.com/jackhawks/telegram-groups/tree/main"]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        tr_list = response.xpath('//tbody/tr')
        for tr in tr_list:
            tg_url = tr.xpath('./td[1]/a[starts-with(@href,"https://t.me")]/@href').get()
            tg_name = tr.xpath('./td[1]/a[starts-with(@href,"https://t.me")]/text()').get()
            tg_desc = tr.xpath('./td[last()]/text()').get()
            yield scrapy.Request(url=tg_url, callback=self.parse_telegram_page,
                                 meta={'tg_name': tg_name, 'tg_desc': tg_desc})

    def parse_telegram_page(self, response: Response):
        tg_url = response.url
        tg_name = response.meta['tg_name']
        tg_desc = response.meta['tg_desc']
        tg_extra = response.xpath('//div[@class="tgme_page"]/div[@class="tgme_page_extra"]/text()').get()
        (tg_person_num, tg_category) = self.parse_person_number(tg_extra)
        yield MyGithubSpiderItem(tg_url=tg_url, tg_name=tg_name, tg_desc=tg_desc, tg_person_num=tg_person_num,
                                 tg_category=tg_category)

    def parse_person_number(self, extra: str | None):
        if extra:
            trim_str = extra.strip()
            if trim_str.startswith('@'):
                return (None, '机器人')
            else:
                full_trim_str = re.sub(' ', '', trim_str)
                person_number = re.match(r'\d+', full_trim_str).group()
                if 'subscribers' in full_trim_str:
                    return (person_number, '频道')
                elif 'members' in full_trim_str:
                    return (person_number, '群组')
        else:
            return (None, None)
