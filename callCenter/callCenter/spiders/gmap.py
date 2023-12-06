import scrapy, time, re
from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class GmapSpider(scrapy.Spider):
    name = "gmap"
    allowed_domains = ["www.google.com"]
    start_urls = ["https://www.google.com/maps/search/magasin+de+vetement+montreal/"]

    def __init__(self, *args, **kwargs):
        super(GmapSpider, self).__init__(*args, **kwargs)

        # options = uc.ChromeOptions()
        # self.driver = uc.Chrome(options=options, headless=False)

        options = webdriver.ChromeOptions()
        prefs = {"intl.accept_languages": "fr,fr_FR"}
        options.add_argument('--user-data-dir=chrome-profile') 
        options.add_argument('--lang=fr')
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('prefs', {'intl.accept_languages': 'fr,fr_FR'})
        self.driver = webdriver.Chrome(ChromeDriverManager().install())


    def parse(self, response):
        self.driver.get(response.url)
        # Get the initial number of results
        old_results_count = len(self.driver.find_elements(By.XPATH, '//div[contains(@class, "fontHeadlineSmall")]'))
        
        # while True:
        #     # Scroll to the bottom
        #     results_container = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.WNBkOb[role="main"]')
        #     ActionChains(self.driver).move_to_element(results_container).send_keys(Keys.END).perform()
        #     time.sleep(2)

        #     # Get the updated number of results
        #     new_results_count = len(self.driver.find_elements(By.XPATH, '//div[contains(@class, "fontHeadlineSmall")]'))

        #     # Break the loop if no new results are loaded
        #     if new_results_count == old_results_count:
        #         break

        #     # Update the old results count
        #     old_results_count = new_results_count

        # links = self.driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc').get_attribute("href")
        # nLinks = [link for link in links]
        nLinks = [link.get_attribute("href") for link in self.driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')]

        yield from response.follow_all (nLinks, callback=self.parse_final)

        
    def parse_final(self, response):
        self.driver.get(response.url)
        print('Processing: ', response.url)
        html_content  = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        name_element = soup.select_one('div.TIHn2 h1.DUwDvf.lfPIob')
        data = {
        'Name': soup.select_one('div.TIHn2 h1.DUwDvf.lfPIob').get_text() if soup.select_one('div.TIHn2 h1.DUwDvf.lfPIob') else '',
        'Address': soup.select_one('[data-item-id*="address"]').get_text() if soup.select_one('[data-item-id*="address"]') else '',
        'Website': soup.select_one('a[data-item-id="authority"] div.fontBodyMedium').get_text() if soup.select_one('a[data-item-id="authority"] div.fontBodyMedium') else '',
        'Telephone': soup.select_one('button[data-item-id*="phone:tel:"] div.fontBodyMedium').get_text() if soup.select_one('button[data-item-id*="phone:tel:"] div.fontBodyMedium') else '',
        'Reviews Count': soup.select_one('span[aria-label*="avis"]').get_text() if soup.select_one('span[aria-label*="avis"]') else '',
        'Average Rating': soup.select_one('div.TIHn2 div.fontBodyMedium.dmRWX span[aria-hidden]').get_text() if soup.select_one('div.TIHn2 div.fontBodyMedium.dmRWX span[aria-hidden]') else '',
        'Business Website': soup.select_one('a.lcr4fd')['href'] if soup.select_one('a.lcr4fd') else '',
        'Category': soup.select_one('[jsaction="pane.rating.category"]').get_text() if soup.select_one('[jsaction="pane.rating.category"]') else '',
        'Description': soup.select_one('div.WeS02d.fontBodyMedium div.PYvSYb').get_text() if soup.select_one('div.WeS02d.fontBodyMedium div.PYvSYb') else ''
        }

        # Handle cases where data is not available by replacing with empty strings
        for key, value in data.items():
            if not value:
                data[key] = ''

        print(data)
            