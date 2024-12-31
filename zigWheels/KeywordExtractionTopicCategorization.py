#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
import torch
from nltk.stem import WordNetLemmatizer
import nltk
import re

# Download necessary NLTK data
tokenizers_list = ['punkt', 'wordnet', 'omw-1.4']
for tokenizer in tokenizers_list:
    nltk.download(tokenizer)

# Load models
kw_model = KeyBERT(model='all-mpnet-base-v2')
embedding_model = SentenceTransformer('all-mpnet-base-v2')
lemmatizer = WordNetLemmatizer()

# Synonym-enriched buckets
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

buckets = {lemmatizer.lemmatize(bucket.lower()): [lemmatizer.lemmatize(sub.lower()) for sub in sub_buckets] for bucket, sub_buckets in buckets.items()}

def extract_keywords_without_bike_name(text, bike_name_words, top_n=3):
    if pd.isna(text):
        return []

    stop_words = set(word for phrase in ['bike', 'bikes', 'motorcycle', 'motorcycles', 'bajaj'] + bike_name_words for word in phrase.lower().split())

    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words=list(stop_words),
        top_n=top_n * 2
    )

    unique_keywords = []
    keyword_embeddings = []

    for keyword, _ in keywords:
        if re.search(r'\d', keyword) or keyword.lower() in stop_words:
            continue

        current_embedding = embedding_model.encode(keyword, convert_to_tensor=True)

        if keyword_embeddings:
            similarities = util.pytorch_cos_sim(current_embedding, torch.stack(keyword_embeddings))
            if max(similarities[0]).item() > 0.8:
                continue

        unique_keywords.append(keyword)
        keyword_embeddings.append(current_embedding)

        if len(unique_keywords) == top_n:
            break

    return unique_keywords

def assign_bucket_and_sub_bucket(review_text, buckets, embedding_model, similarity_threshold=0.3):
    if pd.isna(review_text):
        return "Other", "Other"

    # Combine main buckets and sub-buckets for embedding
    all_buckets = list(buckets.keys()) + [sub for sublist in buckets.values() for sub in sublist]
    bucket_embeddings = embedding_model.encode(all_buckets, convert_to_tensor=True)
    review_embedding = embedding_model.encode(review_text, convert_to_tensor=True)

    # Calculate similarity
    similarities = util.pytorch_cos_sim(review_embedding, bucket_embeddings)
    max_similarity, best_bucket_index = torch.max(similarities, dim=1)

    # Check if similarity exceeds new threshold (0.3)
    if max_similarity.item() > similarity_threshold:
        best_bucket = all_buckets[best_bucket_index.item()]
        for bucket, sub_buckets in buckets.items():
            if best_bucket == bucket or best_bucket in sub_buckets:
                return bucket, best_bucket
        return best_bucket, best_bucket

    # If no bucket is found, perform keyword extraction
    keywords = extract_keywords_without_bike_name(review_text, [], top_n=1)
    top_keyword = keywords[0] if keywords else "Other"
    return "Other", top_keyword

def process_file(file_path):
    print(f"Processing file: {file_path}")
    df = pd.read_csv(file_path)

    if 'Review' not in df.columns or 'Bike' not in df.columns:
        raise ValueError(f"The CSV file '{file_path}' must contain 'Review' and 'Bike' columns.")

    print(f"Initial DataFrame loaded for file: {file_path}")
    bike_name_words = df['Bike'].str.lower().dropna().unique()

    # Assign buckets and sub-buckets
    def assign_and_extract(row):
        bucket, sub_bucket = assign_bucket_and_sub_bucket(row['Review'], buckets, embedding_model, similarity_threshold=0.3)
        
        # Perform keyword extraction **only if bucket is 'Other'**
        if bucket == "Other":
            keywords = extract_keywords_without_bike_name(row['Review'], bike_name_words, top_n=3)
        else:
            keywords = []  # No keywords for other assigned buckets
        
        return pd.Series([bucket, sub_bucket, ", ".join(keywords)])

    df[['Assigned_Bucket', 'Assigned_Sub_Bucket', 'Keywords']] = df.apply(assign_and_extract, axis=1)

    print(f"Saving updated file: {file_path}")
    df.to_csv(file_path, index=False)
    print(f"File successfully updated: {file_path}")

# Directory for review files
review_folder = './reviews'

csv_files = [os.path.join(review_folder, file) for file in os.listdir(review_folder) if file.endswith('.csv')]

for file_path in csv_files:
    process_file(file_path)