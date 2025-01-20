import scrapy, time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


class MinningSpider(scrapy.Spider):
    name = "minning"
    allowed_domains = ["google.com"]
    start_urls = ["https://asicmarketplace.com/shop/?orderby=date"]
    base_url = "https://www.asicmarketplace.com"

    productData = []
    productLinks = []

    def __init__(self, *args, **kwargs):
        super(MinningSpider, self).__init__(*args, **kwargs)
        print('🚀  Starting the engine...')
        chrome = webdriver.ChromeOptions()
        chrome.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome)

        self.ua = UserAgent()
        self.headers = {"User-Agent": self.ua.random}

    def click_view_more(self):
        while True:
            try:
                load_more_button = wait.until(EC.element_to_be_clickable((By.ID, "loadMore")))
                print("Clicking 'View more' button...")
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(2)  # Wait for products to load
            except Exception as e:
                print("No more 'View more' button or all products loaded.")
                break
    
    def parse(self, response):
        print('🕸️  Parsing')
        self.driver.get(response.url)
        self.click_view_more()

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        productList = soup.find_all("li",{"class":"type-product"})
        for product in productList:
            link = product.find("a").get("href")
            self.productLinks.append(link)
        
        yield from response.follow_all (
            self.productLinks,
            callback=self.parse_children
        )

    def parse_children(self, response):
        """Getting Product links to extract product single page data"""
        singleProductPage = requests.get(response.url, headers=self.headers).text
        soup = BeautifulSoup(singleProductPage, 'html.parser')

        # Extracting Product Information from Single product Pages
        try:
            price = [i.text.strip("US$") for i in soup.select('.price bdi:first-child')]
            regular_price = price[0]
            sale_price = price[1]
        except:
            price = None

        try:
            summary = soup.select_one(".entry-summary") 
            name = summary.select_one("h1").text if summary.select_one("h1") else ""
            sku = summary.select_one(".sku").text if summary.select_one(".sku") else ""
        except:
            name, sku = ""

        try:
            categories = [i.text for i in soup.select("span.posted_in a")]
            categories = ','.join(categories).capitalize()
        except:
            categories = ""

        try:
            props = soup.select(".woocommerce-product-gallery .add-detail li")
            for prop in props:
                key_element = prop.select_one("span.add-heading")
                key = key_element.text.strip() if key_element else "Unknown"
                value = prop.get_text(strip=True).replace(key, "").strip()
                meta_key = f"meta_{key.lower().replace(' ', '_')}"
                product_details[meta_key] = value
        except Exception as e:
            props = []

        try:
            coins = []
            coin_elements = soup.select(".woocommerce-product-gallery .coins li")
            for coin in coin_elements:
                title = coin.find("p").text if coin.find("p") else "Unknown"
                image_element = coin.find("img")
                image_url = image_element["src"] if image_element else ""
                parsed_url = urlparse(image_url)
                image_path = parsed_url.path if image_url else ""
                coins.append({"title": title, "image": image_path})
            product_details['meta_coins'] = json.dumps(coins)  # Store coins as a JSON string
        except Exception as e:
            coins = []

        try:
            gallery = soup.select('.woocommerce-product-gallery__image a')
            images = [image['href'] for image in gallery]
            images = ','.join(images)
        except:
            images = ""

        try:
            description = soup.find("div", {"id":"description"})
        except:
            description = ""

        product = {
                "Regular price": regular_price,
                "Sale price": sale_price,
                "SKU": sku,
                "Name": name,
                "Description": description,
                "Categories": categories,
                "Images": images,
            }

        product.update(product_details)
        self.productData.append(product)
        yield product
        print(product)

    df = pd.DataFrame(productData)
    df.to_csv('asicmines.csv', index=False)