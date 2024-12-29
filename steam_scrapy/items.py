# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AppInfoItem(scrapy.Item):
    name = scrapy.Field()
    id = scrapy.Field()

    developer = scrapy.Field()
    publisher = scrapy.Field()
    release_date = scrapy.Field()

    description = scrapy.Field()
    recent_reviews = scrapy.Field()
    all_reviews = scrapy.Field()

    user_defined_tags = scrapy.Field()
    labels = scrapy.Field()

    languages = scrapy.Field()

    original_price = scrapy.Field()
    discount_final_price = scrapy.Field()


class LanguageItem(scrapy.Item):
    language = scrapy.Field()
    interface = scrapy.Field()
    full_audio = scrapy.Field()
    subtitles = scrapy.Field()


class ReviewItem(scrapy.Item):
    title = scrapy.Field()
    hours = scrapy.Field()
    date_posted = scrapy.Field()
    received_for_free = scrapy.Field()
    refunded = scrapy.Field()
    content = scrapy.Field()