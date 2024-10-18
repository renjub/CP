import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_electric_model_links_to_csv():
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

        # Select all h3 elements under #zw-cmnSilder within the #electric-models container
        link_elements = soup.select("#electric-models #zw-cmnSilder > ul > li > a > h3")

        # Initialize a list to store the results
        links = []

        # Loop through all link elements and extract the text and href
        for link_element in link_elements:
            link_text = link_element.get_text(strip=True)
            link_address = link_element.find_parent('a')['href']  # Get the parent anchor element's href
            full_link = urljoin(base_url, link_address)  # Construct full URL
            links.append((link_text, full_link))

        # Write the data to a CSV file
        with open('electric_model_links.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Text', 'Link'])  # CSV header
            writer.writerows(links)  # Write all link data

        print("Data has been written to 'electric_model_links.csv'")

# Example usage
scrape_electric_model_links_to_csv()