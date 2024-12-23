#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the webpage
url = "https://www.bikedekho.com/bajaj-bikes"

# Add headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

# Initialize an empty list to store bike data
bike_data = []

# Make a GET request with headers
response = requests.get(url, headers=headers)
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Use a broader selector to find all main bike link elements
    bike_elements = soup.select("div.gsc_col-sm-12.gsc_col-xs-12.gsc_col-md-8.listView.holder.posS > a")
    
    # Extract each bike name and link, excluding specific keywords
    for element in bike_elements:
        bike_name = element.select_one("h3").text.strip() if element.select_one("h3") else "N/A"
        bajaj_links = element['href'] if 'href' in element.attrs else "N/A"
        
        # Exclude unwanted links (e.g., those containing "price-in-delhi")
        if "price-in-delhi" not in bajaj_links.lower():
            bike_data.append({"Bike": bike_name, "Link": bajaj_links})
else:
    print("Failed to retrieve the webpage")

# Create a DataFrame from the list
bike_df = pd.DataFrame(bike_data)

# Write the DataFrame to a CSV file
bike_df.to_csv("BajajLinks.csv", index=False)

print("Data has been written to BajajLinks.csv")

