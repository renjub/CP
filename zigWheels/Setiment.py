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

# Function to process all CSV files in the reviews folder
def process_csv_files_in_reviews():
    folder_path = os.path.expanduser("reviews")  # Path to the reviews folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]

    for file in files:
        print(f"Processing file: {file}")
        process_csv_file(os.path.join(folder_path, file))

# Function to process a single CSV file
def process_csv_file(input_csv):
    df = pd.read_csv(input_csv)

    # Ensure the 'Review' column is a string and handle missing values
    df['Review'] = df['Review'].astype(str).fillna('')

    sentiments = []
    scores = []

    for review in df['Review']:
        if review:
            sentiment, score = combined_bert_sentiment(review)
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

# Start processing all CSV files in the reviews folder
process_csv_files_in_reviews()