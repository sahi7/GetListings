from bs4 import BeautifulSoup

base_url = "https://www.pagesjaunes.fr"

def get_links(response_data):
    results = BeautifulSoup(response_data, 'html.parser')
    hotel_links = results.select('.bi-content a[href*="pros/"]')
    # hotel_links = results.select('.results a[href*="pros/"]')
    links_found = []
    if hotel_links:
        print('Len of Hotel Links: ', len(hotel_links))
        for link in hotel_links:
            # link.find("a",{"class":"bi-denomination"}).get('href')
            href = link.get('href')
            target_url = base_url + href
            links_found.append(target_url)
        return links_found


def scrape_content(response_data):
        results = BeautifulSoup(response_data.body, 'html.parser')
        try:
            name = results.find("h1",{"class":"noTrad"}).text.strip()
            split_name = name.split('\n', 1)  # Split at the first '\n'
            result_name = split_name[0].strip()
        except:
            name = ''
        postal_code = ""
        try:
            address_element = results.select_one('.address-container span.noTrad')
            if address_element:
                address = address_element.text.strip()
                # Extract postal code if available
                if address:
                    # Use a regular expression to find a postal code pattern (5 digits)
                    postal_code_match = re.search(r'\b\d{5}\b', address)
                    if postal_code_match:
                        postal_code = postal_code_match.group()
            else:
                address = ''
        except:
            address = ''
        try:
            website = results.select_one('.lvs-container span.value').text
        except:
            website = ''
        try:
            tel = results.find("span",{"class":"coord-numero"}).text
        except:
            tel = ''
        try:
            stars = results.find("span",{"class":"categorie-libelle"}).text
        except:
            stars = ''
        try:
            tariffs = results.select('#tarif-hotel span.prix')
            tariff_texts = [tariff.get_text() for tariff in tariffs]
            # Join the extracted texts with a comma
            all_tariffs = ', '.join(tariff_texts)
        except:
            all_tariffs = ""
        
        # Yield the scraped results
        data = {
            'Name': result_name,
            'Address': address,
            'Postal Code': postal_code,
            'Website': website,
            'Telephone': tel
            # 'Stars': stars,
            # 'Tariffs': all_tariffs
        }
        yield data