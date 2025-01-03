import os
import re
import pandas as pd
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# Function to extract headings, bold text, and associated content
def extract_content(text, ignore_words):
    pattern = r"(## Heading: .+?|\*\*(.+?)\*\*)"
    matches = list(re.finditer(pattern, text))
    extracted_data = []
    for i, match in enumerate(matches):
        heading_or_bold = match.group(0)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        content = '\n'.join([line for line in content.splitlines() if not line.startswith(tuple(["Processing additional page:", "Home » Bike News"]))])
        if not any(word in heading_or_bold for word in ignore_words):
            extracted_data.append([heading_or_bold, content])
    return extracted_data

# Sentiment analysis with the pre-trained BERT model
def bert_sentiment(text, bert_sentiment_analyzer):
    result = bert_sentiment_analyzer(text)[0]
    sentiment = "negative" if result['label'] == "LABEL_0" else "positive"
    return sentiment, result['score']

# Process all .txt files in the directory
def process_txt_files():
    ignore_words = ["Bike Tested", "Price OTR", "Further Reading", "Alternatives", "Road Test No", "Test Location", "Riders", "Picture Editing", "Specifications", "Dimensions"]
    current_folder = os.getcwd()
    txt_files = [f for f in os.listdir(current_folder) if f.endswith('.txt')]
    if not txt_files:
        print("No .txt files found in the current folder.")
        return
    output_folder = os.path.join(current_folder, 'output_files')
    os.makedirs(output_folder, exist_ok=True)

    # Load the sentiment analysis model
    trained_model_path = os.path.expanduser("~/TrainedModelFinal")
    bert_sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model=AutoModelForSequenceClassification.from_pretrained(trained_model_path),
        tokenizer=AutoTokenizer.from_pretrained(trained_model_path)
    )

    article_folder = os.path.join(current_folder, 'Articles')
    txt_files = [f for f in os.listdir(article_folder) if f.endswith('.txt')]
    if not txt_files:
        print("No .txt files found in the Article folder.")
        return

    for txt_file in txt_files:
        print(f"\nProcessing file: {txt_file}")
        with open(os.path.join(article_folder, txt_file), 'r', encoding='utf-8') as file:
            content = file.read()

        extracted_data = extract_content(content, ignore_words)
        sentiment_results = [bert_sentiment(item[1], bert_sentiment_analyzer) for item in extracted_data]

        # Combine extracted data with sentiment analysis results
        df = pd.DataFrame({
            "Heading/Bold Text": [re.sub(r"\*\*(.+?)\*\*", r"\1", item[0]) for item in extracted_data],
            "Content": [item[1] for item in extracted_data],
            "Sentiment": [result[0] for result in sentiment_results],
            "Confidence Score": [result[1] for result in sentiment_results]
        })

        print(df[["Heading/Bold Text", "Sentiment", "Confidence Score"]])  # Display the relevant columns

        # Save the DataFrame to a CSV file for each input file
        analysis_folder = os.path.join(article_folder, 'Analysis')
        os.makedirs(analysis_folder, exist_ok=True)
        output_file = os.path.join(analysis_folder, f"{os.path.splitext(txt_file)[0]}_extracted.csv")
        df.to_csv(output_file, index=False)

if __name__ == "__main__":
    process_txt_files()
