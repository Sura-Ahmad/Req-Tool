import logging
import anthropic
from app.core.config import settings
from qdrant_client import QdrantClient
from app.knowledge_base_loader import text_to_embedding, COLLECTION_NAME

logger = logging.getLogger("requirements_ai")

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

_ROLE_INSTRUCTIONS = {
    "product_owner": "Write requirements as high-level business outcomes and user stories. Focus on WHAT the system should do, not HOW. Use business language.",
    "business_analyst": "Write requirements as detailed functional specifications. Be precise and measurable. Include acceptance criteria hints.",
    "developer": "Write requirements as technical specifications. Include implementation details, APIs, data structures, and performance metrics.",
    "stakeholder": "Write requirements as business goals and benefits. Focus on value delivered, ROI, and business impact. Use non-technical language.",
}


def get_knowledge_context(domain: str, query: str) -> str:
    try:
        embedding = text_to_embedding(query)
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            query_filter={"must": [{"key": "domain", "match": {"value": domain}}]},
            limit=3,
        ).points
        if not results:
            logger.warning("No knowledge-base results for domain: %s", domain)
            return ""
        return "\n\n".join([r.payload["text"] for r in results])
    except Exception:
        logger.exception("Qdrant search error for domain: %s", domain)
        return ""


def generate_requirements(
    domain: str,
    role: str,
    answers: list,
    document_text: str = "",
    knowledge_context: str = "",
) -> dict:
    if not knowledge_context:
        query = f"{domain} system requirements {' '.join([a.get('answer', '') for a in answers])}"
        knowledge_context = get_knowledge_context(domain, query)

    answers_text = "\n".join(
        [f"Q: {a.get('question', '')} A: {a.get('answer', '')}" for a in answers]
    )
    role_instruction = _ROLE_INSTRUCTIONS.get(role, "Write clear and detailed requirements.")

    # ── validation (lightweight call, no caching needed) ──────────────────────
    validation_prompt = (
        f'Does "{" ".join([a.get("answer", "") for a in answers])}" '
        f"relate to the {domain} domain?\nAnswer with only YES or NO."
    )
    try:
        validation = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": validation_prompt}],
        )
        if "NO" in validation.content[0].text.upper():
            return {
                "functional": [],
                "non_functional": [],
                "raw": "",
                "error": (
                    f"The system you described doesn't match the {domain} domain. "
                    f"Please choose a system related to {domain}."
                ),
            }
    except Exception:
        logger.exception("Claude validation call failed")

    # ── static system prompt (cached) ─────────────────────────────────────────
    system_text = f"""You are an expert requirements engineer specializing in the {domain} domain in Jordan.

## Role-Specific Instructions
{role_instruction}

## Output Format
Generate exactly in this format:

### Functional Requirements
FR-1: [requirement]
FR-2: [requirement]

### Non-Functional Requirements
NFR-1: [requirement]
NFR-2: [requirement]"""

    # ── dynamic user prompt ───────────────────────────────────────────────────
    user_prompt_parts = [
        f"## Project Context\n- Domain: {domain}\n- Target Role: {role.replace('_', ' ').title()}\n- Country: Jordan",
        f"## Questionnaire Answers\n{answers_text}",
    ]
    if document_text:
        user_prompt_parts.append(f"## Additional Document Content\n{document_text}")
    if knowledge_context:
        user_prompt_parts.append(f"## Jordan Domain Knowledge Base\n{knowledge_context}")

    user_prompt = "\n\n".join(user_prompt_parts)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=[
                {
                    "type": "text",
                    "text": system_text,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
        )
    except Exception:
        logger.exception("Claude generation call failed")
        return {"functional": [], "non_functional": [], "raw": "", "error": "AI generation failed. Please try again."}

    response_text = message.content[0].text
    functional: list[str] = []
    non_functional: list[str] = []
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
