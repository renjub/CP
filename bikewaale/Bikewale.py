#!/usr/bin/env python
# coding: utf-8

import asyncio
import os
from playwright.async_api import async_playwright
import csv


async def get_and_process_reviews(bike_name, page, page_number):
    all_reviews = []
    try:
        while True:  # Loop until no more reviews are found
            try:
                await page.wait_for_selector("#user-review-header > div > div > div.o-brXWGL > div.o-dJmcbh > div > ul > li", timeout=5000)
                review_items = await page.query_selector_all("#user-review-header > div > div > div.o-brXWGL > div.o-dJmcbh > div > ul > li")
                print(f"Found {len(review_items)} reviews on page {page_number}.")

                for review_item in review_items:
                    try:
                        title_element = await review_item.query_selector("div > div > a > p")
                        title_text = (await title_element.text_content()).strip() if title_element else "No Title"

                        review_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > p.o-eemiLE.o-cYdrZi.o-cJrNdO.o-fyWCgU"
                        )
                        review_text = (await review_element.text_content()).strip() if review_element else "No Review"

                        time_element = await review_item.query_selector(
                            "div > div > div.o-fzpihx.o-fzptYC.o-eemiLE.o-zmksK.o-cpnuEd > p:nth-child(1)"
                        )
                        time_text = (await time_element.text_content()).strip() if time_element else "No Time"

                        design_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div:nth-child(2) > div.o-biwSqu.o-qqdXv.o-XylGE.o-cpnuEd > div:nth-child(1) > div > div > span"
                        )
                        design_text = (await design_element.text_content()).strip() if design_element else "No Design Rating"

                        reliability_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div:nth-child(2) > div.o-biwSqu.o-qqdXv.o-XylGE.o-cpnuEd > div:nth-child(3) > div > div > span"
                        )
                        reliability_text = (await reliability_element.text_content()).strip() if reliability_element else "No Reliability Rating"

                        comfort_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div:nth-child(2) > div.o-biwSqu.o-qqdXv.o-XylGE.o-cpnuEd > div:nth-child(5) > div > div > span"
                        )
                        comfort_text = (await comfort_element.text_content()).strip() if comfort_element else "No Comfort Rating"

                        service_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div:nth-child(2) > div.o-biwSqu.o-qqdXv.o-XylGE.o-cpnuEd > div:nth-child(7) > div > div > span"
                        )
                        service_text = (await service_element.text_content()).strip() if service_element else "No Service Experience"

                        value_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div:nth-child(2) > div.o-biwSqu.o-qqdXv.o-XylGE.o-cpnuEd > div:nth-child(9) > div > div > span"
                        )
                        value_text = (await value_element.text_content()).strip() if value_element else "No Value Rating"

                        used_for_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div.eoWUQZ.o-bUVylL.o-XylGE.o-cpnuEd > div:nth-child(1) > p.o-eemiLE.o-eqqVmt.o-cJrNdO"
                        )
                        used_for_text = (await used_for_element.text_content()).strip() if used_for_element else "No Data"

                        ridden_for_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div.eoWUQZ.o-bUVylL.o-XylGE.o-cpnuEd > div:nth-child(3) > p.o-eemiLE.o-eqqVmt.o-cJrNdO"
                        )
                        ridden_for_text = (await ridden_for_element.text_content()).strip() if ridden_for_element else "No Data"

                        ridden_owned_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div.eoWUQZ.o-bUVylL.o-XylGE.o-cpnuEd > div:nth-child(4) > p.o-eemiLE.o-eqqVmt.o-cJrNdO"
                        )
                        ridden_owned_text = (await ridden_owned_element.text_content()).strip() if ridden_owned_element else "No Data"

                        owned_for_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div.eoWUQZ.o-bUVylL.o-XylGE.o-cpnuEd > div:nth-child(2) > p.o-eemiLE.o-eqqVmt.o-cJrNdO"
                        )
                        owned_for_text = (await owned_for_element.text_content()).strip() if owned_for_element else "No Data"

                        tips_element = await review_item.query_selector(
                            "div > div > div:nth-child(4) > div > div.o-bfyaNx.o-bNxxEB.o-bqHweY > div > div > div.o-fznVme > p.o-eemiLE.o-cJrNdO.o-fyWCgU.o-fzptUA"
                        )
                        tips_text = (await tips_element.text_content()).strip() if tips_element else "No Tips"

                        useful_element = await review_item.query_selector(
                            "div > div > div.o-cpnuEd.o-dsiSgT.o-bUVylL.o-fznJzb > div > div:nth-child(1) > p"
                        )
                        useful_text = (await useful_element.text_content()).strip() if useful_element else "No Data"

                        not_useful_element = await review_item.query_selector(
                            "div > div > div.o-cpnuEd.o-dsiSgT.o-bUVylL.o-fznJzb > div > div:nth-child(3) > p"
                        )
                        not_useful_text = (await not_useful_element.text_content()).strip() if not_useful_element else "No Data"

                        stars_container = await review_item.query_selector(
                            "div.o-fcaNGp.o-dsiSgT.o-NBTwp.o-dGBYL.o-bdcqQE"
                        )
                        filled_star_elements = await stars_container.query_selector_all("svg.o-vYvcJ")
                        num_stars = len(filled_star_elements) if filled_star_elements else 0

                        all_reviews.append({
                            'Bike': bike_name,
                            'Stars': num_stars,
                            'Title': title_text,
                            'Review': review_text,
                            'Time': time_text,
                            'Design and styling': design_text,
                            'Reliability': reliability_text,
                            'Comfort': comfort_text,
                            'Service experience': service_text,
                            'Value for money': value_text,
                            'Used it for': used_for_text,
                            'Ridden for': ridden_for_text,
                            'Ridden for if owned': ridden_owned_text,
                            'Owned for': owned_for_text,
                            'Tips for other riders': tips_text,
                            'Review was useful': useful_text,
                            'Review was not useful': not_useful_text
                        })

                    except Exception as e:
                        print(f"Error processing review: {e}")

                next_button = await page.query_selector(".pagination-next")
                if next_button:
                    await next_button.click()
                    await page.wait_for_timeout(1000)
                    page_number += 1
                else:
                    break

            except TimeoutError:
                print("Timeout while waiting for reviews to load.")
                break

    except Exception as e:
        print(f"Error in review processing: {e}")
    
    return all_reviews


def save_reviews_to_csv(reviews, bike_name, page_number):
    folder_name = f"reviews/{bike_name}"
    os.makedirs(folder_name, exist_ok=True)
    
    file_name = f"{folder_name}/page_{page_number}.csv"
    with open(file_name, 'w', newline='', encoding='utf-8') as f_csv:
        writer = csv.writer(f_csv, quoting=csv.QUOTE_ALL)
        writer.writerow([
            'Bike', 'Stars', 'Title', 'Review', 'Time', 'Design and styling', 'Reliability', 'Comfort',
            'Service experience', 'Value for money', 'Used it for', 'Ridden for',
            'Ridden for if owned', 'Owned for', 'Tips for other riders', 'Review was useful',
            'Review was not useful'
        ])
        for review in reviews:
            writer.writerow([
                review.get('Bike', 'No Bike'),
                review.get('Stars', 'No Stars'),
                review.get('Title', 'No Title'),
                review.get('Review', 'No Review'),
                review.get('Time', 'No Time'),
                review.get('Design and styling', 'No Design Rating'),
                review.get('Reliability', 'No Reliability Rating'),
                review.get('Comfort', 'No Comfort Rating'),
                review.get('Service experience', 'No Service Experience'),
                review.get('Value for money', 'No Value Rating'),
                review.get('Used it for', 'No Data'),
                review.get('Ridden for', 'No Data'),
                review.get('Ridden for if owned', 'No Data'),
                review.get('Owned for', 'No Data'),
                review.get('Tips for other riders', 'No Tips'),
                review.get('Review was useful', 'No Data'),
                review.get('Review was not useful', 'No Data')
            ])
    print(f"Saved {len(reviews)} reviews to {file_name}.")


def read_urls_from_file(file_path):
    bike_data = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as f_csv:
        reader = csv.reader(f_csv)
        next(reader)  # Skip the header row
        for row in reader:
            bike_data.append((row[0], row[1]))  # Extract the Text (bike name) and URL
    return bike_data


async def scrape_reviews():
    bike_data = read_urls_from_file('BajajLinks.csv')
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        
        for bike_name, url in bike_data:
            print(bike_name, url)
            page = await browser.new_page()
            await page.goto(url)

            try:
                page_number = 1
                while True:
                    all_reviews = await get_and_process_reviews(bike_name, page, page_number)
                    
                    if all_reviews:
                        save_reviews_to_csv(all_reviews, bike_name, page_number)

                    next_button = await page.query_selector("#user-review-header > div > ul > li.o-bdccbU.o-fzoTpF > a > span > svg")
                    if next_button:
                        await next_button.click()
                        await page.wait_for_timeout(2000)
                        page_number += 1
                    else:
                        print(f"No more pages for {url}.")
                        break

            except TimeoutError:
                print(f"Timeout while scraping {url}.")
            
            await page.close()

        await browser.close()
        print("Finished scraping all URLs.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(scrape_reviews())
