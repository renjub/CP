from transformers import pipeline, AutoTokenizer
import pandas as pd
import os

# Initialize fine-tuned sentiment pipeline and tokenizer globally
fine_tuned_model_path = os.path.expanduser("~/TrainedModelFinal")  # Expand tilde to absolute path

bert_sentiment_analyzer = pipeline(
    "sentiment-analysis", 
    model=fine_tuned_model_path
)
bert_tokenizer = AutoTokenizer.from_pretrained(fine_tuned_model_path)

# Function for BERT sentiment analysis
def bert_sentiment(text):
    result = bert_sentiment_analyzer(text)[0]
    label = result['label']
    score = result['score']

    # Convert LABEL_0 to negative and LABEL_1 to positive
    if label == "LABEL_0":
        sentiment = "negative"
    elif label == "LABEL_1":
        sentiment = "positive"
    else:
        sentiment = "neutral"  # Handle unexpected labels
    return sentiment, score

# Function to split text based on token limit
def split_text_by_tokens(text, tokenizer, max_length=512):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
    return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

# Function for combined sentiment analysis on longer texts
def combined_bert_sentiment(text):
    chunks = split_text_by_tokens(text, bert_tokenizer, max_length=500)  # Split text into 500-token chunks
    sentiments = []
    scores = []

    for chunk in chunks:
        sentiment, score = bert_sentiment(chunk)
        sentiments.append(sentiment)
        scores.append(score)

    # Combine sentiments and scores
    positive_count = sentiments.count("positive")
    negative_count = sentiments.count("negative")
    neutral_count = sentiments.count("neutral")

    if positive_count > negative_count and positive_count > neutral_count:
        overall_sentiment = "positive"
    elif negative_count > positive_count and negative_count > neutral_count:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    overall_score = sum(scores) / len(scores) if scores else 0.0
    return overall_sentiment, overall_score

# Function to process all CSV files in subdirectories within the Reviews folder
def process_all_csv_files_in_subdirectories(directory):
    for root, dirs, files in os.walk(directory):
        # Skip the current directory (CWD)
        if root == directory:
            continue
        # Check if the current directory is within the Reviews folder
        if 'Reviews' in os.path.relpath(root, directory).split(os.sep):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file_path}")
                    process_csv_file(file_path)

# Function to process a single CSV file
def process_csv_file(input_csv):
    df = pd.read_csv(input_csv)

    # Check if 'Sentiment' column already exists
    # if 'Sentiment' in df.columns:
    #     print(f"Skipping file: {input_csv} (Sentiment column already exists)")
    #     return

    # Assuming the review text is in columns named 'Title' and 'Review'
    df['Title'] = df['Title'].astype(str).fillna('')  # Ensure all values are strings and handle missing values
    df['Review'] = df['Review'].astype(str).fillna('')

    sentiments = []
    scores = []
    for title, review in zip(df['Title'], df['Review']):
        combined_text = f"{title} {review}".strip()  # Combine title and review text
        if combined_text:  # Ensure combined text is non-empty
            sentiment, score = combined_bert_sentiment(combined_text)
        else:
            sentiment, score = "neutral", 0.0  # Handle empty or invalid combined text
        sentiments.append(sentiment)
        scores.append(score)

    # Adding the sentiment and value columns to the DataFrame
    df['Sentiment'] = sentiments
    df['Value'] = scores

    # Saving the updated DataFrame to the same CSV file
    df.to_csv(input_csv, index=False)

    # Displaying the updated DataFrame as a table
    print(df)

# Process all CSV files in subdirectories only
cwd = os.getcwd()  # Get current working directory
process_all_csv_files_in_subdirectories(cwd)