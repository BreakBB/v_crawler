from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from v_crawl.spiders.amazon_de_spider import AmazonDeSpider


print("Starting the run of %s" % AmazonDeSpider.name)
print("Timeout is set to %i" % AmazonDeSpider.spider_timeout)

process = CrawlerProcess(get_project_settings())
process.crawl(AmazonDeSpider)
process.start()
