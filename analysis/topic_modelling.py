import pandas as pd
import spacy
import gensim
from gensim import corpora
import matplotlib.pyplot as plt

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Read the CSV file
file_name = 'reviews.csv'
df = pd.read_csv(file_name)

# Extract the 'Review' column and drop any NaN values
reviews = df['Review'].dropna().astype(str).tolist()  # Convert to string and drop NaN

# Preprocess reviews: Tokenization and removing stop words
def preprocess_reviews(reviews):
    processed_reviews = []
    for review in reviews:
        doc = nlp(review.lower())
        tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
        processed_reviews.append(tokens)
    return processed_reviews

processed_reviews = preprocess_reviews(reviews)

# Create a dictionary and corpus for LDA
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(text) for text in processed_reviews]

# Perform LDA
num_topics = 5
lda_model = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

# Print the topics
for idx, topic in lda_model.print_topics(num_topics=num_topics):
    print(f"Topic {idx}: {topic}")

# Visualize topic distribution for the first document
doc = corpus[0]  # Change the index to analyze a different document
topic_distribution = lda_model.get_document_topics(doc)

# Extract topic ids and their probabilities
topic_ids, probabilities = zip(*topic_distribution)

# Plot the distribution of topics for the document
plt.figure(figsize=(10, 5))
plt.bar(topic_ids, probabilities, color='skyblue')
plt.xlabel('Topics')
plt.ylabel('Probability')
plt.title('Topic Distribution for First Document')
plt.xticks(topic_ids)
plt.grid(axis='y')
plt.show()