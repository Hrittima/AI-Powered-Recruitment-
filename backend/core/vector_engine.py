import pinecone
from sentence_transformers import SentenceTransformer
import os

# INIT MODEL
model = SentenceTransformer("all-MiniLM-L6-v2")

# INIT PINECONE
pinecone.init(
    api_key=os.getenv("pcsk_BWswk_M1gPcVpPEnbKccym9YYgizWTHaBf1vf7q6VDLR1rEu6xh36WoXU2ddQSed3hv5X"),
    environment="gcp-starter"
)

index = pinecone.Index("resume-index")


# =========================
# EMBEDDING FUNCTION
# =========================
def get_embedding(text):
    return model.encode(text).tolist()


# =========================
# STORE RESUME VECTOR
# =========================
def store_resume(id, text):
    vector = get_embedding(text)
    index.upsert([(id, vector)])


# =========================
# MATCH SCORE
# =========================
def match_resume(text):
    vector = get_embedding(text)

    result = index.query(vector=vector, top_k=1, include_values=False)

    if result["matches"]:
        return result["matches"][0]["score"]
    return 0