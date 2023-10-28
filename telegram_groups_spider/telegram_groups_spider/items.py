import scrapy


class TelegramSpiderItem(scrapy.Item):
    user_name = scrapy.Field()
    nick_name = scrapy.Field()
    link = scrapy.Field()
    avatar_url = scrapy.Field()
    resolve_url = scrapy.Field()
    tg_type = scrapy.Field()
    category = scrapy.Field()
    subscribers = scrapy.Field()
    members = scrapy.Field()
    biography = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
