import re, os
import time
import scrapy
import random
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from rules.actions import Actions
from rules.pagejRules import scrape_content, get_links

#Selenium stealth -- https://www.zenrows.com/blog/selenium-stealth#scrape-with-stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager #https://pypi.org/project/webdriver-manager/
from selenium_stealth import stealth
from rules.actions import Actions


class Pagej2Spider(scrapy.Spider):
    name = "pagej2"
    allowed_domains = ["google.com"] # Scrapy can't bypass pagej security
    start_urls = ["https://www.google.com/"] # Use google for easy by pass by scrapy else selenium will not get url
    base_url = "https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui=creche&ou=Grand-Est&idOu=R44&quoiQuiInterprete=creche&page={}"
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
        chrome_profile_path = os.path.abspath('profiles')
        extension_path = os.path.abspath('extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm')
        service = ChromeService(executable_path=ChromeDriverManager().install()) # create a new Service instance and specify path to Chromedriver executable
        
        # options = uc.ChromeOptions()
        options = webdriver.ChromeOptions()
        options.add_argument(f"--load-extension={extension_path}")
        options.add_argument(f"user-data-dir={chrome_profile_path}")
        # options.add_extension(extension_path)
        # options.add_argument("--headless")
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
        web_actions = Actions(self.driver)
        for page_num in range(1, self.num_pages + 1):

            url = self.base_url.format(page_num)
            self.driver.get(url)
            web_actions.scroll_page('down')
            print(f"Scraped page {page_num}")
            
            time.sleep(random.uniform(0.6, 1.5))
            website  = self.driver.page_source
            links = get_links(website)
            for link in links:
                self.driver.get(link)
                time.sleep(random.randint(5, 15))

                html_content  = self.driver.page_source
                html_response = HtmlResponse(self.driver.current_url, body=html_content, encoding='utf-8')
                yield from scrape_content(html_response)

                

    
