#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import os
import re

# Load URLs from a plain text file (one URL per line)
url_file_path = 'BajajLinks.csv'
with open(url_file_path, 'r') as file:
    urls = [line.strip() for line in file if line.strip()]

# Function to sanitize URL for filenames
def sanitize_filename(url):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', url)

# Directory to save output files
output_dir = 'Articles'
os.makedirs(output_dir, exist_ok=True)

# Iterate over URLs and process each
for url in urls:
    try:
        # Request page content
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title and body text based on provided CSS selectors
        title = soup.select_one('body > div.site-container > div > div > main > article > header > h1')
        body_text = soup.select_one('body > div.site-container > div > div > main > article > div')
        
        # Get text and sanitize for output
        title_text = title.get_text(strip=True) if title else 'No Title'
        
        # Remove the `div.author_info` content
        author_info = body_text.select_one('div.author_info') if body_text else None
        if author_info:
            author_info.decompose()
        
        # Get all paragraphs within the body div
        paragraphs = body_text.find_all('p') if body_text else []
        body_text_content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

        # Create a filename based on the URL
        filename = sanitize_filename(url) + '.txt'
        file_path = os.path.join(output_dir, filename)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title_text}\n\n")
            f.write(f"Body Text:\n{body_text_content}")
        
        print(f"Content for {url} saved to {file_path}")

    except Exception as e:
        print(f"Failed to retrieve or parse {url}: {e}")

