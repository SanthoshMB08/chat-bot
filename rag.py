from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()

def get_relevant_context(history, user_input, k=3):
    if not history:
        return []

    texts = [msg for msg in history]
    vectors = vectorizer.fit_transform(texts + [user_input])

    sims = cosine_similarity(vectors[-1], vectors[:-1])[0]
    top_indices = sims.argsort()[-k:][::-1]

    return [texts[i] for i in top_indices]
