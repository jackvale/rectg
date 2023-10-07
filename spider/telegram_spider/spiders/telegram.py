import scrapy
from telegram_spider.items import TelegramSpiderItem
from datetime import datetime
from bs4 import BeautifulSoup


class BaseSpider(scrapy.Spider):
    def parse_telegram_info(self, response):

        item = TelegramSpiderItem()

        action = response.xpath('//div[@class="tgme_page_action"]/a/@href').get()
        extra = response.xpath('//div[@class="tgme_page_extra"]/text()').get()

        item['user_name'] = None
        item['link'] = None
        try:
            user_name = action.split('domain=')[1]
            item['user_name'] = user_name
            item['link'] = 'https://t.me/' + user_name
        except:
            pass

        item['nick_name'] = response.xpath('//div[@class="tgme_page_title"]/span/text()').get()
        item['avatar_url'] = response.xpath('//img[@class="tgme_page_photo_image"]/@src').get()
        item['resolve_url'] = action

        item['members'] = None
        item['subscribers'] = None
        item['tg_type'] = None
        item['category'] = None
        if extra and 'subscribers' in extra:
            item['tg_type'] = 1
            try:
                item['subscribers'] = int(extra.strip().split('subscribers')[0].replace(' ', ''))
            except:
                pass
        elif extra and 'members' in extra:
            item['tg_type'] = 2
            try:
                item['members'] = int(extra.strip().split('members')[0].replace(' ', ''))
            except:
                pass
        elif extra and '@' in extra:
            item['tg_type'] = 3

        biography_html = response.xpath('//div[contains(@class,"tgme_page_description")]').get()

        if biography_html:
            biography = BeautifulSoup(biography_html, 'html.parser')
            item['biography'] = biography.get_text(';', strip=True)
        else:
            item['biography'] = None

        item['create_time'] = datetime.now()
        item['update_time'] = datetime.now()

        yield item


# add
class AddSpider(BaseSpider):
    name = "add"
    start_urls = ['https://t.me/feiyu123']

    def parse(self, response, **kwargs):
        yield scrapy.Request(response.url, callback=self.parse_telegram_info)


# tgnav
class TgnavSpider(BaseSpider):
    name = "tgnav"
    start_urls = ['https://tgnav.github.io/']

    def parse(self, response, **kwargs):
        results = response.xpath('//div[@class="url-body default"]/a[contains(@href,"/go?url=")]/@href').getall()
        for res in results:
            try:
                user_name = res.split('/go?url=')[1]
                url = 'https://t.me/' + user_name
                yield scrapy.Request(url, callback=self.parse_telegram_info)
            except:
                pass


# dianbao
class DianbaoSpider(BaseSpider):
    name = "dianbao"
    start_urls = ['https://www.dianbao.la/']

    def parse(self, response, **kwargs):
        for url in response.xpath('//div[@id="mainContent"]/div[@class="fe"]/div/a/@href').getall():
            if url:
                yield scrapy.Request(url=url, callback=self.parse_next)

    def parse_next(self, response):
        tg_url = response.xpath('//div[@class="zwtit"]/div/a/@href').get()
        if tg_url:
            yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# telgram
class TelGramSpider(BaseSpider):
    name = "telgram"
    start_urls = ['https://tel-gram.com/']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[contains(@class,"url-body")]/a/@data-url').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# smsgou
class SmsgouSpider(BaseSpider):
    name = "smsgou"
    start_urls = ['https://smsgou.com/']

    def parse(self, response, **kwargs):
        for href in response.xpath(
                '//div[@class="content"]//div[starts-with(@class,"slider_menu")]//li[contains(@class,"nav-item")]/a/@href').getall():
            try:
                page_id = href.split("-")[-1]
                next_url = "https://smsgou.com/wp-admin/admin-ajax.php?id={}&taxonomy=favorites&action=load_home_tab&post_id=0&sidebar=0".format(
                    page_id)
                if next_url:
                    yield scrapy.Request(url=next_url, callback=self.parse_next)
            except:
                pass

    def parse_next(self, response):
        for tg_url in response.xpath('//div[starts-with(@class,"url-body")]/a/@data-url').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# tgdriver
class TgdriverSpider(BaseSpider):
    name = "tgdriver"
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
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# itgoyo
class ItgoyoSpider(BaseSpider):
    name = "itgoyo"
    start_urls = ['https://github.com/itgoyo/TelegramGroup/blob/master/README.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//main//li//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# iyideng
class IyidengSpider(BaseSpider):
    name = "iyideng"
    start_urls = ['https://iyideng.net/note/telegram-group-channel-and-robot-summary.html']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//main/article/div//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# jichangtuijian
class JichangtuijianSpider(BaseSpider):
    name = "jichangtuijian"
    start_urls = [
        'https://jichangtuijian.com/telegram%E7%94%B5%E6%8A%A5%E9%A2%91%E9%81%93%E7%BE%A4%E7%BB%84%E6%8E%A8%E8%8D%90.html']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[@class="markdown-body"]/p/a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# justmysocks
class JustmysocksSpider(BaseSpider):
    name = "justmysocks"
    start_urls = ['https://justmysocks.cc/309.html']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[@class="article"]//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# pandavpnpro
class PandavpnproSpider(BaseSpider):
    name = "pandavpnpro"
    start_urls = ['https://pandavpnpro.com/blog/zh-cn/telegram-group-channel-bot']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//div[@class="article-details"]//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# qianghub
class QianghubSpider(BaseSpider):
    name = "qianghub"
    start_urls = ['https://qianghub.com/telegram-group/']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//main//article//a[contains(@href,"t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# telegramlist
class TelegramlistSpider(BaseSpider):
    name = "telegramlist"
    start_urls = ['https://github.com/telegramlist/telegramlist/blob/master/README.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//article//a[@rel="nofollow"]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# GodFatherClover
class GodFatherCloverSpider(BaseSpider):
    name = "GodFatherClover"
    start_urls = ['https://github.com/GodFatherClover/TelegramChannel/blob/main/README.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//article//a[@rel="nofollow"]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# Mrxn
class MrxnSpider(BaseSpider):
    name = "Mrxn"
    start_urls = ['https://github.com/Mr-xn/TG/blob/master/TG-Group.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//article//a[@rel="nofollow"]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# FandGroup
class FandGroupSpider(BaseSpider):
    name = "FandGroup"
    start_urls = ['https://github.com/FandGroup/FandGroup.github.io/blob/main/README.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//article//a[@rel="nofollow"][starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# Barneybook
class BarneybookSpider(BaseSpider):
    name = "Barneybook"
    start_urls = ['https://gist.github.com/Barneybook/e1424b7db8808bf74a4f3007c552d7db#file-telegram_it_group_list-md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//article//a[@rel="nofollow"][starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# tmeseoi
class TmeseoiSpider(BaseSpider):
    name = "tmeseoi"
    start_urls = ['https://github.com/tmeseoi/telegram.github.io/blob/master/README.md']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath('//article//a[@rel="nofollow"][starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# v2ex786320
class V2ex786320Spider(BaseSpider):
    name = "v2ex786320"
    start_urls = ['https://www.v2ex.com/t/786320']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//div[@id="Main"]//a[contains(@rel,"nofollow")][starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# v2ex859082
class V2ex859082Spider(BaseSpider):
    name = "v2ex859082"
    start_urls = ['https://www.v2ex.com/t/859082']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//div[@id="Main"]//a[contains(@rel,"nofollow")][starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# nicechinavpn
class NicechinavpnSpider(BaseSpider):
    name = "nicechinavpn"
    start_urls = ['https://nicechinavpn.com/telegram-tutorial/']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//div[@class="entry-content"]//li[contains(text(),"https://t.me")]/text()').getall():
            if tg_url:
                try:
                    new_tg_url = "https://t.me/" + tg_url.strip().split('https://t.me')[1].split('/')[1]
                    if new_tg_url:
                        yield scrapy.Request(new_tg_url, callback=self.parse_telegram_info)
                except:
                    pass


# moyunews
class MoyunewsSpider(BaseSpider):
    name = "moyunews"
    start_urls = [
        'https://www.moyunews.com/telegram%E7%94%B5%E6%8A%A5%E9%A2%91%E9%81%93%E7%BE%A4%E7%BB%84%E6%9C%BA%E5%99%A8%E4%BA%BAbot%E6%8E%A8%E8%8D%90/']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//main//p[contains(text(),"@")]/text()').getall():
            if tg_url:

                if '@' in tg_url:
                    try:
                        new_tg_url = "https://t.me/" + tg_url.strip().split('@')[1]
                        if new_tg_url:
                            yield scrapy.Request(new_tg_url, callback=self.parse_telegram_info)
                    except:
                        pass


# congcong0806
class Congcong0806Spider(BaseSpider):
    name = "congcong0806"
    start_urls = [
        'https://congcong0806.github.io/2018/04/24/Telegram/']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//div[@class="container"]//a[contains(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# v2ex206766
class V2ex206766Spider(BaseSpider):
    name = "v2ex206766"
    start_urls = ['https://www.v2ex.com/t/206766']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//div[@id="Main"]//a[contains(@rel,"nofollow")][starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)


# kejileida
class KejileidaSpider(BaseSpider):
    name = "kejileida"
    start_urls = ['https://kejileida.net/3914']

    def parse(self, response, **kwargs):
        for tg_url in response.xpath(
                '//article//a[starts-with(@href,"https://t.me")]/@href').getall():
            if tg_url:
                yield scrapy.Request(tg_url, callback=self.parse_telegram_info)