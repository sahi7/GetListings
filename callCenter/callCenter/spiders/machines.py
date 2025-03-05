import scrapy, time
import requests, re
import json
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse

class MachinesSpider(scrapy.Spider):
    name = "machines"
    allowed_domains = ["bitcoinmerch.com"]
    start_urls = ["https://bitcoinmerch.com/collections/bitmain-miners"]
    base_url = "https://bitcoinmerch.com"
    productData = []

    def __init__(self, *args, **kwargs):
        super(MachinesSpider, self).__init__(*args, **kwargs)
        print('🚀  Starting the engine...')
        self.ua = UserAgent()
        self.headers = {"User-Agent": self.ua.random}
        json_path = Path.cwd() / "existing_products.json" 
        with open(json_path, 'r', encoding='utf-8') as f:
            self.existing_products = json.load(f)

        self.categories = [
            "Anexminer",
            "Bitdeer",
            "Bitmain",
            "Bombax miner",
            "Canaan avalon",
            "Dragonball",
            "Elphapex",
            "Fluminer",
            "Goldshell",
            "Ibelink",
            "Iceriver",
            "Immersion Cooling",
            "Innosilicon",
            "Ipollo",
            "Jasminer",
            "Loyaltech",
            "Strongu",
            "Todek",
            "Volcminer",
            "Whatsminer"
        ]

        self.coin_mapping = {
            "Ethereum": "/wp-content/uploads/2025/01/14.png",
            "Bitcoin": "/wp-content/uploads/2025/01/Bitcoin-BTC.png",
            "Doge": "/wp-content/uploads/2025/01/DogeCoinDOGE.png",
            "Litecoin": "/wp-content/uploads/2025/03/Litecoin.png",
            "Alphium": "/wp-content/uploads/2025/01/Alphium.png",
            "Dashcoin": "/wp-content/uploads/2025/01/Dashcoin.png",
            "ScPrime": "/wp-content/uploads/2025/01/ScPrime-SCP.png",
            "Handshake": "/wp-content/uploads/2025/01/Handshake.png",
            "Nervos(CKB)": "/wp-content/uploads/2025/01/NervosCKB.png",
            "Kadena": "/wp-content/uploads/2025/01/Kadena.png",
            "Kaspa": "/wp-content/uploads/2025/01/Kaspa.png",
            "Sedra(SDR)": "/wp-content/uploads/2025/03/SedraSDR.png",
            "Monero": "/wp-content/uploads/2025/01/XMR.webp",
            "Zephyr": "/wp-content/uploads/2025/01/ZephyrZEPH.png",
            "Zcash": "/wp-content/uploads/2025/01/ZCashZEC.png",
            "Radiant(RXD)": "/wp-content/uploads/2025/01/RadiantRXD.png",
            "Nexa": "/wp-content/uploads/2025/01/Nexa.png",
            "SiaClassic": "/wp-content/uploads/2025/01/SiaClassic.png",
            "Grin": "/wp-content/uploads/2025/03/cuckatoo32.png",
            "ALEO": "/wp-content/uploads/2025/01/ALEO.webp",
            "Siacoin": "/wp-content/uploads/2025/01/SiaCoin-SC.png",
            "Lbry": "/wp-content/uploads/2025/01/LBRY.png",
            "Starcoin": "/wp-content/uploads/2025/01/Starcoin.png",
        }

    def parse(self, response, **kwargs):
        productLinks = []
        print('📖️  Parsing ' + response.url)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract products
        productList = soup.find_all("div", {"class": "product-item"})
        for product in productList:
            link = product.find("a").get("href")
            productLinks.append(link)
        print(f"🔗 Found {len(productLinks)} product links.")
        
        # Follow product links
        for link in productLinks:
            yield response.follow(link, callback=self.parse_children, headers=self.headers)

        # Pagination handling
        next_page = response.css('a[class="pagination__next link"]::attr(href)').get()
        if next_page:
            yield response.follow(self.base_url + next_page, self.parse)
        else:
            print("🏁  No more pages")

    def extract_meta_from_name(self, name):
        # Regex to extract hashrate (e.g., 400GH/s, 86Th/s, 5.5TH/s)
        hashrate_match = re.search(r'(\d+\.?\d*)\s*([KMGT]?H/s)', name, re.IGNORECASE)
        # Regex to extract power (e.g., 2800W, 3730 W)
        power_match = re.search(r'(\d+\.?\d*)\s*W', name, re.IGNORECASE)

        meta_hashrate = hashrate_match.group(0) if hashrate_match else None
        meta_power = power_match.group(0) if power_match else None

        return meta_hashrate, meta_power

    def extract_meta_from_text(self, text):
        if not text:
            return None, None

        # Regex to extract hashrate (e.g., 400GH/s, 86Th/s, 5.5TH/s)
        hashrate_match = re.search(r'(\d+\.?\d*)\s*([KMGT]?H/s)', text, re.IGNORECASE)
        # Regex to extract power (e.g., 2800W, 3730 W)
        power_match = re.search(r'(\d+\.?\d*)\s*W\b', text, re.IGNORECASE)

        meta_hashrate = hashrate_match.group(0) if hashrate_match else None
        meta_power = power_match.group(0) if power_match else None

        return meta_hashrate, meta_power

    def determine_mineable_coins(self, name):
        # Check for specific coin names in the product name
        coins = []
        for coin_name, image_path in self.coin_mapping.items():
            # Check for the full coin name or its partial/abbreviated forms
            if (
                coin_name.lower() in name.lower()  # Full name match
                or any(part.lower() in name.lower() for part in coin_name.split())  # Partial match (e.g., "Sedra" or "SDR")
                or (  # Handle cases like "Sedra(SDR)"
                    "(" in coin_name
                    and any(part.lower() in name.lower() for part in coin_name.replace("(", " ").replace(")", " ").split())
                )
                or (  # Handle abbreviations like "KAS" for "Kaspa"
                    "Kaspa" in coin_name and "KAS" in name.upper()
                )
            ):
                coins.append({"title": coin_name, "image": image_path})

        # If no coins are found, assign default coins
        if not coins:
            coins.append({"title": "Bitcoin", "image": self.coin_mapping["Bitcoin"]})
            coins.append({"title": "Ethereum", "image": self.coin_mapping["Ethereum"]})
        return coins

    def generate_sku(self, cleaned_name):
        sku_parts = []
        for part in cleaned_name.split():
            # Look for model-like patterns (e.g., S19, 115TH, KAS)
            if any(c.isdigit() for c in part) or part.upper() in ["PRO", "KAS", "TH", "GH"]:
                # Clean the part by removing unwanted characters
                cleaned_part = part.replace("(", "").replace(")", "").replace("/", "").replace("-", "")
                sku_parts.append(cleaned_part)

        # If no model-like parts are found, use the first two words as fallback
        if not sku_parts:
            fallback_parts = cleaned_name.split()[:2]  # Use the first two words
            sku_parts = [part.replace("(", "").replace(")", "").replace("/", "").replace("-", "") for part in fallback_parts]

        # Combine parts into a single SKU, separated by hyphens
        sku = "-".join(sku_parts)

        # Limit SKU to 10 characters
        sku = sku[:10]

        return sku if sku else ""

    def extract_hashrate(self, title, provided_hashrate):
        if provided_hashrate:
            return self.normalize_hashrate(provided_hashrate)
        patterns = [
            r'(\d+\.?\d*)\s*(TH|GH|MH|KH)\/?s?',
            r'(\d+\.?\d*)\s*(tera|giga|mega|kilo)?\s*hash'
        ]
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).upper() if match.group(2) else 'TH'
                return f"{value}{unit}"
        return ''

    def extract_model_info(self, title):
        model_match = re.search(r'\b([A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9]?\+?)\b', title)
        model = model_match.group(1) if model_match else ''
        
        coin = ''
        if any(x in title.lower() for x in ['btc', 'bitcoin']):
            coin = 'BTC'
        elif any(x in title.lower() for x in ['ltc', 'litecoin']):
            coin = 'LTC'
        elif any(x in title.lower() for x in ['doge', 'dogecoin']):
            coin = 'DOGE'
        elif 'kas' in title.lower():
            coin = 'KAS'
        elif 'etc' in title.lower():
            coin = 'ETC'
        elif 'kadena' in title.lower():
            coin = 'KDA'
        return {'model': model, 'coin': coin}

    def normalize_title(self, title):
        title = title.lower()
        title = re.sub(r'(bitmain|antminer|whatsminer|microbt|goldshell|canaan|avalon|made|miner|btc|hydro|\(|\))', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def normalize_hashrate(self, hashrate):
        if not hashrate:
            return ''
        hashrate = re.sub(r'\s+', '', hashrate.upper())
        hashrate = re.sub(r'\/?[S]$', '', hashrate)
        return hashrate

    def is_duplicate(self, product):
        title = product.get('Name', '')
        hashrate = self.extract_hashrate(title, product.get('meta_hashrate', ''))
        model_info = self.extract_model_info(title)
        normalized_title = self.normalize_title(title)

        for existing_title, existing_hashrate in self.existing_products.items():
            existing_normalized = self.normalize_title(existing_title)
            existing_hashrate_norm = self.normalize_hashrate(existing_hashrate)
            existing_model_info = self.extract_model_info(existing_title)

            # Calculate title similarity
            title_similarity = 0
            import difflib
            title_similarity = difflib.SequenceMatcher(None, normalized_title, existing_normalized).ratio() * 100

            # Model matching
            model_match = model_info['model'] and existing_model_info['model'] and \
                         model_info['model'] == existing_model_info['model']

            # Hashrate comparison
            hashrate_match = False
            if hashrate and existing_hashrate_norm:
                try:
                    hr1 = float(re.search(r'(\d+\.?\d*)', hashrate).group(1))
                    hr2 = float(re.search(r'(\d+\.?\d*)', existing_hashrate_norm).group(1))
                    hashrate_match = abs(hr1 - hr2) <= 5  # 5-unit tolerance
                except (AttributeError, ValueError):
                    hashrate_match = hashrate == existing_hashrate_norm

            # Coin matching
            coin_match = not model_info['coin'] or not existing_model_info['coin'] or \
                        model_info['coin'] == existing_model_info['coin']

            # Duplicate conditions
            if (model_match and hashrate_match and coin_match) or \
               (title_similarity > 85 and coin_match):
                return True

        return False

    def parse_children(self, response, **kwargs):
        """Getting Product links to extract product single page data"""
        # singleProductPage = requests.get(response.url, headers=self.headers).text
        print(f"🔍 Parsing child page: {response.url}")
        soup = BeautifulSoup(response.text, 'html.parser')

        product_details = {}

        # Extracting Product Information from Single product Pages
        try:
            price_list = [i.text.strip("$") for i in soup.select('.product-form__info-item .transcy-money')]
            regular_price = price_list[0] if price_list else None
            sale_price = price_list[1] if len(price_list) > 1 else None
        except Exception as e:
            regular_price = None
            sale_price = None

        try:
            summary = soup.select_one(".product-meta")

            # Get and clean product name
            name_elem = summary.select_one("h1") if summary else None
            raw_name = name_elem.text.strip() if name_elem else ""

            # Define a regex pattern to match all variations of "Bitcoin Merch" prefixes
            prefix_pattern = re.compile(r"^Bitcoin\s*Merch[\s®-]*-\s*", re.IGNORECASE)

            # Clean the name by removing the prefix
            cleaned_name = re.sub(prefix_pattern, "", raw_name).strip()
            name = cleaned_name
            # Generate SKU from cleaned name
            sku = self.generate_sku(name)
            
            # Infer category from cleaned name
            category = ""

            # Check for the special case of "Antminer" first
            if "Antminer" in cleaned_name:
                category = "Bitmain"
            else:
                # Iterate through categories and check for partial matches
                for cat in self.categories:
                    if cat.lower() in cleaned_name.lower():
                        category = cat
                        break
            
        except Exception as e:
            name, sku, category = "", "", ""

        try:
            children = soup.select('.product-block-list__item--description .text--pull > *')
            cleaned_html = ""
            for child in children:
                # Skip processing if the child is a <ul> or <li> tag
                if child.name in ['ul', 'li']:
                    cleaned_html += str(child) + " "  # Preserve the <ul> or <li> tag as-is
                    continue  # Skip to the next child

                # Remove all <a>, <b>, <strong>, and <script> tags
                for tag in child.find_all(['a', 'b', 'strong', 'script', 'br']):
                    tag.decompose()  # Remove the tag but keep its text content

                cleaned_html += str(child) + " "  # Append the cleaned child to the result

            description = cleaned_html.strip()  # Remove leading/trailing whitespace
        except Exception as e:
            print(f"Error processing description: {e}")
            description = ""

        try:
            short_description = soup.find("div", {"class":"woocommerce-product-details__short-description"})
        except:
            short_description = ""

        try:
            # Extract meta_hashrate and meta_power from the name
            meta_hashrate, meta_power = self.extract_meta_from_name(name)

            # If meta_hashrate or meta_power is missing, search in description
            if not meta_hashrate or not meta_power:
                desc_hashrate, desc_power = self.extract_meta_from_text(description)
                meta_hashrate = meta_hashrate or desc_hashrate
                meta_power = meta_power or desc_power

            # If meta_hashrate or meta_power is still missing, search in short_description
            if not meta_hashrate or not meta_power:
                short_desc_hashrate, short_desc_power = self.extract_meta_from_text(short_description)
                meta_hashrate = meta_hashrate or short_desc_hashrate
                meta_power = meta_power or short_desc_power

            # Add meta_hashrate and meta_power to product_details dictionary
            if meta_hashrate:
                product_details["meta_hashrate"] = meta_hashrate
            if meta_power:
                product_details["meta_power"] = meta_power
        except Exception as e:
            props = []

        try:
            coins = self.determine_mineable_coins(name)
            product_details["meta_coins"] = json.dumps(coins)
        except Exception as e:
            coins = []

        try:
            gallery = soup.select('.product-gallery .product-gallery__image')
            images = []
            for image in gallery:
                if 'data-zoom' in image.attrs:
                    image_url = image['data-zoom']
                    # Ensure the URL starts with "https://bitc"
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url  # Add "https:" prefix
                    elif not image_url.startswith('https://'):
                        continue  # Skip URLs that don't match the desired format
                    images.append(image_url)
            images = ','.join(images)
        except Exception as e:
            print(f"Error extracting images: {e}")
            images = ""

        short_description = short_description if short_description is not None else ""
        description = description if description is not None else ""
        combined_description = f"{short_description} {description}".strip()

        product = {
                "Regular price": regular_price,
                "Sale price": sale_price,
                "SKU": sku,
                "Name": name,
                "Description": combined_description,
                "Categories": category,
                "Images": images,
            }

        product.update(product_details)
        if not self.is_duplicate(product):
            self.productData.append(product)
            yield product
            print(product)
        else:
            print(f"Skipped duplicate: {product['Name']} ({product['meta_hashrate']})")

    def close(self, reason):
        """Save data to CSV after Scrapy finishes crawling"""
        df = pd.DataFrame(self.productData)
        df.to_csv('asicmines.csv', index=False)
        print("✅ CSV saved successfully!")
