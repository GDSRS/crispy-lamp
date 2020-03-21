# -*- coding: utf-8 -*-

# Define your item pipelines here
import requests, sys
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class NewsscraperPipeline(object):
    def open_spider(self, spider):
        self.json_data = {}
        self.file = open('urls_nao_visitadas.jl','ab')
        self.exporter = None

    def close_spider(self, spider):
        self.file.close()
        for key in self.json_data:
            tick_specific = self.json_data[key]
            self.sort_dict_list(tick_specific)

        for key in self.json_data:
            tick_specific = self.json_data[key]
            self.send_data_to_api(tick_specific)

    def send_data_to_api(self, tick_specific):
        for key, values in tick_specific.items():
            for news in values:
                news['date'] = news['date'].strftime('%d-%m-%Y %H:%M')
                # r = requests.post('http://localhost:5000/', json=dict(news))
                r = requests.post('https://crispy-lamp-api-heroku.herokuapp.com/', json=dict(news))
                if r.status_code == 201:
                    continue
                elif r.status_code == 500:
                    print('Notícia \" %s \" já foi enviada.' % news['title'])
                    print("JSON: ",r.json())
                    print(r.json()['error'])
                    # return 'error'
                    break
                else:
                    print(r.json()['error'])
                    break

    def process_item(self, item, spider):
        if item.get('content'):
            try:
                tick_specific = self.json_data[item['tick']]
            except KeyError:
                tick_specific = self.json_data[item['tick']] = {}

            try:
                tick_specific[item['site']].append(item)
            except KeyError:#quer dizer que a chave ainda n existe
                tick_specific[item['site']] = [item]
            return item
        else:
            self.export_item(item)
            raise DropItem('Missing content in %s' % item)

    def sort_dict_list(self, tick_specific):
        try:
            # self.json_data.sort(key=lambda x: x['date'], reverse=True)
            for key in tick_specific:
                tick_specific[key].sort(key=lambda x: x['date'], reverse=True)
        except TypeError:
            print(tick_specific)
            sys.exit()

    def export_item(self, item):
        if self.exporter == None:
            self.exporter = JsonLinesItemExporter(file=self.file,encoding='utf-8')
        self.exporter.export_item(item)

