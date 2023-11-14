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


class PagejSpider(scrapy.Spider):
    name = "pagej"
    allowed_domains = ["google.com"]
    start_urls = ["https://www.google.com/"]
    base_url = "https://www.pagesjaunes.fr"
    old_url = ""

    user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/118.0.2088.88',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Vivaldi/6.4.3160.41',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        ]
    user_agent = random.choice(user_agents)


    def __init__(self, *args, **kwargs):
        super(PagejSpider, self).__init__(*args, **kwargs)

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
    
    def rotate_proxy_and_user_agent(self):
        # Set up the driver with the new proxy and user agent
        proxy = self.proxies[0]
        options = self.driver.options
        options.add_argument(f'--proxy-server={proxy}')
        options.add_argument(f'user-agent={self.user_agent}')
    
    def parse(self, response, next_page=None):
        print('🕸️  Parsing')
        if next_page is None: 
            self.driver.get("https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui=creche&ou=Paris%20%2875%29&idOu=L07505600&page=44&contexte=hy7zwbpZSMHUpVqgxpEkl0EctOb6nJJQMR5z%2BTYj9nteQBFQQzOryVgG66OrlgP/tRoJa/wyZt9wOp2zAprUc195dKn8R2IZS6fMh15aky/cJAuiVnIH2wLlmdU3hEi/r//5n6YOW9ABwlyXtHYYXOhT1EP3a91yIrlxPZnt34ntQXpNkEZrnegl6pfCeCvwNFhF4m7KqnNbpltuIjBNdCXcBM1EkZBveYSc9/kYjlzIvwBUJM1hgvg/s8Hvj0qd/cWjwCHKdKv9B0iI2HRFWwwR/7H86O1a4itCRjJBoScJtVU%2B72KRut9XR/StuLsX&quoiQuiInterprete=creche")
        else:
            self.driver.quit()
            time.sleep(random.randint(2, 5))
            self.run_stealth()
            print('Getting Next page')
            self.driver.get(next_page)
        self.driver.save_screenshot("opensea.png")
        time.sleep(random.randint(2, 5))
        self.old_url = self.driver.current_url
        website = self.driver.page_source
        results = BeautifulSoup(website, 'html.parser')

        hotel_links = results.select('.bi-content a[href*="pros/"]')
        # hotel_links = results.select('.results a[href*="pros/"]')
        if hotel_links:
            print('Len of Hotel Links: ', len(hotel_links))
            for link in hotel_links:
                # link.find("a",{"class":"bi-denomination"}).get('href')
                href = link.get('href')
                target_url = self.base_url + href
                print(target_url)
                time.sleep(random.randint(2, 5))
                self.driver.get(target_url)
                time.sleep(random.randint(5, 15))

                html_content  = self.driver.page_source
                html_response = HtmlResponse(self.driver.current_url, body=html_content, encoding='utf-8')

                scroll_port = random.randint(300, 800)
                Actions.scroll_page('down', scroll_port)

                time.sleep(random.uniform(0.6, 1.5))
                yield from self.scrape_content(html_response)

        print(self.driver.execute_script("return navigator.userAgent;"))
        time.sleep(random.uniform(0.6, 1.5))
        self.driver.get(self.old_url)
        time.sleep(random.uniform(0.5, 2.5))

        # Check for Pagination
        while True:
            try:
                wait = WebDriverWait(self.driver, 15)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a#pagination-next")))
            except:
                self.driver.refresh()
            
            time.sleep(random.uniform(0.5, 1.5))
            try:
                next_page_link = self.driver.find_element(By.CSS_SELECTOR, "a#pagination-next")
            except NoSuchElementException:
                print('NO NEXT PAGE FOUND')

            try:
                popup = self.driver.find_element(By.ID, 'didomi-notice-agree-button')
                time.sleep(random.uniform(0.5, 1.5))
                ActionChains(self.driver)\
                    .click(popup)\
                    .perform()
            except:
                pass
            
            if next_page_link:
                time.sleep(random.uniform(0.5, 2.7))
                ActionChains(self.driver)\
                    .move_to_element_with_offset(next_page_link, random.randint(2, 12), random.randint(0, 9))\
                    .perform()
                
                
                ActionChains(self.driver)\
                    .click(next_page_link)\
                    .perform()
                
                
                current_url = self.driver.current_url  
                print('Current URL', current_url)
                yield from self.parse(response, current_url)

            else:
                break


    def scrape_content(self, response_data):
        results = BeautifulSoup(response_data.body, 'html.parser')

        try:
            name = results.find("h1",{"class":"noTrad"}).text
        except:
            name = ''

        postal_code = ""
        try:
            address_element = results.select_one('.address-container span.noTrad')
            if address_element:
                address = address_element.text
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
        yield {
            'Name': name,
            'Address': address,
            'Postal Code': postal_code,
            'Website': website,
            'Telephone': tel
            # 'Stars': stars,
            # 'Tariffs': all_tariffs
        }
