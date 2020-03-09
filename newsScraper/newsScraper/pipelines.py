# -*- coding: utf-8 -*-

# Define your item pipelines here
from scrapy.exceptions import DropItem
import requests
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class NewsscraperPipeline(object):
    def open_spider(self, spider):
        self.json_data = []

    def close_spider(self, spider):
        for news in self.json_data:
            news['date'] = news['date'].strftime('%d-%m-%Y %H:%M')
            requests.post('http://localhost:5000/', json=dict(news))

    def process_item(self, item, spider):
        if item.get('content'):
            self.json_data.append(item)
            return item
        else:
            raise DropItem('Missing content in %s' % item)

