#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import re
import pandas as pd

# Function to extract headings, bold text, and associated content
def extract_content(text, ignore_words):
    # Find all headings and bold text with their positions
    pattern = r"(## Heading: .+?|\*\*(.+?)\*\*)"
    matches = list(re.finditer(pattern, text))

    extracted_data = []

    for i, match in enumerate(matches):
        heading_or_bold = match.group(0)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        # Remove lines starting with specific phrases
        content = '\n'.join([line for line in content.splitlines() if not line.startswith("Processing additional page:") and not line.startswith("Home » Bike News")])

        # Filter out ignored words in bold text or heading
        if not any(word in heading_or_bold for word in ignore_words):
            extracted_data.append([heading_or_bold, content])

    return extracted_data

# Process all .txt files in the current directory
def process_txt_files():
    ignore_words = [
        "Bike Tested", "Price OTR", "Further Reading",
        "Alternatives", "Road Test No", "Test Location",
        "Riders", "Picture Editing",
        "Specifications", "Dimensions"
    ]

    current_folder = os.getcwd()
    txt_files = [f for f in os.listdir(current_folder) if f.endswith('.txt')]

    if not txt_files:
        print("No .txt files found in the current folder.")
        return

    output_folder = os.path.join(current_folder, 'output_files')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for txt_file in txt_files:
        print(f"\nProcessing file: {txt_file}")
        with open(txt_file, 'r', encoding='utf-8') as file:
            content = file.read()

        extracted_data = extract_content(content, ignore_words)

        # Remove ** from bold text in the extracted data
        extracted_data = [[re.sub(r"\*\*(.+?)\*\*", r"\1", item[0]), item[1]] for item in extracted_data]

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(extracted_data, columns=["Heading/Bold Text", "Content"])
        print(df["Heading/Bold Text"])
        print(df)

        # Save the DataFrame to a CSV file for each input file
        output_file = os.path.join(output_folder, f"{os.path.splitext(txt_file)[0]}_extracted.csv")
        df.to_csv(output_file, index=False)

if __name__ == "__main__":
    process_txt_files()

