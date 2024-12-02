import re
import nltk
import yake
import spacy
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from itertools import combinations
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from rake_nltk import Rake
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Initialize spaCy model
nlp = spacy.load('en_core_web_sm')

# Initialize KeyBERT model
kw_model = KeyBERT(model=SentenceTransformer('all-MiniLM-L6-v2'))

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\W', ' ', text)
    return text

# 1. TF-IDF
def extract_keywords_tfidf(text, top_n=10):
    preprocessed_text = preprocess_text(text)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([preprocessed_text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()
    top_indices = tfidf_scores.argsort()[-top_n:][::-1]
    keywords = [feature_names[i] for i in top_indices]
    return keywords

# 2. RAKE
def extract_keywords_rake(text, top_n=10):
    r = Rake()
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()[:top_n]
    return keywords

# 3. YAKE
def extract_keywords_yake(text, top_n=10):
    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords[:top_n]]

# 4. TextRank
def extract_keywords_textrank(text, top_n=10):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    token_pairs = list(combinations(tokens, 2))
    graph = nx.Graph()
    graph.add_edges_from(token_pairs)
    scores = nx.pagerank(graph)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    keywords = [item[0] for item in sorted_scores[:top_n]]
    return keywords

# 5. LDA
def extract_keywords_lda(text, top_n=10, n_topics=1):
    preprocessed_text = preprocess_text(text)
    vectorizer = CountVectorizer(stop_words='english')
    doc_term_matrix = vectorizer.fit_transform([preprocessed_text])
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(doc_term_matrix)
    feature_names = vectorizer.get_feature_names_out()
    keywords = []
    for topic_idx, topic in enumerate(lda.components_):
        top_features_indices = topic.argsort()[:-top_n - 1:-1]
        keywords.extend([feature_names[i] for i in top_features_indices])
    return keywords[:top_n]

# 6. KeyBERT
def extract_keywords_keybert(text, top_n=10):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
    return [kw[0] for kw in keywords]

# Example usage
if __name__ == "__main__":
    sample_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals.
    Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.
    Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem-solving".
    """

    print("TF-IDF Keywords:", extract_keywords_tfidf(sample_text))
    print("RAKE Keywords:", extract_keywords_rake(sample_text))
    print("YAKE Keywords:", extract_keywords_yake(sample_text))
    print("TextRank Keywords:", extract_keywords_textrank(sample_text))
    print("LDA Keywords:", extract_keywords_lda(sample_text))
    print("KeyBERT Keywords:", extract_keywords_keybert(sample_text))
