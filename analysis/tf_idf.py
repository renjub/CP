import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Load the CSV file into a DataFrame (replace 'your_file.csv' with your actual file path)
file_path = 'reviews_short.csv'  # Update this with the actual path to your file
data = pd.read_csv(file_path)

# Ensure 'Review' column is free of NaN and convert to string type
data['Review'] = data['Review'].fillna('').astype(str)

# Extract the 'Review' column
reviews = data['Review'].tolist()

# Initialize the TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit and transform the reviews into TF-IDF matrix
tfidf_matrix = tfidf_vectorizer.fit_transform(reviews)

# Get feature names (unique words)
feature_names = tfidf_vectorizer.get_feature_names_out()

# Convert the TF-IDF matrix into a readable format
tfidf_matrix_dense = tfidf_matrix.todense()

# Print the top 3 TF-IDF scores for each review
for i, review in enumerate(tfidf_matrix_dense):
    print(f"Review {i+1} top 3 TF-IDF scores:")
    
    # Convert the row to a list of tuples (word, score)
    word_score_pairs = list(zip(feature_names, review.tolist()[0]))
    
    # Sort the words by TF-IDF score in descending order
    sorted_word_score_pairs = sorted(word_score_pairs, key=lambda x: x[1], reverse=True)
    
    # Print the top 3 words with the highest TF-IDF scores
    for word, score in sorted_word_score_pairs[:3]:
        print(f"{word}: {score:.4f}")
    print("\n")