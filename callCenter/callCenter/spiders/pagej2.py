import re
import time
import scrapy
import random
from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from rules.actions import Actions
#Selenium stealth -- https://www.zenrows.com/blog/selenium-stealth#scrape-with-stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager #https://pypi.org/project/webdriver-manager/
from selenium_stealth import stealth
from rules.actions import Actions


class Pagej2Spider(scrapy.Spider):
    name = "pagej2"
    allowed_domains = ["google.com"]
    start_urls = ["https://www.google.com/"]
    base_url = "https://www.pagesjaunes.fr/chercherlespros?quoiqui=confiserie%20chocolaterie&ou=Auvergne-Rh%C3%B4ne-Alpes&idOu=R84&page={}"
    num_pages = 27
    user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/118.0.2088.88',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Vivaldi/6.4.3160.41',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        ]       

    def __init__(self, *args, **kwargs):
        super(Pagej2Spider, self).__init__(*args, **kwargs)
        print('🚀  Starting the engine...')
        self.run_stealth()

    def run_stealth(self):
        service = ChromeService(executable_path=ChromeDriverManager().install()) # create a new Service instance and specify path to Chromedriver executable
        # options = uc.ChromeOptions()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-extensions') # disable extensions
        options.add_argument('--no-sandbox') # disable sandbox mode
        options.add_argument('--start-maximized') # start the browser window in maximized mode
        options.add_argument('--disable-popup-blocking') # disable pop-up blocking
        options.add_argument('--disable-blink-features=AutomationControlled') # disable the AutomationControlled feature of Blink rendering engine
        options.add_argument(f'user-agent={random.choice(self.user_agents)}') #User Agents can also be set using execute_cdp_cmd
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(service=service, options=options) #driver instance
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # Change the property value of the navigator for webdriver to undefined
        
        stealth(self.driver,
            languages=["fr-FR", "fr"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def parse(self, response):
        self.driver.get(response.url)
        print('🕸️  Parsing 2')
        try:
            
            for page_num in range(1, self.num_pages + 1):

                url = self.base_url.format(page_num)
                self.driver.get(url)
                Actions.scroll_page('down')
                print(f"Scraped page {page_num}")

                

        except Exception as e:
            print(f"Error occurred: {str(e)}")

    def scrape_content(self, response_data):
        results = BeautifulSoup(response_data.body, 'html.parser')
        try:
            name = results.find("h1",{"class":"noTrad"}).text.strip()
            split_name = name.split('\n', 1)  # Split at the first '\n'
            result_name = split_name[0].strip()
        except:
            name = ''
        postal_code = ""
        try:
            address_element = results.select_one('.address-container span.noTrad')
            if address_element:
                address = address_element.text.strip()
                # Extract postal code if available
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
        data = {
            'Name': result_name,
            'Address': address,
            'Postal Code': postal_code,
            'Website': website,
            'Telephone': tel
            # 'Stars': stars,
            # 'Tariffs': all_tariffs
        }
        yield data
