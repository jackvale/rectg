import scrapy
from tg_spider.items import TgSpiderItem


class MyBaseSpider(scrapy.Spider):
    def parse_tg(self, response):
        item = TgSpiderItem()
        item['name'] = response.xpath('//div[@class="tgme_page"]//div[@class="tgme_page_title"]/span/text()').get(
            default='')

        user_name = response.xpath('//div[@class="tgme_page"]//div[@class="tgme_page_action"]/a/@href').get(
            default='')
        if user_name != '':
            try:
                item['user_name'] = user_name.split('domain=')[1]
            except:
                item['user_name'] = user_name
        else:
            item['user_name'] = user_name

        item['avatar'] = ''
        item['avatar_url'] = response.xpath('//div[@class="tgme_page"]//img[@class="tgme_page_photo_image"]/@src').get(
            default='')
        item['description'] = response.xpath(
            '//div[@class="tgme_page"]//div[@class="tgme_page_description"]/text()').get(default='')
        item['extra'] = response.xpath('//div[@class="tgme_page"]//div[@class="tgme_page_extra"]/text()').get(
            default='')
        item['action'] = response.xpath('//div[@class="tgme_page"]//div[@class="tgme_page_action"]/a/@href').get(
            default='')

        item['action_title'] = response.xpath('//div[@class="tgme_page"]//div[@class="tgme_page_action"]/a/text()').get(
            default='')
        link = response.xpath(
            '//div[@class="tgme_page"]//div[@class="tgme_page_context_link_wrap"]/a/@href').get(default='')

        if link != '':
            try:
                item['link'] = 'https://t.me/' + link.split('/s/')[1]
            except:
                item['link'] = link
        else:
            item['link'] = link

        item['link_title'] = response.xpath(
            '//div[@class="tgme_page"]//div[@class="tgme_page_context_link_wrap"]/a/text()').get(default='')
        yield item


# name = "tel-gram.com"
class TelGramSpider(MyBaseSpider):
    name = "tel-gram.com"
    start_urls = ['https://tel-gram.com/']

    def parse(self, response, **kwargs):
        for quote in response.xpath('//div[@class="url-body default "]'):
            tg_url = quote.xpath('./a/@data-url').get()
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "tgnav.github.io"
class TgnavSpider(MyBaseSpider):
    name = "tgnav.github.io"
    start_urls = ['https://tgnav.github.io/']

    def parse(self, response, **kwargs):
        for quote in response.xpath('//div[@class="url-body default"]'):
            tg_url = quote.xpath('./a/@href').get().split("=")[1]
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "www.dianbao.la"
class DianbaoSpider(MyBaseSpider):
    name = "www.dianbao.la"
    start_urls = ['https://www.dianbao.la/']

    def parse(self, response, **kwargs):
        for url in response.xpath('//div[@id="mainContent"]/div[@class="fe"]/div/a/@href').getall():
            if url:
                yield scrapy.Request(url=url, callback=self.parse_next)

    def parse_next(self, response):
        tg_url = response.xpath('//div[@class="zwtit"]/div/a/@href').get()
        if tg_url:
            yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "smsgou.com"
class SmsgouSpider(MyBaseSpider):
    name = "smsgou.com"
    start_urls = ['https://smsgou.com/']

    def parse(self, response, **kwargs):
        for href in response.xpath(
                '//div[@class="content"]//div[starts-with(@class,"slider_menu")]//li[contains(@class,"nav-item")]/a/@href').getall():
            page_id = href.split("-")[-1]
            next_url = "https://smsgou.com/wp-admin/admin-ajax.php?id={}&taxonomy=favorites&action=load_home_tab&post_id=0&sidebar=0".format(
                page_id)
            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse_next)

    def parse_next(self, response):
        for tg_url in response.xpath('//div[starts-with(@class,"url-body")]/a/@data-url').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "tgdriver.com"
class TgdriverSpider(MyBaseSpider):
    name = "tgdriver.com"
    start_urls = ['https://tgdriver.com/']

    def parse(self, response, **kwargs):
        for href in response.xpath(
                '//div[@id="content"]//li[@class="pagenumber nav-item"]/a/@href').getall():
            page_id = href.split("-")[-1]
            next_url = "https://tgdriver.com/wp-admin/admin-ajax.php?id={}&taxonomy=favorites&action=load_home_tab&post_id=0&sidebar=0".format(
                page_id)
            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse_next)

    def parse_next(self, response):
        for tg_url in response.xpath('//div[starts-with(@class,"url-body")]/a/@data-url').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "itgoyo"
class ItgoyoSpider(MyBaseSpider):
    name = "itgoyo"
    start_urls = ['https://github.com/itgoyo/TelegramGroup/blob/master/README.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//main//li//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "iyideng"
class IyidengSpider(MyBaseSpider):
    name = "iyideng"
    start_urls = ['https://iyideng.net/note/telegram-group-channel-and-robot-summary.html']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//main/article/div//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "jichangtuijian.com"
class JichangtuijianSpider(MyBaseSpider):
    name = "jichangtuijian.com"
    start_urls = [
        'https://jichangtuijian.com/telegram%E7%94%B5%E6%8A%A5%E9%A2%91%E9%81%93%E7%BE%A4%E7%BB%84%E6%8E%A8%E8%8D%90.html']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[@class="markdown-body"]/p/a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "justmysocks.cc"
class JustmysocksSpider(MyBaseSpider):
    name = "justmysocks.cc"
    start_urls = ['https://justmysocks.cc/309.html']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[@class="article"]//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "pandavpnpro.com"
class PandavpnproSpider(MyBaseSpider):
    name = "pandavpnpro.com"
    start_urls = ['https://pandavpnpro.com/blog/zh-cn/telegram-group-channel-bot']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[@class="article-details"]//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)


# name = "qianghub.com"
class QianghubSpider(MyBaseSpider):
    name = "qianghub.com"
    start_urls = ['https://qianghub.com/telegram-group/']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//main//article//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_tg)
