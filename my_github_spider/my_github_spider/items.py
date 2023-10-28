# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyGithubSpiderItem(scrapy.Item):
    tg_url = scrapy.Field()
    tg_name = scrapy.Field()
    tg_desc = scrapy.Field()
    tg_person_num = scrapy.Field()
    tg_category = scrapy.Field()
