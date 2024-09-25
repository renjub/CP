import time
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import nest_asyncio
import asyncio

# Function to extract links and their text from the current page
def extract_links(page_content):
    all_links = []
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find all the links matching the general pattern
    link_elements = soup.select("div.USCqPI ul li > div > div > div > div.o-fznJEv.o-bTDyCI.o-brXWGL > a > h3")

    # Extract the href attribute and text for each link
    for link_element in link_elements:
        parent = link_element.find_parent('a')  # Find the parent <a> tag to extract the href
        link = parent.get('href') if parent else None
        text = link_element.get_text(strip=True)
        if link and text:
            # Convert relative link to absolute URL
            absolute_link = urljoin('https://www.bikewale.com', link)
            # Append '/review/' at the end of the link
            absolute_link_with_review = absolute_link.rstrip('/') + '/reviews/'
            # Store the data with 'Text' first, then 'Link'
            all_links.append({'Text': text, 'Link': absolute_link_with_review})

    return all_links

# Main function to navigate through multiple pages and extract links
async def extract_all_links(playwright):
    all_links = []
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    # Load the webpage
    url = 'https://www.bikewale.com/bajaj-bikes/'
    await page.goto(url)

    while True:
        # Wait for the page content to load
        await page.wait_for_timeout(2000)  # Adjust based on the page load time
        page_content = await page.content()
        
        # Extract links from the current page
        links_on_page = extract_links(page_content)
        all_links.extend(links_on_page)
        print(links_on_page)

        # Check if the 'Next' button is available using the correct CSS selector
        next_button = await page.query_selector("li.pagination__item.pagination__next-page > a")

        if next_button:
            # Click the 'Next' button to go to the next page
            await next_button.click()

            # Wait for the content to load after clicking the button
            await page.wait_for_timeout(2000)  # Adjust if necessary
        else:
            print("Next button not found, or no more pages. Exiting.")
            break

    # Close the browser
    await browser.close()

    return all_links

# Use Playwright to extract data
async def main():
    async with async_playwright() as playwright:
        extracted_links = await extract_all_links(playwright)

    # Move the extracted data to a DataFrame with columns in the desired order
    df = pd.DataFrame(extracted_links, columns=['Text', 'Link'])

    # Optionally, print the DataFrame
    print(df)

    # Optionally, save the DataFrame to a CSV file
    df.to_csv('extracted_bikewale_links_playwright_async.csv', index=False)

    print("Finished extracting the links and texts from all pages using Playwright.")

# Allow running asyncio within a Jupyter Notebook
nest_asyncio.apply()

# Run the main function using the existing event loop
await main()
