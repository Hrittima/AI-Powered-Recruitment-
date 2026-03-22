import os
from pinecone import Pinecone
from sklearn.feature_extraction.text import TfidfVectorizer

# ================= PINECONE INIT =================
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("resume-index")

# ================= TF-IDF VECTORIZER =================
vectorizer = TfidfVectorizer()

# Store all texts for fitting (simple in-memory)
corpus = []

# ================= EMBEDDING =================
def get_embedding(text):
    corpus.append(text)

    vectors = vectorizer.fit_transform(corpus).toarray()
    return vectors[-1].tolist()


# ================= STORE RESUME =================
def store_resume(id, text):
    vector = get_embedding(text)

    index.upsert([
        (id, vector, {"text": text})
    ])


# ================= MATCH RESUME =================
def match_resume(text):
    if not corpus:
        return 0  # no baseline yet

    vector = get_embedding(text)

    result = index.query(
        vector=vector,
        top_k=1,
        include_metadata=True
    )

    if result["matches"]:
        return result["matches"][0]["score"]

    return 0