import re
import os
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(filename='output.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
    title_element = review_div.find('a', id=re.compile(r'rptreviews_ctl\d+_lnkTitle'))
    return title_element.get_text(strip=True) if title_element else "-"

# Function to extract review text from the review_div
def extract_review_text(review_div):
    review_element = review_div.select_one("div.more.reviewdata > p")
    return review_element.get_text(strip=True) if review_element else "-"

# Function to extract date and time from the review_div
def extract_review_datetime(review_div):
    datetime_element = review_div.find('span', id=re.compile(r'^rptreviews_ctl\d+_lblDateTime$'))
    return datetime_element.get_text(strip=True) if datetime_element else "-"

# Function to extract location from the review_div
def extract_location(review_div):
    location_div = review_div.find("div", id=re.compile(r'rptreviews_ctl\d+_divProfile'))
    if location_div:
        address_div = location_div.find("div", class_="usr-addr-text")
        return address_div.get_text(strip=True) if address_div else "-"
    return "-"    

# Function to extract likes from the review_div
def extract_likes(review_div):
    likes_element = review_div.select_one("[id^=rptreviews_ctl][id$=_divlike] > a")
    if likes_element:
        likes_text = likes_element.get_text(strip=True)
        likes = re.search(r'\d+', likes_text)
        return int(likes.group() if likes else "0")
    return 0

# Function to extract comments from the review_div
def extract_num_comments(review_div):
    comments_element = review_div.select_one("[id^=rptreviews_ctl][id$=_commentspan]")
    if comments_element:
        comments_text = comments_element.get_text(strip=True)
        comments = re.search(r'\d+', comments_text)
        return int(comments.group() if comments else "0")
    return 0

def extract_fake_status(review_div):
    fake_element = review_div.select_one("div.stamp > div > span[id^='rptreviews_ctl'][id$='_commentspan']")
    return fake_element.get_text(strip=True) if fake_element else "0"

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
        logging.error(f"Error finding last page number: {e}")
        return 1

async def extract_reviews(page, base_url, last_page, product_name):
    review_count = 0
    folder_name = product_name.replace(" ", "_")
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for page_number in range(1, last_page + 1):
        try:
            current_url = f"{base_url}-page-{page_number}"
            logging.info(f"Scraping page {page_number} from URL: {current_url}...")
            await page.goto(current_url)
            await page.wait_for_timeout(2000)
            page_source = await page.content()
            soup = BeautifulSoup(page_source, 'html.parser')

            review_divs = soup.select('#dvreview-listing > div[class="row review-article"]')
            all_reviews = []

            for review_div in review_divs:
                review_data = {
                    'Product'      : product_name,
                    'Title'        : extract_review_title(review_div),
                    'Rating'       : extract_star_rating_from_review(review_div),
                    'Review Text'  : extract_review_text(review_div),
                    'Date and Time': extract_review_datetime(review_div),
                    'Location'     : extract_location(review_div),
                    'Likes'        : extract_likes(review_div),
                    'Comments'     : extract_num_comments(review_div),
                    'Fake Status'  : extract_fake_status(review_div),
                }
                all_reviews.append(review_data)

            if all_reviews:
                df = pd.DataFrame(all_reviews)
                columns_order = ['Product', 'Rating', 'Title', 'Review Text', 'Date and Time', 'Location', 'Likes', 'Comments', 'Fake Status']
                df = df[columns_order]
                csv_filename = os.path.join(folder_name, f"{product_name.replace(' ', '_')}_page_{page_number}.csv")
                df.to_csv(csv_filename, mode='w', header=True, index=False)

            review_count += len(review_divs)
            if page_number == last_page:
                logging.info(f"Reached the last page: {last_page}. Exiting.")
                break

        except Exception as e:
            logging.error(f"Error occurred during review extraction: {e}")
            break

    return review_count

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = 'extracted_links.csv'
        extracted_links_df = pd.read_csv(file_path)
        logging.info(extracted_links_df)

        for index, row in extracted_links_df.iterrows():
            url = row['Link']
            await page.goto(url)
            await page.wait_for_timeout(2000)
            last_page = await get_last_page_number(page)
            logging.info(f"Last page number: {last_page}")
            product_name = row['Text']
            await extract_reviews(page, url, last_page, product_name)

        await browser.close()
        logging.info("Reviews extraction complete.")

async def main():
    await run_scraper()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())