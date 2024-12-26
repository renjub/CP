#!/usr/bin/env python
# coding: utf-8

# In[3]:


#!/usr/bin/env python
# coding: utf-8

import asyncio
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def extract_links(page, all_links):
    try:
        # Wait for the links to be present
        await page.wait_for_selector('body > div.site-container > div.site-inner > div > main > article > header > h2 > a')

        # Get page content and parse with BeautifulSoup
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Extract links from the specific CSS selector
        link_elements = soup.select('body > div.site-container > div.site-inner > div > main > article > header > h2 > a')
        links = [link.get('href') for link in link_elements]

        # Append to the all_links list
        all_links.extend(links)

        print(f"Extracted {len(links)} links from the current page.")
        return links
    except Exception as e:
        print(f"Error extracting links: {e}")
        return []

async def click_next_button(page, all_links):
    while True:
        try:
            # Extract links from the current page
            await extract_links(page, all_links)

            # Print the current page URL
            current_url = page.url
            print(f"Current page URL: {current_url}")

            # Check for the 'Next' button
            next_button = await page.query_selector(
                "body > div.site-container > div.site-inner > div > main > div.archive-pagination.pagination > ul > li.pagination-next > a"
            )

            if next_button:
                await next_button.click()
                print("Clicked on the 'Next' button.")
                await page.wait_for_timeout(2000)  # Wait for page content to load
            else:
                print("No more 'Next' button found. Exiting loop.")
                break
        except Exception as e:
            print(f"Error while clicking 'Next': {e}")
            break

async def save_to_csv(links, filename="BajajLinks.csv"):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for link in links:
                writer.writerow([link])
        print(f"Saved {len(links)} links to {filename}.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

async def main():
    url = 'https://bikeindia.in/bajaj/'
    all_links = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Use headless=False to see the browser
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the URL
        await page.goto(url)
        print(f"Loaded page: {url}")

        # Extract links and navigate through pages
        await click_next_button(page, all_links)

        # Save links to a CSV file
        await save_to_csv(all_links)

        await browser.close()

# Run the async main function
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # Allows nested event loops in environments like Jupyter
    asyncio.run(main())

