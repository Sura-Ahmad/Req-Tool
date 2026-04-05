from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings
import uuid

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 1536

def ensure_collection():
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION_NAME}' created!")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

def add_document(text: str, metadata: dict, embedding: list):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={**metadata, "text": text}
            )
        ]
    )

def search_similar(embedding: list, domain: str, limit: int = 5):
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        query_filter={
            "must": [{"key": "domain", "match": {"value": domain}}]
        },
        limit=limit
    )
    return results