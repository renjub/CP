from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import linkage, dendrogram
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from transformers import pipeline


# Topic Modeling with LDA
def lda_topic_modeling(reviews, num_topics=5):
    tokenized_reviews = [review.split() for review in reviews]
    dictionary = Dictionary(tokenized_reviews)
    corpus = [dictionary.doc2bow(text) for text in tokenized_reviews]
    lda = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)
    return lda.print_topics()


# Topic Modeling with NMF
def nmf_topic_modeling(reviews, num_topics=5):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(reviews)
    nmf_model = NMF(n_components=num_topics, random_state=42)
    W = nmf_model.fit_transform(tfidf_matrix)
    H = nmf_model.components_
    return nmf_model, tfidf.get_feature_names_out()


# Text Classification (Naive Bayes, SVM, Logistic Regression)
def classify_reviews(reviews, labels, algorithm="naive_bayes"):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(reviews)
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

    if algorithm == "naive_bayes":
        model = MultinomialNB()
    elif algorithm == "svm":
        model = LinearSVC()
    elif algorithm == "logistic_regression":
        model = LogisticRegression(max_iter=1000)
    else:
        raise ValueError("Unsupported algorithm: choose 'naive_bayes', 'svm', or 'logistic_regression'")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    return model, vectorizer


# K-Means Clustering
def kmeans_clustering(reviews, num_clusters=5):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(reviews)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    return kmeans, vectorizer


# Hierarchical Clustering
def hierarchical_clustering(reviews):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(reviews).toarray()
    linkage_matrix = linkage(X, method='ward')
    dendrogram(linkage_matrix)


# Deep Learning with Transformers for Topic Extraction
def transformer_topic_extraction(reviews, model_name="bert-base-uncased"):
    nlp = pipeline("zero-shot-classification", model=model_name)
    topics = []
    for review in reviews:
        topics.append(nlp(review, candidate_labels=["quality", "service", "price", "ambiance", "product"]))
    return topics


# LSTM for Text Classification
def lstm_text_classification(reviews, labels, vocab_size=5000, max_length=100):
    tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(reviews)
    sequences = tokenizer.texts_to_sequences(reviews)
    padded_sequences = pad_sequences(sequences, maxlen=max_length)

    model = Sequential([
        Embedding(vocab_size, 128, input_length=max_length),
        LSTM(64, return_sequences=False),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()
    return model, tokenizer


# Aspect-Based Sentiment Analysis (ABSA) with Transformers
def aspect_based_sentiment_analysis(reviews, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
    nlp = pipeline("sentiment-analysis", model=model_name)
    results = []
    for review in reviews:
        results.append(nlp(review))
    return results


# Example usage
if __name__ == "__main__":
    # Example data
    sample_reviews = [
        "The product quality is amazing and delivery was fast.",
        "Customer service was terrible, and the product broke after a week.",
        "Great value for the price, I love the features.",
        "The ambiance of the store was pleasant, and the staff was helpful.",
        "Delivery took too long, but the product itself is fine."
    ]

    sample_labels = [1, 0, 1, 1, 0]  # Example binary labels for classification

    # Example: LDA Topic Modeling
    print("LDA Topics:")
    print(lda_topic_modeling(sample_reviews))

    # Example: NMF Topic Modeling
    print("\nNMF Topics:")
    nmf_model, features = nmf_topic_modeling(sample_reviews)
    print(features)

    # Example: Classification
    print("\nClassification Report (Naive Bayes):")
    classify_reviews(sample_reviews, sample_labels, algorithm="naive_bayes")

    # Example: K-Means Clustering
    print("\nK-Means Clustering:")
    kmeans, vectorizer = kmeans_clustering(sample_reviews)
    print(kmeans.labels_)

    # Example: Aspect-Based Sentiment Analysis
    print("\nAspect-Based Sentiment Analysis:")
    absa_results = aspect_based_sentiment_analysis(sample_reviews)
    print(absa_results)
