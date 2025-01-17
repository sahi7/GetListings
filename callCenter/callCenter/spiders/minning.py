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
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager 
from selenium_stealth import stealth

class MinningSpider(scrapy.Spider):
    name = "minning"
    allowed_domains = ["www.cryptominerbros.com"]
    start_urls = ["https://www.cryptominerbros.com/"]

    user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/118.0.2088.88',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Vivaldi/6.4.3160.41',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        ]
    user_agent = random.choice(user_agents)
    
    def __init__(self, *args, **kwargs):
        super(MinningSpider, self).__init__(*args, **kwargs)

        print('🧠  Starting engine')
        chrome = webdriver.ChromeOptions()
        # chrome.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome)

    def parse(self, response, next_page=None):
        print('🕸️  Parsing')
        if next_page is None: 
            self.driver.get("https://www.cryptominerbros.com/shop/?orderby=date")
        else:
            self.driver.quit()
