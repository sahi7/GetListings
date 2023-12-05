import scrapy, time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from scrapy.http import HtmlResponse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class GmapSpider(scrapy.Spider):
    name = "gmap"
    allowed_domains = ["www.google.com"]
    start_urls = ["https://www.google.com/maps/search/clothing+store+in+autriche/"]

    def __init__(self, *args, **kwargs):
        super(GmapSpider, self).__init__(*args, **kwargs)
        options = uc.ChromeOptions()
        options.add_argument('--lang=fr')
        self.driver = uc.Chrome(options=options, headless=True)

    def parse(self, response):
        self.driver.get(response.url)
        # Get the initial number of results
        old_results_count = len(self.driver.find_elements(By.XPATH, '//div[contains(@class, "fontHeadlineSmall")]'))
        
        while True:
            # Scroll to the bottom
            results_container = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.WNBkOb[role="main"]')
            ActionChains(self.driver).move_to_element(results_container).send_keys(Keys.END).perform()
            time.sleep(2)

            # Get the updated number of results
            new_results_count = len(self.driver.find_elements(By.XPATH, '//div[contains(@class, "fontHeadlineSmall")]'))

            # Break the loop if no new results are loaded
            if new_results_count == old_results_count:
                break

            # Update the old results count
            old_results_count = new_results_count

        website = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=website, encoding='utf-8')

        # Extract data from the response
        # Replace the following code with your own logic to extract the desired data
        for result in response.css('.Nv2PK'):
            data = {
                    'Name': result.xpath('//div[contains(@class, "fontHeadlineSmall")]/text()').get(),
                    'Address': result.xpath('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]').get(),
                    'Website': result.xpath('//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]').get(),
                    'Telephone': result.xpath('//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]').get(),
                    'Reviews': result.xpath('//span[@role="img"]//text()').get()
                }
            yield data
            print(data)
