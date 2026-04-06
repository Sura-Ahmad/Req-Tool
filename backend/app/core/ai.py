import anthropic
from app.core.config import settings
from app.knowledge_base_loader import text_to_embedding, COLLECTION_NAME
from qdrant_client import QdrantClient

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

def get_knowledge_context(domain: str, query: str) -> str:
    try:
        embedding = text_to_embedding(query)
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            query_filter={
                "must": [{"key": "domain", "match": {"value": domain}}]
            },
            limit=3
        )
        if not results:
            return ""
        context = "\n\n".join([r.payload["text"] for r in results])
        return context
    except Exception as e:
        print(f"Qdrant search error: {e}")
        return ""

def generate_requirements(
    domain: str,
    role: str,
    answers: list,
    document_text: str = "",
    knowledge_context: str = ""
) -> dict:

    if not knowledge_context:
        query = f"{domain} system requirements {' '.join([a.get('answer', '') for a in answers])}"
        knowledge_context = get_knowledge_context(domain, query)

    answers_text = "\n".join([f"Q: {a.get('question', '')} A: {a.get('answer', '')}" for a in answers])

    prompt = f"""You are an expert requirements engineer specializing in the {domain} domain in Jordan.

Your task is to generate comprehensive software requirements based on the following information:

## Project Context
- Domain: {domain}
- Target Role: {role}
- Country: Jordan

## Questionnaire Answers
{answers_text}

{"## Additional Document Content" if document_text else ""}
{document_text if document_text else ""}

{"## Domain Knowledge Base (Jordan-specific regulations and standards)" if knowledge_context else ""}
{knowledge_context if knowledge_context else ""}

## Instructions
Generate requirements tailored for a {role}. Format them as follows:

### Functional Requirements
FR-1: [Requirement description]
FR-2: [Requirement description]

### Non-Functional Requirements
NFR-1: [Requirement description]
NFR-2: [Requirement description]

Make sure requirements are:
- Clear and unambiguous
- Specific to the {domain} domain in Jordan
- Appropriate for the {role} role
- Based on Jordanian regulations and standards where applicable
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    functional = []
    non_functional = []

    lines = response_text.split("\n")
    current_section = None

    for line in lines:
        line = line.strip()
        if "Functional Requirements" in line and "Non-" not in line:
            current_section = "functional"
        elif "Non-Functional Requirements" in line:
            current_section = "non_functional"
        elif line.startswith("FR-") and current_section == "functional":
            functional.append(line)
        elif line.startswith("NFR-") and current_section == "non_functional":
            non_functional.append(line)

    return {
        "functional": functional,
        "non_functional": non_functional,
        "raw": response_text
    }