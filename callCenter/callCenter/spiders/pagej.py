import re
import scrapy
from bs4 import BeautifulSoup
import seleniumwire.undetected_chromedriver as uc
from scrapy.http import HtmlResponse


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
        print("Parsing")
        self.driver.get(response.url)
        website = self.driver.page_source
        results = BeautifulSoup(website, 'html.parser')

        hotel_link = results.select('.bi-content')
        for link in hotel_link:
            link.find("a",{"class":"bi-denomination"}).get('href')
            target_url = self.base_url + link
            self.driver.get(target_url)

            html_content  = self.driver.page_source
            html_response = HtmlResponse(self.driver.current_url, body=html_content, encoding='utf-8')

            yield from self.scrape_content(html_response)


    def scrape_content(self, response_data):
        results = BeautifulSoup(response_data.body, 'html.parser')

        try:
            name = results.find("h1",{"class":"noTrad"}).text
        except:
            name = ''

        try:
            address_element = results.select_one('.address-container span.noTrad')
            if address_element:
                address = address_element.text
                # Extract postal code if available
                postal_code = ""
                if address:
                    # Use a regular expression to find a postal code pattern (5 digits)
                    postal_code_match = re.search(r'\b\d{5}\b', address)
                    if postal_code_match:
                        postal_code = postal_code_match.group()
            else:
                address = ''
        except:
            address = ''

        try:
            website = results.select_one('.lvs-container span.value').text
        except:
            website = ''

        try:
            tel = results.find("span",{"class":"coord-numero-inscription"}).text
        except:
            tel = ''

        try:
            stars = results.find("span",{"class":"categorie-libelle"}).text
        except:
            stars = ''

        try:
            tariffs = results.select('#tarif-hotel span.prix')
            tariff_texts = [tariff.get_text() for tariff in tariffs]

            # Join the extracted texts with a comma
            all_tariffs = ', '.join(tariff_texts)
        except:
            all_tariffs = ""

        
        # Yield the scraped results
        yield {
            'Name': name,
            'Address': address,
            'Postal Code': postal_code,
            'Website': website,
            'Telephone': tel,
            'Stars': stars,
            'Tariffs': all_tariffs
        }
