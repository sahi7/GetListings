import scrapy
import urllib.parse
from bs4 import BeautifulSoup


class PagejcaSpider(scrapy.Spider):
    name = "pagejca"
    allowed_domains = ["www.pagesjaunes.ca"]
    start_urls = ["https://www.pagesjaunes.ca/search/si/1/magasins+de+v%C3%AAtements/Montreal+Qc"]
    max_pages = 10

    def start_requests(self):
        for page_number in range(1, self.max_pages + 1):
            url = f'https://www.pagesjaunes.ca/search/si/{page_number}/magasins+de+v%C3%AAtements/Montreal+Qc'
            yield scrapy.Request(url=url, meta={'page_number': page_number}, callback=self.parse)

    def parse(self, response):
        page_number = response.meta.get('page_number')
        website = BeautifulSoup(response.text, "html.parser")
        unique_entries = set()
        
        # Extract product links
        product_block = website.select_one('.page__container_wrap .resultList')
        selected_blocks = product_block.find_all(lambda tag: tag.name == 'div' and 'listing' in tag.get('class', []) and 'placementText' not in tag.get('class', []))
        for block in selected_blocks:
            title = block.find('a', class_='listing__name--link').text
            try:
                tel = block.find('a', class_='mlr__item__cta jsMlrMenu').get('data-phone')
            except:
                tel = ''
            try:
                site = block.find('li', class_='mlr__item--website')
                website = site.find('a').get('href')
                redirected_url = urllib.parse.parse_qs(urllib.parse.urlsplit(website).query).get('redirect', [''])[0]
            except:
                redirected_url = ''
            try:
                addr = block.find('span', class_='listing__address--full')
                child_texts = [span.text.strip() for span in addr.find_all('span', class_='jsMapBubbleAddress')]
                full_address = ' '.join(child_texts)
            except:
                full_address = ''
            
            entry_identifier = (tel)
            
            if not redirected_url or redirected_url == '':
                data = {
                        'Page': page_number,
                        'Name': title,
                        'Telephone': tel,
                        'Address': full_address
                    }
                if entry_identifier not in unique_entries:
                    unique_entries.add(entry_identifier)
                    yield data
                else:
                    print("Duplicate result found:", entry_identifier)


