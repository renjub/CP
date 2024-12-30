#!/usr/bin/env python
# coding: utf-8

import nest_asyncio
import asyncio
import pandas as pd
from playwright.async_api import async_playwright

# Allow nested async calls in Jupyter Notebook
nest_asyncio.apply()

async def fetch_links_and_texts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.bikewale.com/bajaj-bikes/")

        # Selector for the container
        container_selector = "#root > div > div.body-content > div > div.o-bWHzMb.o-ducbvd.o-cglRxs.Phu9vg.o-fpkJwH.o-dCyDMp > div.MizGdg.fEMaCt > div.o-dpDliG.o-eAyrtt.o-cglRxs.lSq7kt.o-fpkJwH.o-dCyDMp.o-efHQCX > section > div:nth-child(3)"

        # Wait for the container to be visible
        await page.wait_for_selector(container_selector)

        # Extract links and their text content
        links_and_texts = await page.eval_on_selector_all(
            f"{container_selector} a",  # CSS selector for `<a>` tags
            """
            elements => elements.map(el => ({
                href: el.href,
                text: el.textContent.trim()
            }))
            """
        )

        await browser.close()
        return links_and_texts

async def main():
    links_and_texts = await fetch_links_and_texts()
    
    # Create a DataFrame
    df = pd.DataFrame(links_and_texts)
    
    # Rename columns and reorder them
    df = df.rename(columns={"text": "Text", "href": "Link"})
    df = df[["Text", "Link"]]  # Reorder columns to make "Text" the first column

    # Append "/reviews/" to each link
    df["Link"] = df["Link"].apply(lambda x: f"{x}reviews/")
    
    # Save DataFrame to CSV
    file_path = "BajajLinks.csv"
    df.to_csv(file_path, index=False)
    print(f"Data successfully written to {file_path}")

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())
