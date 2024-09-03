# Step 1: Install necessary libraries
# !pip install spacy textblob

# Step 2: Download spaCy's English model
# !python -m spacy download en_core_web_sm

import spacy
from textblob import TextBlob

# Step 3: Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Step 4: Define a function to analyze the sentiment of a review
def analyze_review_emotion(review):
    # Process the review text with spaCy
    doc = nlp(review)
    
    # Use TextBlob for sentiment analysis
    blob = TextBlob(doc.text)
    sentiment = blob.sentiment
    
    # Determine the overall emotion
    if sentiment.polarity > 0:
        emotion = "Positive"
    elif sentiment.polarity < 0:
        emotion = "Negative"
    else:
        emotion = "Neutral"
    
    return emotion, sentiment

# Step 5: Example usage
review = "I absolutely loved the product! It exceeded my expectations."
emotion, sentiment = analyze_review_emotion(review)
print(f"Review: {review}")
print(f"Emotion: {emotion}")
print(f"Sentiment: {sentiment}")

review = "The product was terrible and didn't work as expected."
emotion, sentiment = analyze_review_emotion(review)
print(f"Review: {review}")
print(f"Emotion: {emotion}")
print(f"Sentiment: {sentiment}")

review = "The product is okay, neither good nor bad."
emotion, sentiment = analyze_review_emotion(review)
print(f"Review: {review}")
print(f"Emotion: {emotion}")
print(f"Sentiment: {sentiment}")

