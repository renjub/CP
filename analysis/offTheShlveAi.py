# sentiment_analysis_tools.py

# Import necessary libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer as NLTKSentiment
from nltk.corpus import sentiwordnet as swn
from transformers import pipeline
from flair.models import TextClassifier
from flair.data import Sentence
import fasttext
import nltk
nltk.download('punkt')

# import allennlp
# For Aylien, you'll need to install the SDK and set up API keys

# Ensure NLTK data is downloaded
nltk.download('vader_lexicon')
nltk.download('sentiwordnet')
nltk.download('wordnet')

# Function for VADER
def vader_sentiment(review_text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(review_text)['compound']
    return score

# Function for TextBlob
def textblob_sentiment(review_text):
    blob = TextBlob(review_text)
    return blob.sentiment.polarity

# Function for NLTK VADER
def nltk_sentiment(review_text):
    analyzer = NLTKSentiment()
    score = analyzer.polarity_scores(review_text)['compound']
    return score

# Function for SentiWordNet (simple word-level scoring)
def sentiwordnet_sentiment(review_text):
    words = nltk.word_tokenize(review_text)
    scores = []
    for word in words:
        synsets = nltk.corpus.wordnet.synsets(word)
        if synsets:
            synset = synsets[0]
            swn_synset = swn.senti_synset(synset.name())
            scores.append(swn_synset.pos_score() - swn_synset.neg_score())
    return sum(scores) / len(scores) if scores else 0

# Function for Hugging Face Transformers (using DistilBERT for simplicity)
def transformers_sentiment(review_text):
    classifier = pipeline('sentiment-analysis')
    result = classifier(review_text)[0]
    return result['label'], result['score']

# Function for Aylien (replace with actual API call)
# def aylien_sentiment(review_text):
#     # Requires Aylien API setup
#     # Initialize API client and analyze sentiment
#     pass

# Function for FastText (using a sample pre-trained model)
def fasttext_sentiment(review_text):
    # Load a pre-trained sentiment analysis model if available
    # model = fasttext.load_model('path_to_pretrained_model.bin')
    # result = model.predict(review_text)
    # return result[0][0]
    return "Function placeholder for FastText"

# Function for Flair
def flair_sentiment(review_text):
    classifier = TextClassifier.load('sentiment')
    sentence = Sentence(review_text)
    classifier.predict(sentence)
    return sentence.labels[0].value, sentence.labels[0].score

# Function for AllenNLP (assumes model is available)
# def allennlp_sentiment(review_text):
#     # Configure an AllenNLP pipeline if possible
#     pass

# Sample test for each function
if __name__ == "__main__":
    review = "This is an amazing product. I love it!"
    
    print("VADER Sentiment:", vader_sentiment(review))
    print("TextBlob Sentiment:", textblob_sentiment(review))
    print("NLTK Sentiment:", nltk_sentiment(review))
    print("SentiWordNet Sentiment:", sentiwordnet_sentiment(review))
    print("Transformers Sentiment:", transformers_sentiment(review))
    # print("Aylien Sentiment:", aylien_sentiment(review))  # Requires API setup
    print("FastText Sentiment:", fasttext_sentiment(review))  # Placeholder
    print("Flair Sentiment:", flair_sentiment(review))
    # print("AllenNLP Sentiment:", allennlp_sentiment(review))  # Placeholder