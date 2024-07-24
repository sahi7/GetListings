import scrapy, time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class GmapSpider(scrapy.Spider):
    name = "gmap"
    allowed_domains = ["www.google.com"]
    start_urls = ["https://www.google.com/maps/search/secondary+schools+%C3%A0+proximit%C3%A9+de+Bassa,+Douala"]

    def __init__(self, *args, **kwargs):
        super(GmapSpider, self).__init__(*args, **kwargs)

        print('🧠  Starting engine')
        chrome = webdriver.ChromeOptions()
        chrome.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome)

    def parse(self, response):
        self.driver.get(response.url)
        # Get the initial number of results
        # desired_text = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.WNBkOb[role="main"] [aria-label]').get_attribute('aria-label').split('Résultats pour ')[1].strip('"')
        desired_text = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.WNBkOb[role="main"] [aria-label]').get_attribute('aria-label')
        divSideBar = self.driver.find_element(By.CSS_SELECTOR,f"div[aria-label='{desired_text}']")

        keepScrolling=True
        print('💫  Entering scrollbar')
        while(keepScrolling):
            divSideBar.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            divSideBar.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            html = self.driver.find_element(By.TAG_NAME, "html").get_attribute('outerHTML')
            if(html.find("Vous êtes arrivé à la fin de la liste.")!=-1):
                print('📜  Scrolling complete')
                keepScrolling=False

        nLinks = [link.get_attribute("href") for link in self.driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')]
        print(len(nLinks), ' Results')

        yield from response.follow_all (nLinks, callback=self.parse_final)

        
    def parse_final(self, response):
        self.driver.get(response.url)
        print('🕸️  Processing: ', response.url)
        html_content  = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        name_element = soup.select_one('div.TIHn2 h1.DUwDvf.lfPIob')
        data = {
            'Name': soup.select_one('div.TIHn2 h1.DUwDvf.lfPIob').get_text() if soup.select_one('div.TIHn2 h1.DUwDvf.lfPIob') else '',
            'Address': soup.select_one('[data-item-id*="address"]').get_text() if soup.select_one('[data-item-id*="address"]') else '',
            'Telephone': soup.select_one('button[data-item-id*="phone:tel:"] div.fontBodyMedium').get_text() if soup.select_one('button[data-item-id*="phone:tel:"] div.fontBodyMedium') else '',
            'Website': soup.select_one('a[data-item-id="authority"] div.fontBodyMedium').get_text() if soup.select_one('a[data-item-id="authority"] div.fontBodyMedium') else '',
            # 'Reviews Count': soup.select_one('span[aria-label*="avis"]').get_text() if soup.select_one('span[aria-label*="avis"]') else '',
            # 'Average Rating': soup.select_one('div.TIHn2 div.fontBodyMedium.dmRWX span[aria-hidden]').get_text() if soup.select_one('div.TIHn2 div.fontBodyMedium.dmRWX span[aria-hidden]') else '',
            # 'Business Website': soup.select_one('a.lcr4fd')['href'] if soup.select_one('a.lcr4fd') else '',
            # 'Category': soup.select_one('[jsaction="pane.rating.category"]').get_text() if soup.select_one('[jsaction="pane.rating.category"]') else '',
            # 'Description': soup.select_one('div.WeS02d.fontBodyMedium div.PYvSYb').get_text() if soup.select_one('div.WeS02d.fontBodyMedium div.PYvSYb') else ''
        }

        # Handle cases where data is not available by replacing with empty strings
        for key, value in data.items():
            if not value:
                data[key] = ''

        yield(data)
            