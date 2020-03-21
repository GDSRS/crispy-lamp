# -*- coding: utf-8 -*-
from newsScraper.items import NoticiaLink
from .basespider import BasespiderSpider



class NewsSpider(BasespiderSpider):
    name = 'newsspider'
    start_urls = ['https://www.google.com/search?q=VVAR3&hl=pt&tbs=sbd:1&tbm=nws',
                  'https://www.google.com/search?q=MGLU3&hl=pt&tbs=sbd:1&tbm=nws']

    def __init__(self, max_num_pgs=3, **kwargs):
        self.MAX_NUM_PAG = max_num_pgs
        self.page_number = self.initialize_page_counter()
        super().__init__(**kwargs)

    def initialize_page_counter(self):
        x = {}
        for url in self.start_urls:
            x[url[32:37]] = 0
        return x

    def parse(self, response):
        tick = response.url[32:37]
        urls = self.get_search_page_urls(response)
        sites_names = response.css('.UPmit::text').getall()

        links_noticias = [ NoticiaLink(site=sites_names[i],url=urls[i], tick=tick) for i in range(0,len(urls)) ]

        for link in links_noticias:
            site_name = link.get('site')
            handler_function = self.get_correct_handler(site_name)
            if handler_function != None:
                yield response.follow(link.get('url'), callback=handler_function,
                        cb_kwargs=dict(info=link))
            else:
                yield link


        self.page_number[tick]+=1
        next_page = response.css('.nBDE1b::attr(href)').getall()[-1]
        if next_page is not None and self.page_number[tick] < self.MAX_NUM_PAG:
            yield response.follow(next_page, callback=self.parse)


    def get_correct_handler(self, site):
        for s_handler in self.site_handlers:
            site_name = s_handler.get('site_name')
            if site_name in site:
                return getattr(self, s_handler.get('function'), "erro")
        return None