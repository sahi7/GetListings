import scrapy


class PagejcaSpider(scrapy.Spider):
    name = "pagejca"
    allowed_domains = ["www.pagesjaunes.ca"]
    start_urls = ["https://www.pagesjaunes.ca"]

    def parse(self, response):
        pass
