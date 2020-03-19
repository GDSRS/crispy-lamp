# -*- coding: utf-8 -*-
from newsScraper.items import NoticiaLink
from .basespider import BasespiderSpider



class NewsSpider(BasespiderSpider):
    name = 'newsspider'
    start_urls = ['https://www.google.com/search?q=VVAR3&hl=pt&tbs=sbd:1&tbm=nws',
                  'https://www.google.com/search?q=MGLU3&hl=pt&tbs=sbd:1&tbm=nws']

    def __init__(self, max_num_pgs=3, **kwargs):
        self.MAX_NUM_PAG = max_num_pgs
        self.page_number = 0
        super().__init__(**kwargs)

    def parse(self, response):
        tick = response.url[32:37]
        urls = self.get_search_page_urls(response)
        sites_names = response.css('.UPmit::text').getall()

        links_noticias =  [ NoticiaLink(site=sites_names[i],url=urls[i], tick=tick) for i in range(0,len(urls)) ]
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