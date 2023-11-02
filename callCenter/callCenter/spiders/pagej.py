import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class PagejSpider(scrapy.Spider):
    name = "pagej"
    allowed_domains = ["google.com"]
    start_urls = ["https://www.google.com/"]
    # base_url = "https://webcache.googleusercontent.com/search?q=cache:https://www.pagesjaunes.fr"
    base_url = "https://www.pagesjaunes.fr"


    def __init__(self, *args, **kwargs):
        super(PagejSpider, self).__init__(*args, **kwargs)

        print('🚀  Starting the engine...')

        options = uc.ChromeOptions()
        options.add_argument('--lang=fr')
        options.add_argument('--ignore-certificate-errors')
        
        self.driver = uc.Chrome(options=options, headless=False)

    
    def parse(self, response, next_page=None):
        print(" 🕸️  Parsing")
        actions = ActionChains(self.driver)
        # self.driver.get("https://webcache.googleusercontent.com/search?q=cache:https://www.pagesjaunes.fr/annuaire/region/provence-alpes-cote-d-azur/hotels")
        if next_page is None:
            self.driver.get("https://www.pagesjaunes.fr/annuaire/region/provence-alpes-cote-d-azur/hotels")
        else:
            print('Getting Next page')
            self.driver.get(next_page)
        website = self.driver.page_source
        results = BeautifulSoup(website, 'html.parser')

        hotel_links = results.select('.bi-content')
        # hotel_links = results.select('.results a[href*="pros/"]')
        for link in hotel_links:
            # link.find("a",{"class":"bi-denomination"}).get('href')
            link.find("a",{"class":"bi-denomination"})
            href = link.get('href')
            target_url = self.base_url + href
            print(target_url)
            self.driver.get(target_url)

            html_content  = self.driver.page_source
            html_response = HtmlResponse(self.driver.current_url, body=html_content, encoding='utf-8')


            yield from self.scrape_content(html_response)


        # Check for Pafination
        next_page_link = results.find('a', {'id': 'pagination-next'})
        if next_page_link:
            actions.context_click(next_page_link).perform()

            clickedhref = next_page_link.get_attribute('href')
            if clickedhref == "#":
                next_page_link.click()
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                next_page_url = self.driver.current_url
            else:
                next_page_href = next_page_link.get('href')
                next_page_url = self.base_url + next_page_href
                print(f"Next page: {next_page_url}")
                self.driver.get(next_page_url)

            yield from self.parse(response, next_page_url)


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
            tel = results.find("span",{"class":"coord-numero"}).text
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
