#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import os

# File name containing the URLs
file_name = 'BajajLinks.txt'
# Directory where the output files will be stored
output_directory = 'Articles'

# Create the output directory if it does not exist
os.makedirs(output_directory, exist_ok=True)

# Read URLs from the file
with open(file_name, 'r') as file:
    urls = [line.strip() for line in file if line.strip()]

# Function to fetch and parse a URL
def fetch_and_parse(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

# Function to format and extract text, including bold inline
def format_text(element):
    # Replace bold tags (<b> and <strong>) with a markdown-style indication for bold
    for bold in element.find_all(['strong', 'b']):
        bold.string = f"**{bold.get_text().strip()}**"
    return element.get_text().strip()

# Function to extract and write content from a page
def extract_content(soup, f_out):
    # Try to find the specific container for the main content: <div class="post-content">
    container = soup.find('div', class_='post-content')
    
    # Check if the container was found
    if container:
        # Find all headings, paragraph elements, and <div class="text-yellow">
        elements = container.find_all(['h2', 'h3', 'h4', 'p', 'div'])
        
        # Iterate through each element and write to file
        for element in elements:
            # Only include <div> elements with class "text-yellow"
            if element.name == 'div' and 'text-yellow' not in element.get('class', []):
                continue

            text = format_text(element)
            if element.name in ['h2', 'h3', 'h4']:  # Headings
                f_out.write(f"\n**{text}**\n")
            elif element.name == 'p' or (element.name == 'div' and 'text-yellow' in element.get('class', [])):  # Paragraphs or text-yellow divs
                f_out.write(f"{text}\n")
    else:
        f_out.write("Main content container (<div class='post-content'>) not found.\n")

# Function to extract all pagination links
def get_pagination_links(soup):
    pagination_links = []
    page_links_container = soup.select_one('div.page-links')
    
    if page_links_container:
        # Find all the anchor tags within the pagination container
        page_links = page_links_container.find_all('a')
        for link in page_links:
            page_url = link.get('href')
            if page_url and page_url not in pagination_links:
                pagination_links.append(page_url)
    
    return pagination_links

# Iterate through each URL and perform the operations
for url in urls:
    # Create a filename based on the URL
    url_filename = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
    output_file = os.path.join(output_directory, f"{url_filename}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(f"URL: {url}\n\n")
        
        # Fetch and parse the main page
        soup = fetch_and_parse(url)
        
        if soup:
            # Extract and write content from the main page
            extract_content(soup, f_out)
            
            # Check if there are multiple pages
            pagination_links = get_pagination_links(soup)
            
            # If pagination links are found, fetch and extract content from each page
            for page_url in pagination_links:
                f_out.write(f"\nProcessing additional page: {page_url}\n\n")
                page_soup = fetch_and_parse(page_url)
                if page_soup:
                    extract_content(page_soup, f_out)
        else:
            f_out.write("Failed to parse the main page.\n")

