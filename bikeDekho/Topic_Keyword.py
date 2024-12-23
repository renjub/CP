#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
import torch
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK data
tokenizers_list = ['punkt', 'wordnet', 'omw-1.4']
for tokenizer in tokenizers_list:
    nltk.download(tokenizer)

# Load models
kw_model = KeyBERT(model='all-mpnet-base-v2')  # Improved keyword extraction
embedding_model = SentenceTransformer('all-mpnet-base-v2')  # Most accurate semantic similarity model
lemmatizer = WordNetLemmatizer()  # Initialize lemmatizer

# Synonym-enriched buckets with hierarchical sub-categories
buckets = {
    "Mileage": ["Fuel Efficiency", "Fuel Economy", "Fuel Consumption", "Miles per Gallon"],
    "Comfort": ["Riding Comfort", "Seat Comfort", "Suspension Comfort", "Vibration Control"],
    "Looks": ["Design", "Exterior", "Aesthetics", "Styling", "Color Options"],
    "Performance": ["Acceleration", "Handling", "Stability", "Braking Performance", "Cornering"],
    "Power": ["Horsepower", "Torque", "Engine Output", "Power Delivery"],
    "Engine": ["Engine Sound", "Engine Performance", "Engine Reliability", "Engine Smoothness", "Engine Cooling"],
    "Experience": ["Riding Experience", "Ownership Experience", "Long Ride Experience", "Daily Ride Experience"],
    "Speed": ["Top Speed", "Speed Pickup", "Speed Acceleration", "Speed Stability"],
    "Price": ["Affordability", "Value for Money", "Cost Effectiveness", "Pricing Options", "Discounts"],
    "Service": ["Service Cost", "Service Center Experience", "After Sales Service", "Service Quality", "Service Availability"],
    "Pickup": ["Initial Pickup", "Throttle Response", "Low-End Torque"],
    "Maintenance": ["Maintenance Cost", "Maintenance Frequency", "Maintenance Ease", "Spare Parts Availability"],
    "Seat": ["Seat Comfort", "Seat Design", "Seat Material", "Seat Height"]
}

# Apply lemmatization to normalize bucket names and sub-buckets
buckets = {lemmatizer.lemmatize(bucket.lower()): [lemmatizer.lemmatize(sub.lower()) for sub in sub_buckets] for bucket, sub_buckets in buckets.items()}

# Function to extract keywords for a single review
def extract_keywords_without_bike_name(text, bike_name_words, top_n=3):
    if pd.isna(text):  # Handle missing or NaN values
        return []
    
    # Extract keywords using KeyBERT
    keywords = kw_model.extract_keywords(text, 
                                         keyphrase_ngram_range=(1, 2), 
                                         stop_words=['english', 'bike', 'bajaj'] + bike_name_words, 
                                         top_n=top_n)
    return [keyword for keyword, score in keywords]

# Function to find the best matching bucket and sub-bucket
def assign_bucket_and_sub_bucket(review_text, buckets, embedding_model, similarity_threshold=0.4):
    if pd.isna(review_text):  # Handle missing or NaN values
        return "Other", "Other"
    
    # Flatten buckets into a list of all buckets and sub-buckets
    all_buckets = list(buckets.keys()) + [sub for sublist in buckets.values() for sub in sublist]

    # Generate embeddings for buckets
    bucket_embeddings = embedding_model.encode(all_buckets, convert_to_tensor=True)

    # Generate embedding for the review text
    review_embedding = embedding_model.encode(review_text, convert_to_tensor=True)
    
    # Compute similarity scores
    similarities = util.pytorch_cos_sim(review_embedding, bucket_embeddings)
    max_similarity, best_bucket_index = torch.max(similarities, dim=1)

    # Check if the similarity is above the threshold
    best_bucket = all_buckets[best_bucket_index.item()]
    if max_similarity.item() > similarity_threshold:
        for bucket, sub_buckets in buckets.items():
            if best_bucket == bucket or best_bucket in sub_buckets:
                return bucket, best_bucket
        return best_bucket, best_bucket
    
    # If no match found, assign "Other" bucket
    return "Other", "Other"

# Function to conditionally extract keywords if Assigned_Bucket is 'Other'
def extract_keywords_if_other(review_text, bike_name_words, bucket):
    if bucket == "Other":
        return extract_keywords_without_bike_name(review_text, bike_name_words, top_n=3)
    return ""

# Process all CSV files in the current working directory and subfolders
for root, dirs, files in os.walk('.'):  # Traverse through all subfolders
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")

            # Load the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Skip if 'Assigned_Bucket' column already exists
            if 'Assigned_Bucket' in df.columns:
                print(f"Skipping file '{file_path}' as it already contains the 'Assigned_Bucket' column.")
                continue

            # Extract bike name from file name
            bike_name = " ".join(file_path.split("_")[:-1])  # Extract bike name from file name (without 'reviews')
            bike_name_words = bike_name.lower().split()  # Split bike name into individual words
            bike_name_words.extend(['bike', 'bajaj'])  # Add additional stop words

            # Check if 'Review' column exists
            if 'Review' not in df.columns:
                raise ValueError(f"The CSV file '{file_path}' must contain a 'Review' column.")

            # Apply the functions to assign buckets and extract conditional keywords
            df[['Assigned_Bucket', 'Assigned_Sub_Bucket']] = df['Review'].apply(
                lambda x: pd.Series(assign_bucket_and_sub_bucket(x, buckets, embedding_model, similarity_threshold=0.4))
            )
            df['Keywords'] = df.apply(
                lambda row: extract_keywords_if_other(row['Review'], bike_name_words, row['Assigned_Bucket']),
                axis=1
            )

            # Convert keywords to a string for better readability in the output
            df['Keywords'] = df['Keywords'].apply(lambda x: ", ".join(x) if x else "")

            # Save the DataFrame to the original CSV file with new columns
            df.to_csv(file_path, index=False)

            print(f"Updated the input file '{file_path}' with keywords, assigned buckets, and assigned sub-buckets.")
            print("Sample Keywords Output:")
            print(df['Keywords'].head())

