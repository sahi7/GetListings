import scrapy
import requests


class FiverrSpider(scrapy.Spider):
    name = "fiverr"
    allowed_domains = ["www.pv4.webshare.io"]
    start_urls = ["https://ipv4.webshare.io/"]

    custom_settings = {
        'ITEM_PIPELINES': {},  # Exclude all pipelines
        'DOWNLOADER_MIDDLEWARES': {
            'callCenter.middlewares.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400, 
        },
    }

    def parse(self, response):
        
        yield {
            'url': response.url,
            'status': response.status,
            'body': response.body.decode(response.encoding),
        }
