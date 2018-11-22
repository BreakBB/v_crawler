BOT_NAME = 'vCrawler'

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.1

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'v_crawl.pipelines.JsonLinesExportPipeline': 100,
}

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

FEED_FORMAT = 'json'
