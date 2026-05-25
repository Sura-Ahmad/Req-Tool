import logging
import uuid
import os
import pdfplumber
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
from app.core.config import settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("requirements_ai")

COLLECTION_NAME = "knowledge_base"
CHUNK_SIZE = 500
VECTOR_SIZE = 384

_qdrant_client = None
_model = None


def _get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    return _qdrant_client


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _kb_path() -> str:
    return settings.KNOWLEDGE_BASE_PATH


def text_to_embedding(text: str) -> list:
    return _get_model().encode(text).tolist()


def ensure_collection():
    client = _get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    for field in ("domain", "country"):
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception:
            pass


def retrieve_context(domain: str, query: str, limit: int = 5) -> str:
    try:
        embedding = text_to_embedding(query)
        results = _get_qdrant_client().query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            query_filter={"must": [{"key": "domain", "match": {"value": domain}}]},
            limit=limit,
        ).points
        return "\n\n".join([r.payload["text"] for r in results]) if results else ""
    except Exception:
        logger.exception("Qdrant search error for domain: %s", domain)
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size])
        for i in range(0, len(words), chunk_size)
        if " ".join(words[i : i + chunk_size]).strip()
    ]


def load_pdf(file_path: str, domain: str, country: str = "JO") -> int:
    """Extract text from a PDF, embed it, and upsert into Qdrant. Returns chunk count."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if not text.strip():
        return 0

    _delete_from_qdrant(domain, country)

    chunks = chunk_text(text)
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=text_to_embedding(chunk),
            payload={
                "text": chunk,
                "domain": domain,
                "country": country,
                "source": os.path.basename(file_path),
            },
        )
        for chunk in chunks
    ]

    if points:
        _get_qdrant_client().upsert(collection_name=COLLECTION_NAME, points=points)

    return len(points)


def _delete_from_qdrant(domain: str, country: str):
    _get_qdrant_client().delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(key="domain", match=MatchValue(value=domain)),
                FieldCondition(key="country", match=MatchValue(value=country)),
            ]
        ),
    )
