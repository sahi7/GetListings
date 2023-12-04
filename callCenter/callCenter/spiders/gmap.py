import scrapy


class GmapSpider(scrapy.Spider):
    name = "gmap"
    allowed_domains = ["www.google.com"]
    start_urls = ["https://www.google.com/maps/search/clothing+store+in+autriche/"]

    def parse(self, response):
        # name_xpath = '//div[contains(@class, "fontHeadlineSmall")]'
        # address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
        # website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
        # phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
        # reviews_span_xpath = '//span[@role="img"]'