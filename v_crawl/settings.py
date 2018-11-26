BOT_NAME = 'v_crawler'

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'v_crawl.pipelines.JsonLinesExportPipeline': 100,
}

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

FEED_FORMAT = 'json'
