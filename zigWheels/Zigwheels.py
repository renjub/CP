#!/usr/bin/env python
# coding: utf-8

import time
import os
import sys
from bs4 import BeautifulSoup
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
import csv
import re

# Apply nest_asyncio to allow nested event loops in Jupyter
nest_asyncio.apply()

async def get_total_review_count(page):
    try:
        page_source = await page.content()
        soup = BeautifulSoup(page_source, 'html.parser')
        element = soup.select_one('body > main > div > div > div.pull-left.bodyLeft > div.ur-mct.rcat > div.col-lg-4.col-md-4.col-sm-4.col-xs-12 > div > div > div.clr-bl.ur-rc > div.fnt-12.clr.clr-sry.pull-left')

        if element:
            text = element.get_text(strip=True)
            match = re.search(r'Based on (\d+) reviews', text)
            if match:
                return int(match.group(1))
            else:
                print("Number of reviews not found in the text.")
                return None
        else:
            print("Element not found.")
            return None
    except Exception as e:
        print(f"An error occurred while fetching total reviews: {e}")
        return None

async def click_load_more_review_button(page, bike_name):
    total_reviews = await get_total_review_count(page)
    if total_reviews is None:
        print("Could not fetch the total number of reviews. Exiting.")
        return

    print(f"Total reviews to load for '{bike_name}': {total_reviews}")

    while True:
        try:
            review_blocks = await page.query_selector_all('#userReviews8 [id^="overflow_hidden_"]')
            current_reviews_count = len(review_blocks)
            print(f"Current reviews displayed: {current_reviews_count}")

            if current_reviews_count >= total_reviews:
                print("All reviews are loaded. Exiting the function.")
                break

            load_more_button = await page.query_selector('#loadMore8')
            if load_more_button:
                await load_more_button.scroll_into_view_if_needed()
                await load_more_button.click()
                print("Clicked on the 'Load More Reviews' button.")
                await asyncio.sleep(3)
            else:
                print("No more 'Load More Reviews' button found. Exiting the function.")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

async def get_reviews(page):
    page_source = await page.content()
    soup = BeautifulSoup(page_source, 'html.parser')

    all_reviews = []
    review_blocks = soup.select('#userReviews8 [id^="overflow_hidden_"]')

    for block in review_blocks:
        review_data = {}

        top_zw_voice = block.select_one('div > div.col-sm-2.nc-ndc.remove-clr > div.ndc-mr > span.fnt-12.clr-sry') or \
                       block.select_one('div > div.col-sm-2.nc-ndc.remove-clr > div.ndc-mr.pt-10 > span.fnt-12.clr-sry')

        badge = block.select_one('div > div.col-sm-2.nc-ndc.remove-clr > div.ndc-mr > div > span > span')

        title = block.select_one('div > div.col-sm-10.col-xs-12 > div > div.f-rv-des.mb-10.clr-bl > div.row.clr > div.col-sm-10.col-xs-10 > p') or \
                block.select_one('div > div.col-sm-10.col-xs-12 > div > div.row.clr > div.col-sm-10.col-xs-10 > p')

        review_text = block.select_one('div > div.col-sm-10.col-xs-12 > div > div.f-rv-des.mb-10.clr-bl > div.read-more.ht-4lines.rm > p') or \
                      block.select_one('div > div.col-sm-10.col-xs-12 > div > div.read-more > p')

        likes = block.select_one('[id^="review_"]')

        star_rating = block.select_one('div > div.col-sm-10.col-xs-12 > div > div.f-rv-des.mb-10.clr-bl > div.row.clr > div.col-sm-2.col-xs-2.text-right.pl-0.pr-0 > span > span')

        review_data['Top_ZW_Voice'] = top_zw_voice.get_text(strip=True) if top_zw_voice else "-"
        review_data['Badge']        = badge.get_text(strip=True) if badge else "-"
        review_data['Title']        = title.get_text(strip=True) if title else "-"
        review_data['Review_Text']  = review_text.get_text(strip=True) if review_text else "-"
        review_data['Likes']        = likes.get_text(strip=True) if likes else "-"
        review_data['Star_Rating']  = star_rating.get_text(strip=True) if star_rating else "-"

        all_reviews.append(review_data)

    return all_reviews

def save_reviews_to_csv(reviews, file_name, bike_name):
    # Ensure the 'reviews' folder exists
    folder_path = os.path.join(os.getcwd(), 'reviews')
    os.makedirs(folder_path, exist_ok=True)

    # Construct the full file path
    file_path = os.path.join(folder_path, file_name)

    # Include Bike_Name in the headers
    headers = ['Bike', 'Top_ZW_Voice', 'Badge', 'Title', 'Review_Text', 'Likes', 'Star_Rating']
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for review in reviews:
            # Add the bike name to each review
            review['Bike'] = bike_name
            writer.writerow(review)
    print(f"Reviews saved to: {file_path}")

def read_urls_from_csv(file_name):
    urls = []
    with open(file_name, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get('Link')
            bike_name = row.get('Text')
            if url and bike_name:
                urls.append((url, bike_name))
            else:
                print(f"Missing URL or BikeName in row: {row}")
    return urls

async def scrape_reviews(url, bike_name, file_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await click_load_more_review_button(page, bike_name)
        all_reviews = await get_reviews(page)
        if all_reviews:
            save_reviews_to_csv(all_reviews, file_name, bike_name)  # Pass bike_name here
        print(f"Reviews for '{bike_name}' saved to {file_name}.")
        await browser.close()

async def main():
    urls = read_urls_from_csv('BajajLinks.csv')
    if not urls:
        print("No URLs found in the CSV file.")
        return
    url, bike_name = urls[0]
    file_name = f"{bike_name.replace(' ', '_').lower()}_reviews.csv"
    await scrape_reviews(url, bike_name, file_name)

asyncio.run(main())