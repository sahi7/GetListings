import scrapy


class PagejSpider(scrapy.Spider):
    name = "pagej"
    allowed_domains = ["pagejaune.fr"]
    start_urls = ["https://pagejaune.fr"]

    def __init__(self, *args, **kwargs):
        super(GcenterSpider, self).__init__(*args, **kwargs)

        print('🚀  Starting the engine...')

        options = uc.ChromeOptions()
        options.add_argument('--lang=fr')
        options.add_argument('--ignore-certificate-errors')
        
        self.driver = uc.Chrome(options=options, headless=False)

    def parse(self, response):
        pass
