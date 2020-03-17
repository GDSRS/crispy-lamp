# -*- coding: utf-8 -*-

# Define your item pipelines here
import requests
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class NewsscraperPipeline(object):
    def open_spider(self, spider):
        self.json_data = []
        self.file = open('urls_nao_visitadas.jl','ab')
        self.exporter = None

    def close_spider(self, spider):
        self.file.close()
        self.json_data.sort(key=lambda x: x['date'], reverse=True)
        for news in self.json_data:
            news['date'] = news['date'].strftime('%d-%m-%Y %H:%M')
            # r = requests.post('http://localhost:5000/', json=dict(news))
            r = requests.post('https://crispy-lamp-api-heroku.herokuapp.com/', json=dict(news))
            if r.status_code == 201:
                continue
            else:
                print('Notícia %s já foi enviada.' % news['title'])
                print(r.json()['error'])
                return 'error'

    def export_item(self, item):
        if self.exporter == None:
            self.exporter = JsonLinesItemExporter(file=self.file,encoding='utf-8')
        self.exporter.export_item(item)

    def process_item(self, item, spider):
        if item.get('content'):
            self.json_data.append(item)
            return item
        else:
            self.export_item(item)
            raise DropItem('Missing content in %s' % item)

