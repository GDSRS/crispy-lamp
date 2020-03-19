from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

process.crawl('newsspider', max_num_pgs=10)
# crawler = next(iter(process._crawlers))
process.start()
