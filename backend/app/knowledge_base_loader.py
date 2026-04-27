import os
import pdfplumber
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from anthropic import Anthropic
from app.core.config import settings
import uuid
import hashlib

qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

COLLECTION_NAME = "knowledge_base"
CHUNK_SIZE = 500
VECTOR_SIZE = 384

def ensure_collection():
    collections = qdrant_client.get_collections().collections
    names = [c.name for c in collections]
    if COLLECTION_NAME not in names:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION_NAME}' created!")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
def text_to_embedding(text: str) -> list:
    return model.encode(text).tolist()

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_pdf(file_path: str, domain: str, country: str = "JO"):
    print(f"Loading {file_path}...")
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if not text.strip():
        print(f"No text found in {file_path}")
        return

    chunks = chunk_text(text)
    print(f"Found {len(chunks)} chunks")

    points = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        embedding = text_to_embedding(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "domain": domain,
                "country": country,
                "source": os.path.basename(file_path)
            }
        ))

    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✅ Added {len(points)} chunks to Qdrant!")

def load_all():    
    ensure_collection()
    kb_path = "knowledge_base"
    files = {
        "jordan_health.pdf": "Health",
        "jordan_education.pdf": "Education",
        "jordan_finance.pdf": "Finance",
    }
    for filename, domain in files.items():
        filepath = os.path.join(kb_path, filename)
        if os.path.exists(filepath):
            load_pdf(filepath, domain=domain, country="JO")
        else:
            print(f"Skipping {filename} — not found")

if __name__ == "__main__":
    load_all()