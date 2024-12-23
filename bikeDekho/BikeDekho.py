import asyncio
import pandas as pd
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from IPython import get_ipython
import nest_asyncio
import re
import csv

nest_asyncio.apply()

async def click_next_button(page, bike_name, max_reviews=9999999):
    review_count = 0
    page_number = 1  # Track page number for dynamic file naming

    # Create a directory for the bike under Reviews if it doesn't exist
    folder_name = os.path.join("Reviews", bike_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    while review_count <= max_reviews:
        try:
            # Get the page content and parse it with BeautifulSoup
            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')

            # Extract the reviews on the current page
            review_elements = soup.select(
                "#rf01 > div.app-content > div > div:nth-child(1) > main > div > div.gsc_col-xs-12.gsc_col-sm-12.gsc_col-md-8.gsc_col-lg-9 > section.clearfix.ReadReview.shadow24.marginBottom20 > div > div.gsc-ta-active.gsc-ta-content > ul > li"
            )
            
            reviews_data = []  # List to store review details for the current page
            review_count += len(review_elements)
            print(f"Total reviews loaded on page {page_number}: {len(review_elements)}")

            for review in review_elements:
                review_data = {}

                # Add the bike name to the review data
                review_data['Bike'] = bike_name

                # Extract rating text, or use '-' if not found
                rating_element = review.select_one("div > div > div.authorInfo.authordetail > div.authorSummary > span > span.ratingStarNew")
                review_data['Rating'] = rating_element.get_text(strip=True) if rating_element else '-'

                # Extract content with newline characters replaced by spaces, or use '-'
                contentspace_span = review.select_one("div > div > div.contentspace > span")
                review_data['Title'] = contentspace_span.get_text(" ", strip=True) if contentspace_span else '-'

                contentspace_div = review.select_one("div > div > div.contentspace > div")
                review_data['Review'] = contentspace_div.get_text(strip=True).replace('\n', ' ') if contentspace_div else '-'

                # Extract author summary date, or default to '-'
                author_summary_div = review.select_one("div > div > div.authorInfo.authordetail > div.authorSummary > div")
                if author_summary_div:
                    author_summary_text = author_summary_div.get_text(strip=True)
                    print(f"Debug: Author Summary Text - {author_summary_text}")  # Debugging line to check text

                    # Adjust regex to capture dates in more formats if necessary
                    date_match = re.search(r'(?:on\s+)?(\w{3} \d{1,2}, \d{4})', author_summary_text)
                    review_data['Date'] = date_match.group(1) if date_match else '-'
                else:
                    review_data['Date'] = '-'

                # Append extracted data to list
                reviews_data.append(review_data)

            # Convert to DataFrame and write to CSV with QUOTE_ALL
            reviews_df = pd.DataFrame(reviews_data)
            file_name = os.path.join(folder_name, f'{bike_name}_page_{page_number}.csv')
            reviews_df.to_csv(file_name, index=False, quoting=csv.QUOTE_ALL)
            print(f"Data for page {page_number} written to {file_name}.")

            # Check if the 'Next' button is available and click it
            next_button = await page.query_selector(
                "#rf01 > div.app-content > div > div:nth-child(1) > main > div > div.gsc_col-xs-12.gsc_col-sm-12.gsc_col-md-8.gsc_col-lg-9 > section.clearfix.ReadReview.shadow24.marginBottom20 > div > div.marginTop20 > div > div > div > ul > li:nth-child(11) > span"
            )

            if next_button:
                await next_button.click()
                print(f"Clicked on the 'Next' button. Moving to page {page_number + 1}.")
                await page.wait_for_timeout(3000)  # Increase wait time to ensure the next page loads fully
                page_number += 1
            else:
                print("No more 'Next' button found. Exiting the function.")
                break

        except Exception as e:
            print(f"An error occurred on page {page_number}: {e}. Exiting the function.")
            break

    print("Review extraction complete.")


async def main():
    # Load URLs from BajajLinks.csv
    links_df = pd.read_csv('BajajLinks.csv')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Iterate over each link in the CSV
        for index, row in links_df.iterrows():
            bike = row['Bike'].replace(' ', '_')
            url = row['Link'] + '/reviews'  # Append '/reviews' to the link
            print(f"Extracting reviews for {bike} from {url}")

            # Load the webpage
            await page.goto(url)

            # Click the 'Next' button until the desired number of reviews are loaded and save each page to a file
            await click_next_button(page, bike)

        # Keep the browser open after the script is done
        print("Finished navigating through all bike reviews and extracting them.")
        await page.wait_for_timeout(1000)  # Keeps the browser open for 60 seconds

# Check if running in IPython (e.g., Jupyter Notebook) and use appropriate event loop
if __name__ == "__main__":
    asyncio.run(main())
