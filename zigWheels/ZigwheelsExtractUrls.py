import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_bike_links_to_csv():
    # Base URL for constructing full links
    base_url = 'https://www.zigwheels.com'

    # Start Playwright
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the desired webpage
        page.goto('https://www.zigwheels.com/bajaj-bikes')

        # Grab the page content
        content = page.content()

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Initialize a list to store all links
        all_links = []

        # Scrape all Bajaj bike links
        bike_elements = soup.select("#modelList > li > div > div.p-15.pt-10.mke-ryt.rel > a")
        for element in bike_elements:
            link_text = element.find('h3').get_text(strip=True)
            link_address = element['href']
            # Construct updated URL
            full_link = urljoin(base_url, link_address.replace('bajaj-bikes', 'user-reviews/bajaj'))
            all_links.append((link_text, full_link))

        # Scrape electric bike links
        container = soup.select_one("#electric-models")
        selector = "#zw-cmnSilder > div.gscr_slideOuter > div > div.gscr_slideWrapper.gscr_usingCss > ul > li > a > h3"
        link_elements = container.select(selector) if container else []

        for link_element in link_elements:
            link_text = link_element.get_text(strip=True)
            link_address = link_element.find_parent('a')['href']  # Get the parent anchor element's href
            # Construct updated URL
            full_link = urljoin(base_url, link_address.replace('bajaj-bikes', 'user-reviews/bajaj'))
            all_links.append((link_text, full_link))

        # Write all links to a CSV file
        with open('BajajLinks.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Text', 'Link'])  # CSV header
            writer.writerows(all_links)  # Write all link data

        print("All updated links have been written to 'BajajLinks.csv'")

# Example usage
scrape_bike_links_to_csv()
