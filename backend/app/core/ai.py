import google.generativeai as genai
from app.core.config import settings
from qdrant_client import QdrantClient
from app.knowledge_base_loader import text_to_embedding, COLLECTION_NAME

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

def get_knowledge_context(domain: str, query: str) -> str:
    try:
        embedding = text_to_embedding(query)
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            query_filter={"must": [{"key": "domain", "match": {"value": domain}}]},
            limit=3
        ).points
        if not results:
            return ""
        return "\n\n".join([r.payload["text"] for r in results])
    except Exception as e:
        print(f"Qdrant search error: {e}")
        return ""

def generate_requirements(domain: str, role: str, answers: list, document_text: str = "", knowledge_context: str = "") -> dict:
    if not knowledge_context:
        query = f"{domain} system requirements {' '.join([a.get('answer', '') for a in answers])}"
        knowledge_context = get_knowledge_context(domain, query)

    answers_text = "\n".join([f"Q: {a.get('question', '')} A: {a.get('answer', '')}" for a in answers])

    prompt = f"""You are an expert requirements engineer specializing in the {domain} domain in Jordan.

Generate comprehensive software requirements based on:

## Project Context
- Domain: {domain}
- Target Role: {role}
- Country: Jordan

## Questionnaire Answers
{answers_text}

{"## Additional Document" if document_text else ""}
{document_text if document_text else ""}

{"## Domain Knowledge Base" if knowledge_context else ""}
{knowledge_context if knowledge_context else ""}

Generate requirements for a {role}:

### Functional Requirements
FR-1: [description]
FR-2: [description]

### Non-Functional Requirements
NFR-1: [description]
NFR-2: [description]"""

    response = model.generate_content(prompt)
    response_text = response.text

    functional = []
    non_functional = []
    current_section = None

    for line in response_text.split("\n"):
        line = line.strip()
        if "Functional Requirements" in line and "Non-" not in line:
            current_section = "functional"
        elif "Non-Functional Requirements" in line:
            current_section = "non_functional"
        elif line.startswith("FR-") and current_section == "functional":
            functional.append(line)
        elif line.startswith("NFR-") and current_section == "non_functional":
            non_functional.append(line)

    return {"functional": functional, "non_functional": non_functional, "raw": response_text}