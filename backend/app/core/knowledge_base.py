import os
import json
import uuid
import logging
import pdfplumber
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
from app.core.config import settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("requirements_ai")

COLLECTION_NAME = "knowledge_base"
CHUNK_SIZE = 500
VECTOR_SIZE = 384
MANIFEST_FILENAME = "manifest.json"

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


# ── helpers ────────────────────────────────────────────────────────────────────

def _kb_path() -> str:
    return settings.KNOWLEDGE_BASE_PATH

def _manifest_path() -> str:
    return os.path.join(_kb_path(), MANIFEST_FILENAME)

def _read_manifest() -> dict:
    path = _manifest_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_manifest(manifest: dict):
    os.makedirs(_kb_path(), exist_ok=True)
    with open(_manifest_path(), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def _entry_id(domain: str, country: str) -> str:
    """Stable ID from domain + country — uploading the same domain again overwrites it."""
    return f"{domain.strip().lower().replace(' ', '_')}_{country.strip().upper()}"


# ── core functions ──────────────────────────────────────────────────────────────

def text_to_embedding(text: str) -> list:
    return _get_model().encode(text).tolist()


def retrieve_context(domain: str, query: str, limit: int = 5) -> str:
    """Embed query, search Qdrant filtered by domain, return joined text chunks."""
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


def ensure_collection():
    client = _get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    for field in ("domain", "country"):
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_pdf(file_path: str, domain: str, country: str = "JO") -> int:
    """Load a single PDF into Qdrant. Returns the number of chunks stored."""
    print(f"Loading '{file_path}' → domain='{domain}', country='{country}' ...")
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if not text.strip():
        print(f"No text found in {file_path}")
        return 0

    # Remove existing vectors for this domain/country before re-loading
    _delete_from_qdrant(domain, country)

    chunks = chunk_text(text)
    print(f"  {len(chunks)} chunks to index ...")

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
        print(f"  Done — {len(points)} vectors stored.")

    return len(points)


def _delete_from_qdrant(domain: str, country: str):
    """Remove all Qdrant points for a given domain + country."""
    _get_qdrant_client().delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(key="domain", match=MatchValue(value=domain)),
                FieldCondition(key="country", match=MatchValue(value=country)),
            ]
        ),
    )


# ── public API ─────────────────────────────────────────────────────────────────

def register_and_load(file_path: str, domain: str, country: str, original_name: str) -> dict:
    """
    Save metadata to the manifest and load the PDF into Qdrant.
    Called by the admin upload endpoint after saving the file to disk.
    Returns the manifest entry.
    """
    ensure_collection()
    chunks = load_pdf(file_path, domain=domain, country=country)

    entry_id = _entry_id(domain, country)
    manifest = _read_manifest()
    entry = {
        "id": entry_id,
        "filename": os.path.basename(file_path),
        "domain": domain,
        "country": country.upper(),
        "original_name": original_name,
        "uploaded_at": datetime.utcnow().isoformat(),
        "chunks": chunks,
    }
    manifest[entry_id] = entry
    _write_manifest(manifest)
    return entry


def list_kb_files() -> list:
    """Return all entries from the manifest, newest first."""
    manifest = _read_manifest()
    return sorted(manifest.values(), key=lambda e: e.get("uploaded_at", ""), reverse=True)


def delete_kb_file(entry_id: str) -> bool:
    """
    Delete a KB entry: remove from Qdrant, delete the file, update the manifest.
    Returns True if the entry existed.
    """
    manifest = _read_manifest()
    entry = manifest.get(entry_id)
    if not entry:
        return False

    # Remove vectors from Qdrant
    _delete_from_qdrant(entry["domain"], entry["country"])

    # Delete the PDF file
    file_path = os.path.join(_kb_path(), entry["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    del manifest[entry_id]
    _write_manifest(manifest)
    return True


def load_all():
    """
    Load all PDFs registered in the manifest into Qdrant.
    On first run (no manifest yet) it auto-discovers legacy files using the
    old naming convention  {country_name}_{domain}.pdf  (e.g. jordan_health.pdf).
    """
    ensure_collection()
    os.makedirs(_kb_path(), exist_ok=True)
    manifest = _read_manifest()

    # ── legacy auto-discovery (runs once if manifest is empty) ──────────────
    if not manifest:
        print("No manifest found — scanning for legacy PDF files ...")
        legacy_country_map = {"jordan": "JO", "saudi": "SA", "egypt": "EG", "uae": "AE"}
        for filename in os.listdir(_kb_path()):
            if not filename.endswith(".pdf"):
                continue
            base = filename.replace(".pdf", "").lower()
            parts = base.split("_", 1)
            if len(parts) == 2 and parts[0] in legacy_country_map:
                country = legacy_country_map[parts[0]]
                domain = parts[1].replace("_", " ").title()
            else:
                domain = base.replace("_", " ").title()
                country = "JO"

            file_path = os.path.join(_kb_path(), filename)
            chunks = load_pdf(file_path, domain=domain, country=country)
            entry_id = _entry_id(domain, country)
            manifest[entry_id] = {
                "id": entry_id,
                "filename": filename,
                "domain": domain,
                "country": country,
                "original_name": filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "chunks": chunks,
            }
        _write_manifest(manifest)
        return

    # ── normal run: load every file listed in the manifest ──────────────────
    for entry in manifest.values():
        file_path = os.path.join(_kb_path(), entry["filename"])
        if os.path.exists(file_path):
            load_pdf(file_path, domain=entry["domain"], country=entry["country"])
        else:
            print(f"Warning: file '{entry['filename']}' listed in manifest but not found on disk.")


if __name__ == "__main__":
    load_all()
