# -*- coding: utf-8 -*-
import scrapy
import locale
from w3lib.html import remove_tags
from urllib.parse import unquote
from datetime import datetime, timezone
import logging
from newsScraper.items import NoticiaLink, Noticia

from .basespider import BasespiderSpider

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

class ViavarejoSpider(BasespiderSpider):
    name = 'viavarejo'
    # allowed_domains = ['https://www.google.com/search?hl=pt&biw=1366&bih=589&tbs=sbd%3A1&tbm=nws&q=VVAR3']
    start_urls = ['https://www.google.com/search?q=VVAR3&hl=pt&tbs=sbd:1&tbm=nws']

    def __init__(self, max_num_pgs=3, **kwargs):
        self.MAX_NUM_PAG = max_num_pgs
        self.page_number = 0
        super().__init__(**kwargs)

    def parse(self, response):
        urls = self.get_search_page_urls(response)
        sites_names = response.css('.UPmit::text').getall()

        links_noticias =  [ NoticiaLink(site=sites_names[i],url=urls[i], tick='VVAR3') for i in range(0,len(urls)) ]
        # logging.debug('links_noticias', links_noticias)
        for link in links_noticias:
            for handler in self.site_handlers:
                if handler.get('site_name') in link.get('site'):
                    parse_handler = getattr(self, handler.get('function'), lambda: 'invalid method name')
                    yield response.follow(link.get('url'), callback=parse_handler,
                        cb_kwargs=dict(info=link))
        yield link


        self.page_number+=1
        next_page = response.css('.nBDE1b::attr(href)').getall()[-1]
        if next_page is not None and self.page_number < self.MAX_NUM_PAG:
            yield response.follow(next_page, callback=self.parse)