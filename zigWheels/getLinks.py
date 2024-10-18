import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_all_links_to_csv():
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

        # Select all list items that contain the links
        link_elements = soup.select("#modelList > li > div > div.p-15.pt-10.mke-ryt.rel > a")

        # Initialize a list to store the results
        links = []

        # Loop through all link elements and extract the text and href
        for link_element in link_elements:
            link_text = link_element.find('h3').get_text(strip=True)
            link_address = link_element['href']
            full_link = urljoin(base_url, link_address)  # Construct full URL
            links.append((link_text, full_link))

        # Write the data to a CSV file
        with open('bajaj_bikes_links.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Text', 'Link'])  # CSV header
            writer.writerows(links)  # Write all link data

        print("Data has been written to 'bajaj_bikes_links.csv'")

# Example usage
scrape_all_links_to_csv()