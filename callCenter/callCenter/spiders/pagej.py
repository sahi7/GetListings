import re, os, sys
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

        if hasattr(sys, 'argv') and '-o' in sys.argv:
            # Normally, arguments are rep with -a, using -o for hasattr may not be acceptable. There is margin for error here
            output_index = sys.argv.index('-o')
            self.output_filename = sys.argv[output_index + 1] if output_index + 1 < len(sys.argv) else "selenium_state.pkl"
        else:
            self.output_filename = "selenium_state.pkl"

        self.run_stealth()

    def save_state(self, state, filename):
        with open(filename, "wb") as f:
            pickle.dump(state, f)

    def load_state(self, filename):
        try:
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    state = pickle.load(f)
        except FileNotFoundError:
            return None

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
    
    def rotate_proxy_and_user_agent(self):
        # Set up the driver with the new proxy and user agent
        proxy = self.proxies[0]
        options = self.driver.options
        options.add_argument(f'--proxy-server={proxy}')
        options.add_argument(f'user-agent={self.user_agent}')
    
    def parse(self, response, next_page=None):
        print('🕸️  Parsing')
        if next_page is None: 
            state = self.load_state(self.output_filename)
            if state is None:
                self.driver.get("https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui=creche&ou=Ile-de-France&idOu=R11&page=187&contexte=sBof0Z7OI026/jhfe3maxLga7/M08GezCNEYQp5nLUJ/nUVSjldDcc%2BZ%2BLCDliVvZmrl/ViyobEUJMSYceb1dqLd19isAPXPVUXYegX6%2BgDupOcmnLQPMnFC%2BIiWME6XiX2ce/0ignEkVDH6%2BbnOjnQ0GhInLt1NZ6B2kWKggOvMeG3tpUaP4F6j6wvVrdWBTGXcy0MG66WChRYyh5w3lSBhiSmUThB/KPteWrB4MjI5l0HjMAPRhLVLZpr56alCiQcjhimTVYUQks3XbqSWEYiNcJRnKlOXgMNR0q21hgjqSUPDu3QfsPWgXyKLFDkP0XjgtkBT6yhYdTK3QYH5EpcLprx2/FwQ9tB64TvxpOF1bLOH1rRIVueZ2hUFziPauhhzEHuJ/QeHG5QduaGx%2BC8wrM8X7V1Pq%2BenB/h6lca/Lr2s/qks4Z1ltFe6ordUywWLN3FiktZAounjLBhLt15PrL8dK4NEP0SNJb3WvDg0TMeq0960dIb6woGO5vCAazmywEmWXJ2lOMY77R0F9hqEHDHj0B1rrCFlIe6FVL%2BwH42NN%2BzEzz74E8pgvESKNJEdlG5S%2BZTa6TMor6gnY7yxfRdaWXPoBIs9AneVCIH508VboZeYKqIxYh8s0q5Y%2BsYzYDdgHNuPsUM6s2AIER3PR6utSgzoinyk0qujv1hHGwcC7AIdB4ESM/YFUGWBB3MXOBc%2BvrOLM8oU/dt/cSTQs3wMu3%2B1WL4NPdDqrYaByVTrrUoF4whdgeRITUvINp/EK5O4gtG3qQtRL/bit7vkuWcYmo4M2ey3YZ0jxJZneLc3g4qvihUYC/aaokU4JH9v8L1tIWv1rHAEgzJkN7ZOsBDIDdWV37QKkgzibTtWGzDyOx%2BdLnRkV3SKJOW9vg0HYPsKlsic18%2BbclKodUISFZjwr7J/yArqTlfoPn2l1Zt5VwukIXbjUHkoKZExGcuUwh0hJU8EOtzebVb4rIazmBIDbim8cGNLKkQqLtR6MsJCy5YRMvRMq0u6PpwSQupdS/Kso2h36QG6PVKVfUbx%2ByCVI5GKXPirU4xuM8XSYuX%2B0Yyo/DcasBbV/xE4RajD6z9ngZQ38lCujji6hhkvqsbJzs/gFZ4Q%2BQhR5UEgvBjx/f6wT4L03qx/BwJumjmxXEBY4unJr2fzVHkXLMrUjGqpg77LFV0GxJfGAofvoPjrWMrF3QyOpxrhfG0dX5ElNdRbyr0AMrmzc9C10aPLoGeTgeAeTfw6dKrOh18%3D&quoiQuiInterprete=creche")
            else:
                self.driver.get(state["url"])
                for cookie in state["cookies"]:
                    self.driver.add_cookie(cookie)
        else:
            self.driver.quit()
            time.sleep(random.randint(2, 5))
            self.run_stealth()
            print('Getting Next page')
            self.driver.get(next_page)
        self.driver.save_screenshot("opensea.png")
        time.sleep(random.randint(2, 5))
        try:
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
        except:
            # self.save_state(self.output_filename)
            self.save_state({
                "url": self.driver.current_url,
                "cookies": self.driver.get_cookies(),
                }, self.output_filename
            )        

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
