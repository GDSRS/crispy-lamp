# -*- coding: utf-8 -*-
import scrapy
import locale
from w3lib.html import remove_tags
from urllib.parse import unquote
from datetime import datetime, timezone
from newsScraper.items import NoticiaLink, Noticia

locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

class ViavarejoSpider(scrapy.Spider):
    name = 'viavarejo'
    # allowed_domains = ['https://www.google.com/search?hl=pt&biw=1366&bih=589&tbs=sbd%3A1&tbm=nws&q=VVAR3']
    start_urls = ['https://www.google.com/search?q=VVAR3&hl=pt&tbs=sbd:1&tbm=nws']

    def __init__(self, max_num_pgs=3, **kwargs):
        self.MAX_NUM_PAG = max_num_pgs
        self.page_number = 0
        super().__init__(**kwargs)

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
            elif 'Investing' in link.get('site') and 'analysis' not in link.get('site'): #descarta análises
                yield response.follow(link.get('url'), callback=self.parse_investing,
                    cb_kwargs=dict(info=link))
            elif 'EXAME' in link.get('site'): #descarta análises
                yield response.follow(link.get('url'), callback=self.parse_exame,
                    cb_kwargs=dict(info=link))
            elif 'Suno Notícias' == link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_sunoresearch,
                    cb_kwargs=dict(info=link))
            elif 'InfoMoney' == link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_infomoney,
                    cb_kwargs=dict(info=link))
            elif 'Seu Dinheiro' == link.get('site'):
                yield response.follow(link.get('url'), callback=self.parse_seudinheiro,
                    cb_kwargs=dict(info=link))
            else:
               yield link

        self.page_number+=1

        next_page = response.css('.nBDE1b::attr(href)').getall()[-1]
        if next_page is not None and self.page_number < self.MAX_NUM_PAG:
            print('Número da pagina %i' % self.page_number, next_page)
            yield response.follow(next_page, callback=self.parse)

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
            'tick': 'VVAR3'
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
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.mvp-post-title::text').get(),
            'content': remove_tags(''.join(response.css('#mvp-content-main p').getall())),
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
        date = date.replace(tzinfo=timezone.utc)
        
        news_obj = {
            'title': response.css('.single__title::text').get().strip(),
            'content': remove_tags(''.join(response.css('.single__text p').getall())),
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

    def parse_investing(self, response, info):
        date = response.css('.contentSectionDetails span::text').get()
        date = datetime.strptime(date,'%d.%m.%Y %H:%M')
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.articleHeader::text').get(),
            'content': remove_tags(''.join(response.css('.articlePage p').getall())),
            'data': date,
            'author': 'Investing',
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'   
        }
        yield Noticia(news_obj)

    def parse_exame(self, response, info):
        date = response.css('.article-date span::text').get().strip()
        date = datetime.strptime(date,'%d %b %Y, %Hh%M')
        date = date.replace(tzinfo=timezone.utc)

        news_obj = {
            'title': response.css('.article-title::text').get(),
            'content': remove_tags(''.join(response.css('.article-content p').getall())),
            'data': date,
            'author': response.css('.author-element::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'   
        }
        yield Noticia(news_obj)

    def parse_sunoresearch(self, response, info):
        date = response.css('.published::attr(datetime)').get()
        date = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S%z')

        news_obj = {
            'title': response.css('.entry-title::text').get(),
            'content': remove_tags(''.join(response.css('.single-body p').getall())).replace('\n',''),
            'data': date,
            'author': response.css('.entry-author__name::text').get(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'   
        }
        yield Noticia(news_obj)

    def parse_infomoney(self, response, info):
        date = response.css('.published::attr(datetime)').get()
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')

        news_obj = {
            'title': response.css('.page-title-1::text').get(),
            'content': remove_tags(''.join(response.css('.article-content p').getall())).strip(),
            'data': date,
            'author': response.css('.author-name a::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'   
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
            'data': date,
            'author': response.css('.author-bio__title::text').get().strip(),
            'url': info['url'],
            'site': info['site'],
            'tick': 'VVAR3'   
        }
        yield Noticia(news_obj)
