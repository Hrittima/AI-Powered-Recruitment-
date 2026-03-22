import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Pinecone is optional: if the env var is missing, vector scoring is skipped ──
_pinecone_enabled = False
_index = None

try:
    from pinecone import Pinecone
    _api_key = os.getenv("PINECONE_API_KEY")
    if _api_key:
        pc = Pinecone(api_key=_api_key)
        _index = pc.Index("resume-index")
        _pinecone_enabled = True
        print("✅ Pinecone connected")
    else:
        print("⚠️  PINECONE_API_KEY not set — vector scoring disabled")
except Exception as e:
    print(f"⚠️  Pinecone init failed ({e}) — vector scoring disabled")


# ── Stable vectorizer: fitted once on a broad corpus ────────────────────────
# We keep a module-level vectorizer and update it incrementally via a
# simple in-memory document store so match_resume can always query.
_corpus = []
_vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
_corpus_matrix = None   # set after first fit


def _refit(texts):
    global _corpus_matrix, _vectorizer
    _vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
    _corpus_matrix = _vectorizer.fit_transform(texts)


def get_embedding(text: str) -> list:
    """Return a 512-d TF-IDF vector as a plain Python list."""
    global _corpus_matrix
    try:
        if not _corpus:
            # No corpus yet — fit on this single document
            _refit([text])
            return _corpus_matrix.toarray()[0].tolist()
        vec = _vectorizer.transform([text])
        return vec.toarray()[0].tolist()
    except Exception:
        return [0.0] * 512


def store_resume(doc_id: str, text: str):
    """Store resume vector in Pinecone (if available) and local corpus."""
    _corpus.append(text)
    _refit(_corpus)          # refit so future transforms are consistent

    if not _pinecone_enabled:
        return

    try:
        vector = get_embedding(text)
        _index.upsert([{
            "id": doc_id,
            "values": vector,
            "metadata": {"text": text[:1000]}
        }])
    except Exception as e:
        print(f"Pinecone upsert error: {e}")


def match_resume(text: str) -> float:
    """Return cosine similarity score 0-1 vs best stored resume."""
    if not _pinecone_enabled:
        return 0.0

    try:
        vector = get_embedding(text)
        result = _index.query(vector=vector, top_k=1, include_metadata=True)
        if result and result.get("matches"):
            return float(result["matches"][0]["score"])
    except Exception as e:
        print(f"Pinecone query error: {e}")

    return 0.0