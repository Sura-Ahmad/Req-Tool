import anthropic
from app.core.config import settings
from qdrant_client import QdrantClient
from app.knowledge_base_loader import text_to_embedding, COLLECTION_NAME

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
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
            print(f"⚠️ No knowledge base results for domain: {domain}")
            return ""
        print(f"✅ Found {len(results)} chunks for domain: {domain}")
        return "\n\n".join([r.payload["text"] for r in results])
    except Exception as e:
        print(f"Qdrant search error: {e}")
        return ""

def generate_requirements(domain: str, role: str, answers: list, document_text: str = "", knowledge_context: str = "") -> dict:
    if not knowledge_context:
        query = f"{domain} system requirements {' '.join([a.get('answer', '') for a in answers])}"
        knowledge_context = get_knowledge_context(domain, query)

    answers_text = "\n".join([f"Q: {a.get('question', '')} A: {a.get('answer', '')}" for a in answers])

    role_instructions = {
    "product_owner": "Write requirements as high-level business outcomes and user stories. Focus on WHAT the system should do, not HOW. Use business language.",
    "business_analyst": "Write requirements as detailed functional specifications. Be precise and measurable. Include acceptance criteria hints.",
    "developer": "Write requirements as technical specifications. Include implementation details, APIs, data structures, and performance metrics.",
    "stakeholder": "Write requirements as business goals and benefits. Focus on value delivered, ROI, and business impact. Use non-technical language."
}

    role_instruction = role_instructions.get(role, "Write clear and detailed requirements.")

    # Validate system type matches domain
    validation_prompt = f"""Does "{' '.join([a.get('answer', '') for a in answers])}" relate to the {domain} domain?
    Answer with only YES or NO."""
    
    validation = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=10,
        messages=[{"role": "user", "content": validation_prompt}]
    )
    
    if "NO" in validation.content[0].text.upper():
        return {
            "functional": [],
            "non_functional": [],
            "raw": "",
            "error": f"The system you described doesn't match the {domain} domain. Please choose a system related to {domain}."
        }

    prompt = f"""You are an expert requirements engineer specializing in the {domain} domain in Jordan.

Generate comprehensive software requirements tailored specifically for a {role.replace('_', ' ').title()}.

## Role-Specific Instructions
{role_instruction}

## Project Context
- Domain: {domain}
- Target Role: {role.replace('_', ' ').title()}
- Country: Jordan

## Questionnaire Answers
{answers_text}

{"## Additional Document Content" if document_text else ""}
{document_text if document_text else ""}

{"## Jordan Domain Knowledge Base" if knowledge_context else ""}
{knowledge_context if knowledge_context else ""}

## Output Format
Generate exactly in this format:

### Functional Requirements
FR-1: [requirement tailored for {role.replace('_', ' ')}]
FR-2: [requirement tailored for {role.replace('_', ' ')}]

### Non-Functional Requirements
NFR-1: [requirement tailored for {role.replace('_', ' ')}]
NFR-2: [requirement tailored for {role.replace('_', ' ')}]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text
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