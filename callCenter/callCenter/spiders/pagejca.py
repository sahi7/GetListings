import scrapy
import urllib.parse
from bs4 import BeautifulSoup


class PagejcaSpider(scrapy.Spider):
    name = "pagejca"
    allowed_domains = ["www.pagesjaunes.ca"]
    start_urls = ["https://www.pagesjaunes.ca/search/si/1/Studio+Photo/Abitibi-Temiscamingue+QC"]
    ville = "Abitibi-Temiscamingue+QC"
    max_pages = 1

    def start_requests(self):
        for page_number in range(1, self.max_pages + 1):
            url = f'https://www.pagesjaunes.ca/search/si/{page_number}/Studio+Photo/Abitibi-Temiscamingue+QC'
            yield scrapy.Request(url=url, meta={'page_number': page_number}, callback=self.parse)

    def parse(self, response):
        page_number = response.meta.get('page_number')
        website = BeautifulSoup(response.text, "html.parser")
        
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
            try:
                postal_code = block.find('span', {'itemprop': 'postalCode'}).text
            except:
                postal_code = ''
            
            
            # if not redirected_url or redirected_url == '':
            data = {
                    'Page': page_number,
                    'Name': title,
                    'Address': full_address,
                    'Postal Code': postal_code,
                    'Website': redirected_url,
                    'Telephone': tel,
                    'Ville': self.ville
                }
                
            yield data


