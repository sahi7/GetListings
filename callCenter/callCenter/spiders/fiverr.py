import scrapy
import requests
import random, os, time
from dotenv import load_dotenv
from fake_useragent import UserAgent
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class FiverrSpider(scrapy.Spider):
    name = "fiverr"
    allowed_domains = []
    start_urls = ["https://www.fiverr.com/sonypete"]
    ua = UserAgent(browsers=['edge', 'chrome'])
    user_agent = ua.random
    load_dotenv()
    print(user_agent)

    ENDPOINT = os.getenv('ENDPOINT')
    PORT = os.getenv('PORT')
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')

    custom_settings = {
        'ITEM_PIPELINES': {},
    }

    referers = [
        'https://www.facebook.com',
        'https://www.whatsapp.com',
        'https://www.twitter.com',
        'https://www.instagram.com'
    ]
    Referer = random.choice(referers)


    def __init__(self, *args, **kwargs):
        super(FiverrSpider, self).__init__(*args, **kwargs)

        print('🧠  Starting engine')
        self.rotate_proxy_and_user_agent()
        

    def rotate_proxy_and_user_agent(self):
        # Set up the driver with the new proxy and user agent
        PROXY_ENDPOINT = os.getenv('PROXY_ENDPOINT')
        PROXY_PORT = os.getenv('PROXY_PORT')
        PROXY_USERNAME = os.getenv('PROXY_USERNAME')
        PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')

        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')

        # options = self.driver.options
        # options.add_argument(f'--proxy-server=http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_ENDPOINT}:{PROXY_PORT}')
        options.add_argument(f'user-agent={self.user_agent}')
        options.add_argument(f"--referer={self.Referer}")
        options.add_argument("--auto-open-devtools-for-tabs")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)
        # Get IP address using JavaScript
        self.driver.execute_script("window.open('https://api.ipify.org/')")
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(2)
        ip_page_source = self.driver.execute_script("return document.body.textContent")
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[0])
        # Get the initial headers
        public_ip = requests.get('https://api.ipify.org').text
        user_agent = self.driver.execute_script("return navigator.userAgent")
        response_status = self.driver.execute_script("return document.readyState")
        current_url = self.driver.current_url
        referer_status = self.driver.execute_script("return document.referrer")

        yield {
            'url': current_url,
            'status': response_status,
            'referer': referer_status,
            'ip': ip_page_source,
            'ua': user_agent,
        }

        time.sleep(60)
