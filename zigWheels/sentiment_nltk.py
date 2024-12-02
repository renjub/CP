import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

def categorize_review(review):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(review)
    
    if sentiment['compound'] >= 0.05:
        return 'Positive'
    elif sentiment['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# Example usage
review = "The product is okay, but I would not buy it again."
category = categorize_review(review)
print(f"The review is categorized as: {category}")

for review in div_reviews:
    print(categorize_review(review.get_text()))
