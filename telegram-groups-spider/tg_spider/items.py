import scrapy


class TgSpiderItem(scrapy.Item):
    name = scrapy.Field()
    user_name = scrapy.Field()
    avatar = scrapy.Field()
    avatar_url = scrapy.Field()
    description = scrapy.Field()
    extra = scrapy.Field()
    action = scrapy.Field()
    action_title = scrapy.Field()
    link = scrapy.Field()
    link_title = scrapy.Field()
