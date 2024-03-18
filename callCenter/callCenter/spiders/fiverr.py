import scrapy
import requests
import random, os, time
from dotenv import load_dotenv
from fake_useragent import UserAgent
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium_authenticated_proxy import SeleniumAuthenticatedProxy
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


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

        # Initialize SeleniumAuthenticatedProxy
        # Todo @SeleniumAuthenticatedProxy NOT WORKING
        proxy_helper = SeleniumAuthenticatedProxy(proxy_url=f'http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_ENDPOINT}:{PROXY_PORT}')
        
        # Enrich Chrome options with proxy authentication
        proxy_helper.enrich_chrome_options(options)

        # options = self.driver.options
        # options.add_argument(f'--proxy-server=http://{PROXY_ENDPOINT}:{PROXY_PORT}')
        options.add_argument(f'user-agent={self.user_agent}')
        options.add_argument(f"--referer={self.Referer}")
        # options.add_argument("--auto-open-devtools-for-tabs")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)
        # Get IP address using JavaScript
        self.driver.execute_script("window.open('https://api.ipify.org/')")
        self.driver.switch_to.window(self.driver.window_handles[1])
        ip_page_source = self.driver.execute_script("return document.body.textContent")
        self.driver.switch_to.window(self.driver.window_handles[0])
        # Get the initial headers
        public_ip = requests.get('https://api.ipify.org').text
        user_agent = self.driver.execute_script("return navigator.userAgent")
        response_status = self.driver.execute_script("return document.readyState")
        current_url = self.driver.current_url
        referer_status = self.driver.execute_script("return document.referrer")

        # Work starts 
        wait_time = random.uniform(1.5, 7.5)
        scroll_amount = random.randint(50, 100)
        actions = ActionChains(self.driver)
        elements = self.driver.find_elements(By.CSS_SELECTOR, "#Services .gig-card-layout")

        for element in elements:
            random_x = random.randint(-50, 50)
            random_y = random.randint(-50, 50)
            actions.move_to_element_with_offset(element, random.randint(2, 12), random.randint(0, 9))
            actions.move_by_offset(0, scroll_amount)
            time.sleep(random.uniform(0.2, 0.5))
            actions.move_by_offset(0, -scroll_amount)
            time.sleep(random.uniform(0.2, 0.5))

            actions.send_keys(Keys.ARROW_DOWN)
            actions.send_keys(Keys.ARROW_UP)

            # Click on the element
            actions.click()

            # Perform all actions
            actions.perform()

            # Randomize mouse movements
            actions.move_by_offset(random_x, random_y)


        yield {
            'url': current_url,
            'status': response_status,
            'referer': referer_status,
            'ip': ip_page_source,
            'ua': user_agent,
        }

        time.sleep(60)
