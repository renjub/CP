import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK data
tokenizers_list = ['punkt', 'wordnet', 'omw-1.4']
for tokenizer in tokenizers_list:
    nltk.download(tokenizer)

# Load models
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

# Function to find the best matching bucket and sub-bucket
def assign_bucket_and_sub_bucket(review_text, buckets, embedding_model, similarity_threshold=0.3):
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
    
    # If no match found, assign "Other"
    return "Other", "Other"

# Function to process each CSV file without extracting keywords
def process_csv(file_path):
    print(f"Processing file: {file_path}")  # Print the file name being processed

    # Extract bike name from file name
    bike_name = " ".join(file_path.split("_")[:-1])  # Extract bike name from file name (without 'reviews')

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Check if 'Review' column exists
    if 'Review' not in df.columns:
        raise ValueError(f"The CSV file '{file_path}' must contain a 'Review' column.")

    # Assign buckets and sub-buckets without keywords
    df[['Assigned_Bucket', 'Assigned_Sub_Bucket']] = df['Review'].apply(
        lambda x: pd.Series(assign_bucket_and_sub_bucket(x, buckets, embedding_model, similarity_threshold=0.3))
    )

    # Save the DataFrame to the original CSV file with new columns
    df.to_csv(file_path, index=False)

    print(f"File processed and updated: {file_path}")  # Confirm file is processed

# Sequentially process files in the reviews/*/*.csv directory
csv_files = []
for root, dirs, files in os.walk('reviews'):  # Traverse only the 'reviews' directory
    for file in files:
        print(file)
        if file.endswith('.csv') and root.count(os.sep) == 1:  # Match 'reviews/*/*.csv' structure
            process_csv(os.path.join(root, file))