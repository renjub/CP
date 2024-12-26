import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from keybert import KeyBERT
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import pandas as pd

# Step 1: Get Articles Folder Path
folder_path = os.path.join(os.getcwd(), "Articles")  # Point to 'Articles' folder

# Step 2: Read text files, extract title, bike name, and content
def read_articles_with_bike_names_and_titles(folder_path, prefix):
    articles = []
    filenames = []
    bike_names = []
    titles = []

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        # Only process .txt files, ignore folders
        if os.path.isfile(filepath) and filename.startswith(prefix) and filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    # Extract title from the first line
                    title = lines[0].strip().replace("Title: ", "").strip()

                    # Extract bike name from the second line
                    bike_name = lines[1].strip().replace("Bike: ", "").strip()

                    # Extract content excluding the title and bike name
                    content = "".join(lines[2:])  # Exclude first two lines from content

                    titles.append(title)
                    bike_names.append(bike_name)
                    articles.append(content)
                    filenames.append(filename)
    return filenames, titles, bike_names, articles

# Specify the prefix for filtering
prefix = "https___bikeindia_in_"
filenames, titles, bike_names, articles = read_articles_with_bike_names_and_titles(folder_path, prefix)

# Step 3: Load Trained Model and Tokenizer
trained_model_path = os.path.expanduser("~/TrainedModelFinal")  # Updated path to the trained model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(trained_model_path)
model = AutoModelForSequenceClassification.from_pretrained(trained_model_path)

# Define a pipeline using the trained model
longformer_pipeline = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    truncation=True,      # Ensures text is truncated at 4096 tokens
    max_length=4096       # Set the maximum length for processing
)

# Step 4: Define Label Mapping
label_mapping = {
    "LABEL_0": "Negative",
    "LABEL_1": "Positive"
}

# Step 5: Initialize KeyBERT for Keyword Extraction
kw_model = KeyBERT(model="all-MiniLM-L6-v2")  # Lightweight BERT model for keyword extraction

def extract_keywords(article, bike_name, top_n=5):
    # Add bike name words to the stop words
    bike_name_words = set(bike_name.lower().split())
    custom_stop_words = ENGLISH_STOP_WORDS.union(bike_name_words)
    keywords = kw_model.extract_keywords(article, keyphrase_ngram_range=(1, 2), stop_words=custom_stop_words, top_n=top_n)
    # Dynamically adjust to ensure at least one keyword
    if not keywords:
        keywords = kw_model.extract_keywords(article, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=1)
    return ", ".join([kw[0] for kw in keywords])

# Step 6: Perform Sentiment Analysis and Keyword Extraction
results = []
for filename, title, bike_name, article in zip(filenames, titles, bike_names, articles):
    sentiment = longformer_pipeline(article)[0]
    human_readable_label = label_mapping.get(sentiment["label"], "Unknown")
    if human_readable_label != "Unknown":  # Ignore neutral sentiments
        keywords = extract_keywords(article, bike_name)  # Extract top keywords or phrases
        results.append({
            "filename": filename,
            "title": title,  # Include title in the results
            "bike_name": bike_name,
            "sentiment": human_readable_label,
            "confidence_score": sentiment["score"],
            "keywords": keywords
        })

# Step 7: Save Results to DataFrame
df = pd.DataFrame(results)

# Optional: Save results to a CSV file
output_file = "longformer_sentiment_with_keywords_titles_and_bike_names.csv"
df.to_csv(output_file, index=False)

# Display results
print(df)
