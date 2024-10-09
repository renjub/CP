import re
import os
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Function to extract star rating from the review_div
def extract_star_rating_from_review(review_div):
    rating_div = review_div.find('div', class_='rating')
    if rating_div:
        star_span = rating_div.find('span', recursive=False)
        if star_span:
            rated_stars = star_span.find_all('i', class_='icon-rating rated-star')
            star_rating = len(rated_stars)
        else:
            star_rating = 0
    else:
        star_rating = 0
    return star_rating

# Function to extract review title from the review_div
def extract_review_title(review_div):
    # Use the appropriate pattern to find the title element
    title_element = review_div.find('a', id=re.compile(r'rptreviews_ctl\d+_lnkTitle'))
    
    if title_element:
        review_title = title_element.get_text(strip=True)
    else:
        review_title = "-"
    
    return review_title

# Function to extract review text from the review_div
def extract_review_text(review_div):
    review_element = review_div.select_one("div.more.reviewdata > p")
    if review_element:
        review_text = review_element.get_text(strip=True)
    else:
        review_text = "-"
    return review_text

# Function to extract date and time from the review_div
def extract_review_datetime(review_div):
    datetime_element = review_div.find('span', id=re.compile(r'^rptreviews_ctl\d+_lblDateTime$'))
    if datetime_element:
        review_datetime = datetime_element.get_text(strip=True)
    else:
        review_datetime = "-"
    return review_datetime

# Function to extract location from the review_div
def extract_location(review_div):
    # Use a regular expression to match the div with id containing 'rptreviews_ctl<number>_divProfile'
    location_div = review_div.find("div", id=re.compile(r'rptreviews_ctl\d+_divProfile'))
    
    if location_div:
        # Now find the div containing the actual address text
        address_div = location_div.find("div", class_="usr-addr-text")
        if address_div:
            return address_div.get_text(strip=True)
    
    return "-"    

# Function to extract likes from the review_div
def extract_likes(review_div):
    likes_element = review_div.select_one("[id^=rptreviews_ctl][id$=_divlike] > a")
    if likes_element:
        likes_text = likes_element.get_text(strip=True)
        likes = re.search(r'\d+', likes_text)
        likes = likes.group() if likes else "0"
    else:
        likes = "0"
    return int(likes)


# Function to extract comments from the review_div
def extract_num_comments(review_div):
    comments_element = review_div.select_one("[id^=rptreviews_ctl][id$=_commentspan]")
    if comments_element:
        comments_text = comments_element.get_text(strip=True)
        comments = re.search(r'\d+', comments_text)
        comments = comments.group() if comments else "0"
    else:
        comments = "0"
    return int(comments)

def extract_fake_status(review_div):
    # Adjusted selector to handle dynamic number in the pattern
    fake_element = review_div.select_one("div.stamp > div > span[id^='rptreviews_ctl'][id$='_commentspan']")
    if fake_element:
        fake_status = fake_element.get_text(strip=True)
    else:
        fake_status = "0"
    return fake_status

# Function to read the last page number
async def get_last_page_number(page):
    try:
        last_page_selector = "#spnPaging > li:nth-child(12) > a"
        last_page_element = await page.query_selector(last_page_selector)
        if last_page_element:
            last_page_text = await last_page_element.inner_text()
            return int(last_page_text.strip())
        else:
            return 1  # Fallback to 1 if last page is not found
    except Exception as e:
        print(f"Error finding last page number: {e}")
        return 1

async def extract_reviews(page, base_url, last_page, product_name):
    review_count = 0

    # Create a folder for the product if it doesn't exist
    folder_name = product_name.replace(" ", "_")  # Use underscores instead of spaces for folder names
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for page_number in range(1, last_page + 1):
        try:
            # Construct the URL for the current page
            current_url = f"{base_url}-page-{page_number}"
            print(f"Scraping page {page_number} from URL: {current_url}...")

            await page.goto(current_url)

            # Add a delay to ensure the page fully loads
            await page.wait_for_timeout(2000)

            page_source = await page.content()
            soup = BeautifulSoup(page_source, 'html.parser')

            # Use a selector to find div elements with class "row review-article"
            review_divs = soup.select('#dvreview-listing > div[class="row review-article"]')

            all_reviews = []

            # Extract data from each review
            for review_div in review_divs:
                review_title    = extract_review_title(review_div)  # Extract the review title
                review_text     = extract_review_text(review_div)
                star_rating     = extract_star_rating_from_review(review_div)
                review_datetime = extract_review_datetime(review_div)
                location        = extract_location(review_div)
                likes           = extract_likes(review_div)
                comments        = extract_num_comments(review_div)
                fake_status     = extract_fake_status(review_div)

                review_data = {
                    'Product'      : product_name,
                    'Title'        : review_title,  # Add review title to the data
                    'Rating'       : star_rating,
                    'Review Text'  : review_text,
                    'Date and Time': review_datetime,
                    'Location'     : location,
                    'Likes'        : likes,
                    'Comments'     : comments,
                    'Fake Status'  : fake_status,
                }

                all_reviews.append(review_data)

            # Save reviews to a CSV file per page in the product folder
            if all_reviews:
                df = pd.DataFrame(all_reviews)
                # Reorder columns to include 'Title' and move 'Product' to the beginning
                columns_order = ['Product', 'Rating', 'Title', 'Review Text', 'Date and Time', 'Location', 'Likes', 'Comments', 'Fake Status']
                df = df[columns_order]
                
                # Save the DataFrame to CSV
                csv_filename = os.path.join(folder_name, f"{product_name.replace(' ', '_')}_page_{page_number}.csv")
                df.to_csv(csv_filename, mode='w', header=True, index=False)

            review_count += len(review_divs)

            if page_number == last_page:
                print(f"Reached the last page: {last_page}. Exiting.")
                break

        except Exception as e:
            print(f"Error occurred during review extraction: {e}")
            break

    return review_count

# Updated run_scraper to pass the current URL
async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Load the CSV file with the links
        file_path = 'extracted_links.csv'
        extracted_links_df = pd.read_csv(file_path)
        print(extracted_links_df)

        for index, row in extracted_links_df.iterrows():
            url = row['Link']
            await page.goto(url)
            await page.wait_for_timeout(2000)  # Wait for 2 seconds

            # Get the last page number
            last_page = await get_last_page_number(page)
            print(f"Last page number: {last_page}")

            # Extract reviews until the last page
            product_name = row['Text']
            await extract_reviews(page, url, last_page, product_name)

        await browser.close()
        print("Reviews extraction complete.")

# For environments with a running event loop
async def main():
    await run_scraper()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())