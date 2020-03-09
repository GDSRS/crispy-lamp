# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NoticiaLink(scrapy.Item):
	site = scrapy.Field()
	url = scrapy.Field()

class Noticia(NoticiaLink):
	title = scrapy.Field()
	content = scrapy.Field()
	tick = scrapy.Field()
	date = scrapy.Field()
	author = scrapy.Field()