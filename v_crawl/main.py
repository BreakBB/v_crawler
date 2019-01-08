from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from v_crawl.spiders.amazon_de_spider import AmazonDeSpider
from v_crawl.spiders.amazon_com_spider import AmazonComSpider


print("Starting the run of %s" % AmazonComSpider.name)
print("Timeout is set to %i" % AmazonComSpider.spider_timeout)

process = CrawlerProcess(get_project_settings())
process.crawl(AmazonComSpider)
process.start()
