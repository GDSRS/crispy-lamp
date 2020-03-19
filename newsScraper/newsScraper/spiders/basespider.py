# -*- coding: utf-8 -*-
import scrapy
import locale
import logging
from w3lib.html import remove_tags
from urllib.parse import unquote
from datetime import datetime, timezone
from newsScraper.items import NoticiaLink, Noticia

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

class BasespiderSpider(scrapy.Spider):
    name = 'basespider'

    site_handlers = [
        {'site_name': 'Estadão', 'function': 'parse_estadao'},
        {'site_name': 'Valor Invest', 'function': 'parse_valorinveste'},
        {'site_name': 'Investimentos e Notícias', 'function': 'parse_investimento_noticias'},
        {'site_name': 'Money Invest', 'function': 'parse_money_invest'},
        {'site_name': 'Money Times', 'function': 'parse_money_times'},
        {'site_name': 'Advfn', 'function': 'parse_advfn'},
        {'site_name': 'SpaceMoney', 'function': 'parse_spacemoney'},
        {'site_name': 'Investing.com Brasil', 'function': 'parse_investing'},
        {'site_name': 'EXAME', 'function': 'parse_exame'},
        {'site_name': 'Suno Notícias', 'function': 'parse_sunoresearch'},
        {'site_name': 'InfoMoney', 'function': 'parse_infomoney'},
        {'site_name': 'Seu Dinheiro', 'function': 'parse_seudinheiro'},
    ]

    def get_search_page_urls(self, response) -> list: 
        urls = response.css(".kCrYT > a::attr(href)").getall() 
        urls = list(map(lambda x : x[7:].split('&sa=')[0],urls))
        urls = self.remove_duplicates(urls)
        urls = [unquote(x) for x in urls]

        return urls
        

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
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.n--noticia__title::text').get(),
            'content': content,
            'date': date,
            'author': author if author != 'notfound' else response.css('.n--noticia__state-title::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']
        }
        yield Noticia(news_obj)

    def parse_valorinveste(self, response, info):
        date = response.css('time::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        news_obj = {
            'title': response.css('.content-head__title::text').get(),
            'content': remove_tags(''.join(response.css('article p').getall())),
            'date': date, #response.css('time::text').get().strip()
            'author': response.css('.content-publication-data__from::attr(title)').get(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']
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
            'tick': info['tick']
        }
        yield Noticia(news_obj)

    def parse_money_invest(self, response, info):
        date = response.css('time::attr(datetime)').get()
        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.mvp-post-title::text').get(),
            'content': remove_tags(''.join(response.css('#mvp-content-main p').getall())),
            'date': date, #response.css('time::text').get().strip()
            'author': 'None',
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']
        }
        yield Noticia(news_obj)

    def parse_money_times(self, response, info):
        date = response.css('.single-meta__date::text').get().strip()
        date = datetime.strptime(date, '%d/%m/%Y - %H:%M')
        date = date.replace(tzinfo=timezone.utc)
        
        news_obj = {
            'title': response.css('.single__title::text').get().strip(),
            'content': remove_tags(''.join(response.css('.single__text p').getall())),
            'date': date,
            'author': response.css('.single-meta__author a::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']
        }
        yield Noticia(news_obj)

    def parse_advfn(self, response, info):
        news_type = ' '.join(response.css('.category .cat-title a::text').getall())
        if "Análise Técnica" in news_type or "Opinião" in news_type:
            yield info
        else:
            date = response.css('time::attr(datetime)').get()
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')

            news_obj = {
                'title': response.css('.post-title::text').get().strip(),
                'content': remove_tags(''.join(response.css('.post-content p').getall())),
                'date': date,
                'author': response.css('.posted-by a::text').get().strip(),
                'url': info['url'],
                'site': info['site'],
                'tick': info['tick']
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
            'tick': info['tick']
        }
        yield Noticia(news_obj)

    def parse_investing(self, response, info):
        if 'analysis' in response.url:
            yield info
        else:
            date = response.css('.contentSectionDetails span::text').get()
            if len(date) > 16:
                date = response.css('.contentSectionDetails span::text').get()[-17:-1]
            date = datetime.strptime(date,'%d.%m.%Y %H:%M')
            date = date.replace(tzinfo=timezone.utc)

            news_obj = {
                'title': response.css('.articleHeader::text').get(),
                'content': remove_tags(''.join(response.css('.articlePage p').getall())),
                'date': date,
                'author': 'Investing',
                'url': info['url'],
                'site': info['site'],
                'tick': info['tick']   
            }
            yield Noticia(news_obj)

    def parse_exame(self, response, info):
        date = response.css('.article-date span::text').get().strip()
        date = datetime.strptime(date,'%d %b %Y, %Hh%M')
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.article-title::text').get(),
            'content': remove_tags(''.join(response.css('.article-content p').getall())),
            'date': date,
            'author': response.css('.author-element::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']   
        }
        yield Noticia(news_obj)

    def parse_sunoresearch(self, response, info):
        date = response.css('.published::attr(datetime)').get()
        date = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S%z')

        news_obj = {
            'title': response.css('.entry-title::text').get(),
            'content': remove_tags(''.join(response.css('.single-body p').getall())).replace('\n',''),
            'date': date,
            'author': response.css('.entry-author__name::text').get(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']   
        }
        yield Noticia(news_obj)

    def parse_infomoney(self, response, info):
        date = response.css('.published::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')

        news_obj = {
            'title': response.css('.page-title-1::text').get(),
            'content': remove_tags(''.join(response.css('.article-content p').getall())).strip(),
            'date': date,
            'author': response.css('.author-name a::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']   
        }
        yield Noticia(news_obj)

    def parse_seudinheiro(self, response, info):
        date = response.css('.single__date-time::text').get().strip()
        date = date +" "+remove_tags(response.css('.single__time').get()).strip().replace('\t','')[:5]
        date = datetime.strptime(date,'%d de %B de %Y %H:%M')
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.single__title::text').get(),
            'content': remove_tags(''.join(response.css('.single__body p').getall())).strip(),
            'date': date,
            'author': response.css('.author-bio__title::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': info['tick']   
        }
        yield Noticia(news_obj)