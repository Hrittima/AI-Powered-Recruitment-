import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# ================= LOAD MODEL =================
model = SentenceTransformer("all-MiniLM-L6-v2")

# ================= PINECONE INIT =================
pc = Pinecone(api_key=os.getenv("pcsk_BWswk_M1gPcVpPEnbKccym9YYgizWTHaBf1vf7q6VDLR1rEu6xh36WoXU2ddQSed3hv5X"))

index = pc.Index("resume-index")  # your index name


# ================= EMBEDDING =================
def get_embedding(text):
    return model.encode(text).tolist()


# ================= STORE RESUME =================
def store_resume(id, text):
    vector = get_embedding(text)

    index.upsert([
        (id, vector, {"text": text})
    ])


# ================= MATCH RESUME =================
def match_resume(text):
    vector = get_embedding(text)

    result = index.query(
        vector=vector,
        top_k=1,
        include_metadata=True
    )

    if result["matches"]:
        return result["matches"][0]["score"]

    return 0