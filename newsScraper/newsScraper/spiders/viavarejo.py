# -*- coding: utf-8 -*-
import scrapy
import locale
from w3lib.html import remove_tags
from urllib.parse import unquote
from datetime import datetime
from newsScraper.items import NoticiaLink, Noticia


class ViavarejoSpider(scrapy.Spider):
    name = 'viavarejo'
    # allowed_domains = ['https://www.google.com/search?hl=pt&biw=1366&bih=589&tbs=sbd%3A1&tbm=nws&q=VVAR3']
    start_urls = ['https://www.google.com/search?hl=pt&biw=1366&bih=589&tbs=sbd%3A1&tbm=nws&q=VVAR3/']

    def parse(self, response):
        urls = response.css(".kCrYT > a::attr(href)").getall() 
        urls = list(map(lambda x : x[7:].split('&sa=')[0],urls))
        urls = self.remove_duplicates(urls)
        urls = [unquote(x) for x in urls]

        sites_names = response.css('.UPmit::text').getall()

        links_noticias =  [ NoticiaLink(site=sites_names[i],url=urls[i]) for i in range(0,len(urls)) ]

        for link in links_noticias:
            if 'Estadão' in link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_estadao,
                    cb_kwargs=dict(info=link))
            elif 'Valor Invest' in link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_valorinveste,
                    cb_kwargs=dict(info=link))
            elif 'Investimentos e Notícias' in link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_investimento_noticias,
                    cb_kwargs=dict(info=link))
            elif 'Money Invest' in link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_money_invest,
                    cb_kwargs=dict(info=link))
            elif 'Money Times' == link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_money_times,
                    cb_kwargs=dict(info=link))
            elif 'Advfn' == link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_advfn,
                    cb_kwargs=dict(info=link))
            elif 'SpaceMoney' == link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_spacemoney,
                    cb_kwargs=dict(info=link))
            else:
               yield link

    def remove_duplicates(self, urls: list) -> list:
        unique_urls = []
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
        return unique_urls

    def parse_estadao(self, response, info):
        content = response.xpath("//div[@class='n--noticia__content content']/p").getall()
        content = ''.join([remove_tags(x) for x in content])

        author = response.css('.n--noticia__state p span::text').get(default='notfound')

        date = response.css('.n--noticia__state p::text').getall()[-1].strip()
        date = datetime.strptime(date, '%d de %B de %Y | %Hh%M')

        news_obj = {
            'title': response.css('.n--noticia__title::text').get(),
            'content': content,
            'date': date,
            'author': author if author != 'notfound' else response.css('.n--noticia__state-title::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)

    def parse_valorinveste(self, response, info):
        date = response.css('time::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        news_obj = {
            'title': response.css('.content-head__title::text').get(),
            'content': ''.join([remove_tags(x) for x in response.css('article p').getall()]),
            'date': date, #response.css('time::text').get().strip()
            'author': response.css('.content-publication-data__from::attr(title)').get(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)

    def parse_investimento_noticias(self, response, info):
        content = response.css('.itemIntroText p').getall() +\
            response.css('.itemFullText p').getall()
        content = ''.join([remove_tags(x) for x in content])

        date = response.css('time::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        news_obj = {
            'title': response.xpath('//header/h1/text()').get(),
            'content': content,
            'date': date, #response.css('time::text').get().strip()
            'author': 'None',
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)

    def parse_money_invest(self, response, info):
        date = response.css('time::attr(datetime)').get()
        date = datetime.strptime(date, "%Y-%m-%d")
        news_obj = {
            'title': response.css('.mvp-post-title::text').get(),
            'content': ''.join([remove_tags(x) for x in response.css('#mvp-content-main p').getall()]),
            'date': date, #response.css('time::text').get().strip()
            'author': 'None',
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)

    def parse_money_times(self, response, info):
        date = response.css('.single-meta__date::text').get().strip()
        date = datetime.strptime(date, '%d/%m/%Y - %H:%M')
        news_obj = {
            'title': response.css('.single__title::text').get().strip(),
            'content': ''.join([remove_tags(x) for x in response.css('.single__text p').getall()]),
            'date': date,
            'author': response.css('.single-meta__author a::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)

    def parse_advfn(self, response, info):
        date = response.css('time::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')

        news_obj = {
            'title': response.css('.post-title::text').get().strip(),
            'content': remove_tags(''.join(response.css('.post-content p').getall())),
            'date': date,
            'author': response.css('.posted-by a::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)

    def parse_spacemoney(self, response, info):
        date = response.css('.post-published::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        news_obj = {
            'title': response.css('.post-title::text').get(),
            'content': remove_tags(''.join(response.css('.single-post-content p').getall())),
            'date': date,
            'author': response.css('.post-author-name b::text').get(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'
        }
        yield Noticia(news_obj)