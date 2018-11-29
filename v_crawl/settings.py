BOT_NAME = 'v_crawler'

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'v_crawl.pipelines.JsonLinesExportPipeline': 100,
}

USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

DOWNLOADER_MIDDLEWARES = {
    'v_crawl.middlewares.ProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 200,
    'v_crawl.middlewares.UserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMIddleware': None
}

USER_AGENT_LIST = "user_agents.txt"

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

FEED_FORMAT = 'json'
