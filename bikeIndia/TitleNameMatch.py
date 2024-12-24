#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define the list of vehicle names with 'Bajaj' added, one per line
vehicle_names = [
    "Bajaj CT110",
    "Bajaj CT110X",
    "Bajaj CT125X",
    "Bajaj Platina 100",
    "Bajaj Platina CT110",
    "Bajaj Platina 110 H-Gear",
    "Bajaj Pulsar 125",
    "Bajaj Pulsar NS125",
    "Bajaj Pulsar N125",
    "Bajaj Pulsar 150",
    "Bajaj Pulsar N150",
    "Bajaj Pulsar P150",
    "Bajaj Pulsar NS160",
    "Bajaj Pulsar N160",
    "Bajaj Pulsar 180",
    "Bajaj Pulsar 180F",
    "Bajaj Pulsar 220F",
    "Bajaj Pulsar NS200",
    "Bajaj Pulsar RS200",
    "Bajaj Pulsar N250",
    "Bajaj Pulsar F250",
    "Bajaj Pulsar NS400Z",
    "Bajaj Dominar 250",
    "Bajaj Dominar 400",
    "Bajaj Avenger Street 160",
    "Bajaj Avenger Cruise 220",
    "Bajaj Chetak"
]

# Normalize the vehicle names
def normalize_name(name):
    """Remove specific prefixes, file extensions, replace special characters with space, retain numbers, and convert to lowercase."""
    name = re.sub(r'^https___bikeindia_in_', '', name)  # Remove the specified prefix
    name = re.sub(r'\.[a-zA-Z0-9]+$', '', name)  # Remove file extension
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', name).lower()  # Replace special characters with space

# Matching algorithm using partial matches
def match_file_names(file_names, bike_names):
    normalized_bikes = [normalize_name(name) for name in bike_names]
    matches = {}

    for file in file_names:
        # Normalize the file name
        normalized_file = normalize_name(file)

        # Combine file name and bike names for vectorization
        all_texts = [normalized_file] + normalized_bikes

        # Vectorize using TF-IDF
        vectorizer = TfidfVectorizer()  # Unigram-based vectorization
        vectors = vectorizer.fit_transform(all_texts)
        similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

        # Get the best match based on similarity scores
        best_match_index = similarities.argmax()
        best_match_score = similarities[best_match_index]

        # Allow partial matches with a lower threshold
        if best_match_score > 0.1:  # Adjust threshold as needed
            matches[file] = bike_names[best_match_index]
        else:
            matches[file] = "No Match"
    return matches

# Write the best match to the second line of the file
def write_best_match_to_file(file_path, best_match):
    try:
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            if len(lines) < 2:
                # If the file has fewer than 2 lines, add a new second line
                while len(lines) < 1:
                    lines.append("\n")  # Ensure at least one line
                lines.append(f"Bike: {best_match}\n")
            else:
                # Overwrite the second line with the best match
                lines[1] = f"Bike: {best_match}\n"

            # Write the updated content back to the file
            file.seek(0)
            file.writelines(lines)
            file.truncate()
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

# Folder path containing the files in the "Article" folder
folder_path = "./Articles"  # Replace with the relative or absolute path to the Article folder

# Read all file names in the folder
if os.path.exists(folder_path):
    file_names = os.listdir(folder_path)
else:
    print(f"The folder '{folder_path}' does not exist.")
    file_names = []

# Match file names with vehicle names
matches = match_file_names(file_names, vehicle_names)

# Update the second line of each file with the best match
for file in file_names:
    file_path = os.path.join(folder_path, file)
    best_match = matches.get(file, "No Match")
    write_best_match_to_file(file_path, best_match)

# Combine results for reporting
final_results = [{"File Name": file, "Best Match (TF-IDF)": matches.get(file, "No Match")} for file in file_names]

# Convert results to a DataFrame for better readability
results_df = pd.DataFrame(final_results)

# Save results to a CSV file
results_df.to_csv("file_name_matches_with_best_match.csv", index=False)

# Print the results
print("File Name - Best Match (TF-IDF)")
print(results_df)

