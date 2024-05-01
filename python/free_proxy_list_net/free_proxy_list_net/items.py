# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FreeProxyListNetItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ip_address = scrapy.Field()
    port = scrapy.Field()
    country = scrapy.Field()
    anonymity = scrapy.Field()
    last_checked = scrapy.Field()
