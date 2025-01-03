import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from IPython import get_ipython
import subprocess

# Base URL for the bike reviews
base_url = 'https://www.motorbeam.com/tag/bike-reviews/page/'

# Open a file to log the output
log_file = open("BajajLinks.txt", "w")

# Function to log messages to the file
def log_message(message):
    print(message)  # Print to console as well (optional)
    log_file.write(message + "\n")

# Function to read the value of #content > nav > div > div > ul > li:nth-child(5) > a
async def read_last_page(page):
    try:
        page_element = page.locator("#content > nav > div > div > ul > li:nth-child(5) > a")
        last_page_number = await page_element.inner_text()
        last_page_number = last_page_number.strip()
        # log_message(f"Last page number detected: {last_page_number}")
        return int(last_page_number)
    except Exception as e:
        log_message(f"Error while reading the last page number: {e}")
        return None

# Function to extract link addresses from the specific selector
async def extract_links(page):
    try:
        # Get the page content and parse it using BeautifulSoup
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the links using the provided CSS selector
        link_elements = soup.select('h2.entry-title > a')

        # Filter and log links containing 'bajaj'
        for link in link_elements:
            href = link.get('href')
            if 'bajaj' in href.lower():  # Check if 'bajaj' is in the link address (case-insensitive)
                log_message(href)
    except Exception as e:
        log_message(f"An error occurred while extracting links: {e}")

# Function to increment pages until the last page is reached
async def navigate_pages(page, current_page, last_page):
    while current_page <= last_page:
        # log_message(f"Navigating to page {current_page}...")
        # Navigate to the next page
        await page.goto(f'{base_url}{current_page}/')
        
        # Extract links from the current page
        await extract_links(page)
        
        # Increment the current page
        current_page += 1

async def main():
    try:
        # Ensure the necessary browser is installed
        subprocess.run(["playwright", "install"], check=True)

        async with async_playwright() as p:
            # Launch the browser in headless mode
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Load the first webpage
            current_page = 0
            await page.goto(f'{base_url}{current_page}/')

            # Read the last page number
            last_page = await read_last_page(page)

            # Start the navigation process
            if last_page:
                await navigate_pages(page, current_page + 1, last_page)

            # log_message("Finished navigating through the pages and extracting links.")
            await browser.close()
    except Exception as e:
        log_message(f"An error occurred during execution: {e}")
    finally:
        log_file.close()  # Ensure the log file is closed properly

# Check if running in Jupyter Notebook and run the main function accordingly
if get_ipython() is not None and "IPKernelApp" in get_ipython().config: 
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(main())
    except RuntimeError:
        asyncio.run(main())
else:
    asyncio.run(main())