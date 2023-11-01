import csv
import scrapy
from bs4 import BeautifulSoup

class WoodSpider(scrapy.Spider):
    name = "wood"
    allowed_domains = ["oudandmusk.com"]
    start_urls = ["https://oudandmusk.com/en/16-sandal"]

    def parse(self, response):
        # Parse the product list page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product links
        product_links = soup.select('.product-container .product-image-container')
        
        for link in product_links:
            product_url = link.find("span",{"class":"product_img_link"}).get('data-product')
            print('Product URL', product_url)
            yield response.follow(product_url, callback=self.parse_product)
        
        # Handle pagination
        pagination = soup.find('ul', class_='pagination')
        
        try:
            # Find the currently active page
            active_page = pagination.find('li', class_='active current')
            
            if active_page:
                next_page_li = active_page.find_next_sibling('li')  # Get the next sibling <li> element
                if next_page_li:
                    next_page_url = next_page_li.find('a').get('href')
                    yield response.follow(next_page_url, callback=self.parse)
        except AttributeError:
            print("No Pagination")

    def parse_product(self, response):
        # Parse the product detail page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product details
        product_title = soup.find("h1", {"itemprop": "name"}).text
        price_element = soup.find('span', itemprop='price')
        product_price = price_element.get('content') if price_element else None
        if product_price:
            product_price = float(product_price)  # Convert to float
            product_price = f"${product_price:.2f}"

        short_desc = soup.find("div", {"id": "short_description_content"})
        long_desc = soup.find("div", {"id": "tab-more-info"})

        # Extract the img src using the 'itemprop' attribute
        img_element = soup.find('img', itemprop='image')
        img_src = img_element.get('src') if img_element else None

        breadcrumb_items = soup.find_all('li', itemprop='itemListElement')
        categories = []
        for item in breadcrumb_items[1:]:  # Take the last two items
            category_name = item.find('span', itemprop='name').text.strip()
            categories.append(category_name)
        if len(categories) >= 2:
            # Remove the last element
            categories.pop()

        category_hierarchy = ' > '.join(categories)

        # Store the scraped data in a dictionary
        scraped_data = {
            'title': product_title,
            'price': product_price,
            'short_description': short_desc,
            'long_description': long_desc,
            'image_src': img_src,
            'category_hierarchy': category_hierarchy
        }

        # Yield the scraped data as an item
        yield scraped_data
        # Write the data to a CSV file
        self.write_to_csv(scraped_data)

    def write_to_csv(self, data):
        # Define the CSV file name
        csv_filename = 'scraped_data.csv'

        # Write the data to the CSV file
        with open(csv_filename, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['title', 'price', 'short_description', 'long_description', 'image_src', 'category_hierarchy']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Check if the file is empty (write header row if it is)
            if csv_file.tell() == 0:
                writer.writeheader()

            writer.writerow(data)

