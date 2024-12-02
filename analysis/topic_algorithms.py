# Install necessary libraries
# Uncomment the below lines if running for the first time
# !pip install rake-nltk yake bertopic[visualization] sentence-transformers -q
# import nltk
# nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF, TruncatedSVD
from sklearn.cluster import KMeans
from rake_nltk import Rake
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
import yake


# Latent Dirichlet Allocation (LDA)
def extract_topics_lda(reviews, n_topics=1):
    stop_words = stopwords.words('english')
    vectorizer = CountVectorizer(stop_words=stop_words)
    X = vectorizer.fit_transform(reviews)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    words = vectorizer.get_feature_names_out()
    topics = []
    for idx, topic in enumerate(lda.components_):
        topic_words = [words[i] for i in topic.argsort()[:-11:-1]]
        topics.append('Topic {}: {}'.format(idx+1, ' '.join(topic_words)))
    return topics


# Non-negative Matrix Factorization (NMF)
def extract_topics_nmf(reviews, n_topics=1):
    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    X = vectorizer.fit_transform(reviews)
    nmf = NMF(n_components=n_topics, random_state=42)
    nmf.fit(X)
    words = vectorizer.get_feature_names_out()
    topics = []
    for idx, topic in enumerate(nmf.components_):
        topic_words = [words[i] for i in topic.argsort()[:-11:-1]]
        topics.append('Topic {}: {}'.format(idx+1, ' '.join(topic_words)))
    return topics


# Latent Semantic Analysis (LSA)
def extract_topics_lsa(reviews, n_topics=1):
    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    X = vectorizer.fit_transform(reviews)
    lsa = TruncatedSVD(n_components=n_topics, random_state=42)
    lsa.fit(X)
    words = vectorizer.get_feature_names_out()
    topics = []
    for idx, component in enumerate(lsa.components_):
        topic_words = [words[i] for i in component.argsort()[:-11:-1]]
        topics.append('Topic {}: {}'.format(idx+1, ' '.join(topic_words)))
    return topics


# Clustering on Word Embeddings
def extract_topics_embeddings(reviews, n_clusters=1):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(reviews)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(embeddings)
    labels = kmeans.labels_
    cluster_reviews = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
        cluster_reviews[label].append(reviews[idx])
    return cluster_reviews


# Keyword Extraction using RAKE
def extract_keywords_rake(review):
    r = Rake()
    r.extract_keywords_from_text(review)
    keywords = r.get_ranked_phrases()
    return keywords


from umap import UMAP
from bertopic import BERTopic

def extract_topics_bertopic(reviews):
    umap_model = UMAP(n_neighbors=5, n_components=2, metric='cosine')
    topic_model = BERTopic(umap_model=umap_model)
    
    # Fit the model
    topics, probabilities = topic_model.fit_transform(reviews)
    
    # Get topic info
    topic_info = topic_model.get_topic_info()
    return topic_info

## Topic Modeling using BERTopic
#def extract_topics_bertopic(reviews):
#    topic_model = BERTopic(verbose=False)
#    topics, probabilities = topic_model.fit_transform(reviews)
#    topic_info = topic_model.get_topic_info()
#    return topic_info


# Keyword Extraction using YAKE
def extract_keywords_yake(review):
    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(review)
    return [kw for kw, score in keywords]


# Example usage of all functions
if __name__ == "__main__":
    reviews = [
        "The product quality is excellent and the customer service was great.",
        "The battery life of this phone is outstanding and the camera is superb.",
        "The installation process was straightforward, and the interface is user-friendly."
    ]

    print("LDA Topics:", extract_topics_lda(reviews, n_topics=2))
    print("NMF Topics:", extract_topics_nmf(reviews, n_topics=2))
    print("LSA Topics:", extract_topics_lsa(reviews, n_topics=2))
    print("Embedding Clusters:", extract_topics_embeddings(reviews, n_clusters=2))
    print("RAKE Keywords:", extract_keywords_rake(reviews[0]))
    # print("BERTopic Topics:", extract_topics_bertopic(reviews))
    print("YAKE Keywords:", extract_keywords_yake(reviews[0]))