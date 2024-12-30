import os
import pandas as pd
from transformers import pipeline, AutoTokenizer

# Expand the home directory path for the model
model_path = os.path.expanduser("~/TrainedModelFinal")

# Load the local BERT sentiment model and tokenizer
bert_sentiment_analyzer = pipeline(
    "sentiment-analysis", 
    model=model_path, 
    tokenizer=model_path
)
bert_tokenizer = AutoTokenizer.from_pretrained(model_path)

# Function for BERT sentiment analysis
def bert_sentiment(text):
    result = bert_sentiment_analyzer(text)[0]
    label = result['label']
    score = result['score']

    # Convert labels to sentiment: LABEL_0 -> negative, LABEL_1 -> positive
    if label == "LABEL_0":
        sentiment = "negative"
    elif label == "LABEL_1":
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return sentiment, score

# Function to split text based on token limit
def split_text_by_tokens(text, tokenizer, max_length=512):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
    return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

# Function for combined sentiment analysis on longer texts
def combined_bert_sentiment(text):
    chunks = split_text_by_tokens(text, bert_tokenizer, max_length=500)
    sentiments = []
    scores = []

    for chunk in chunks:
        sentiment, score = bert_sentiment(chunk)
        sentiments.append(sentiment)
        scores.append(score)

    # Combine sentiments and scores
    positive_count = sentiments.count("positive")
    negative_count = sentiments.count("negative")

    if positive_count > negative_count:
        overall_sentiment = "positive"
    elif negative_count > positive_count:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    overall_score = sum(scores) / len(scores) if scores else 0.0
    return overall_sentiment, overall_score

# Function to process all CSV files in the 'reviews' subdirectories
def process_csv_files_in_reviews():
    base_dir = "reviews"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                process_csv_file(file_path)

# Function to process a single CSV file
def process_csv_file(input_csv):
    df = pd.read_csv(input_csv)

    # Ensure text columns are strings and handle missing values
    df['Title'] = df['Title'].astype(str).fillna('')
    df['Review'] = df['Review'].astype(str).fillna('')

    sentiments = []
    scores = []

    for title, review in zip(df['Title'], df['Review']):
        combined_text = f"{title} {review}".strip()
        if combined_text:
            sentiment, score = combined_bert_sentiment(combined_text)
        else:
            sentiment, score = "neutral", 0.0
        sentiments.append(sentiment)
        scores.append(score)

    # Add sentiment and score columns
    df['Sentiment'] = sentiments
    df['Value'] = scores

    # Save the updated DataFrame to the same file
    df.to_csv(input_csv, index=False)
    print(f"Processed and updated: {input_csv}")
    print(df)

# Start processing all CSV files in the 'reviews' subdirectories
process_csv_files_in_reviews()
