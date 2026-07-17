# backend/data/vectordb.py
"""
Vector DB — uses the full CRM knowledge base (crm_knowledge.json) 
instead of the old 12-entry synthetic list.
"""
import json
import os
# pyrefly: ignore [missing-import]
import chromadb
import numpy as np

class MockSentenceTransformer:
    def __init__(self, name=None):
        pass
    def encode(self, text: str):
        # Generate deterministic mock unit embedding based on text hash
        val = sum(ord(c) for c in text)
        np.random.seed(val % 10000)
        vector = np.random.uniform(-1, 1, 384)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

JSON_PATH = os.path.join(os.path.dirname(__file__), "crm_knowledge.json")

# 1. Load the embedding model (mocked to run with 0MB RAM)
model = MockSentenceTransformer('all-MiniLM-L6-v2')

# 2. Create an in-memory Chroma DB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="crm_knowledge",
    metadata={"hnsw:space": "cosine"}
)

# 3. Load the knowledge base
if os.path.exists(JSON_PATH):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE = json.load(f)
else:
    # Fallback to old synthetic data if JSON not generated yet
    KNOWLEDGE = [
        {"type": "decision", "id": i+1, "text": d} for i, d in enumerate([
            "Decision: Expanded to second location in 2024. Outcome: Failed. Reason: Logistics capacity insufficient.",
            "Decision: Hired 10 sales reps in Q1 2025. Outcome: Success. Reason: Revenue increased by 18%.",
            "Decision: Cut prices by 10%. Outcome: Mixed. Reason: Volume up, margins down.",
            "Decision: Invested in warehouse automation. Outcome: Success. Reason: 15% overhead reduction.",
            "Decision: Outsourced logistics. Outcome: Failed. Reason: SLA breaches, complaints up 40%.",
            "Decision: Launched premium product line. Outcome: Success. Reason: High margins, brand differentiation.",
        ])
    ]
    print("⚠️  crm_knowledge.json not found. Run: python data/seed_db.py")

# 4. Add all knowledge entries to Chroma
for entry in KNOWLEDGE:
    uid = f"{entry['type']}_{entry['id']}"
    embedding = model.encode(entry["text"]).tolist()
    collection.upsert(
        ids=[uid],
        embeddings=[embedding],
        metadatas=[{"text": entry["text"], "type": entry["type"]}]
    )

print(f"[OK] Vector DB loaded with {len(KNOWLEDGE)} CRM knowledge entries.")

# 4.2 Load and index uploaded documents on startup
UPLOADED_JSON_PATH = os.path.join(os.path.dirname(__file__), "uploaded_docs.json")
if os.path.exists(UPLOADED_JSON_PATH):
    try:
        with open(UPLOADED_JSON_PATH, "r", encoding="utf-8") as f:
            uploaded_docs = json.load(f)
            uploaded_chunk_count = 0
            for doc in uploaded_docs:
                for chunk in doc.get("chunks", []):
                    uid = f"{doc['id']}_{chunk['index']}"
                    embedding = model.encode(chunk["text"]).tolist()
                    collection.upsert(
                        ids=[uid],
                        embeddings=[embedding],
                        metadatas=[{"text": chunk["text"], "type": "uploaded_document", "filename": doc["filename"]}]
                    )
                    uploaded_chunk_count += 1
            print(f"[OK] Vector DB loaded {uploaded_chunk_count} chunks from {len(uploaded_docs)} uploaded documents.")
    except Exception as e:
        print(f"⚠️ Error loading uploaded_docs.json on startup: {e}")


def add_document_to_vector_db(text: str, filename: str, doc_id: str) -> list:
    """
    Chunks text, encodes each chunk, and inserts it into Chroma.
    Returns: list of string chunks.
    """
    chunks = []
    chunk_size = 1000
    overlap = 200
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += chunk_size - overlap

    for i, chunk in enumerate(chunks):
        uid = f"{doc_id}_{i}"
        embedding = model.encode(chunk).tolist()
        collection.upsert(
            ids=[uid],
            embeddings=[embedding],
            metadatas=[{"text": chunk, "type": "uploaded_document", "filename": filename}]
        )
    return chunks


def add_chunks_to_vector_db_incremental(chunks: list, filename: str, doc_id: str, start_index: int = 0):
    """
    Helper function to insert a pre-chunked list of texts incrementally to save RAM.
    """
    for i, chunk in enumerate(chunks):
        uid = f"{doc_id}_{start_index + i}"
        embedding = model.encode(chunk).tolist()
        collection.upsert(
            ids=[uid],
            embeddings=[embedding],
            metadatas=[{"text": chunk, "type": "uploaded_document", "filename": filename}]
        )


def remove_document_from_vector_db(doc_id: str, chunks_count: int):
    """
    Deletes document chunks from Chroma.
    """
    ids = [f"{doc_id}_{i}" for i in range(chunks_count)]
    try:
        collection.delete(ids=ids)
    except Exception as e:
        print(f"⚠️ Error removing document {doc_id} from vector store: {e}")



def retrieve_memory(query_text: str, top_k: int = 3) -> tuple:
    """
    Queries the vector DB and returns the best matching CRM knowledge entries
    along with the average cosine similarity score.
    Returns: (combined_text, avg_similarity_score)
    """
    query_embedding = model.encode(query_text).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "distances"]
    )

    if results["metadatas"] and len(results["metadatas"][0]) > 0:
        texts = []
        scores = []
        for i, meta in enumerate(results["metadatas"][0]):
            distance = results["distances"][0][i]
            similarity = round(1 - distance, 4)
            scores.append(similarity)
            texts.append(meta["text"])

        combined_text = " | ".join(texts)
        avg_score = round(sum(scores) / len(scores), 4)
        return combined_text, avg_score

    return "No relevant past memory found.", 0.0