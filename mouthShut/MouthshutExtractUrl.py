import asyncio
from playwright.async_api import async_playwright
import nest_asyncio
import csv

# Apply nest_asyncio to allow multiple event loops in Jupyter
nest_asyncio.apply()

async def extract_and_save_to_csv():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the desired URL
        url = 'https://www.mouthshut.com/bajaj-auto-bikes-proid-925019'
        await page.goto(url)

        # Wait for the page to load
        await page.wait_for_timeout(2000)

        # Specify the CSV file name
        csv_filename = "BajajLinks.csv"

        # Open the CSV file for writing and create a writer object
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(["Text", "Link"])

            while True:
                # Extract all elements that match the general pattern for nth-child elements
                elements = await page.query_selector_all('#aspnetForm > div.container-fluid.p-0.header_ms > div.main-content > div.custom-container.p-15 > div > div.listing-section > div.row > div.col.listing-rightbar > div.card-deck > div > div.card-body > div.listing-prod-title > a')

                # Loop through each element and extract the text and 'href' attribute (the link)
                for element in elements:
                    text = await element.inner_text()
                    link = await element.get_attribute('href')
                    # Write the extracted text and link to the CSV file
                    writer.writerow([text, link])

                print("Data extracted from current page.")

                # Check if the "Next" button is available
                next_button = await page.query_selector('#aspnetForm > div.container-fluid.p-0.header_ms > div.main-content > div.custom-container.p-15 > div > div.listing-section > div.row > div.col.listing-rightbar > nav > ul > li.page-item.next > a')
                if next_button:
                    # Click the "Next" button
                    await next_button.click()

                    # Wait for the next page to load
                    await page.wait_for_timeout(2000)
                else:
                    # No "Next" button, exit the loop
                    print("No more pages to scrape.")
                    break

        print(f"Data successfully saved to {csv_filename}")

        # Close the browser
        await browser.close()

# Run the async function in an event loop
if __name__ == "__main__":
    asyncio.run(extract_and_save_to_csv())
