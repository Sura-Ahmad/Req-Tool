import json
import logging
import anthropic
from fastapi import HTTPException
from app.core.config import settings
from app.core.knowledge_base import retrieve_context

logger = logging.getLogger("requirements_ai")

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


_ROLE_INSTRUCTIONS = {
    "product_owner": "Write requirements as high-level business outcomes and user stories. Focus on WHAT the system should do, not HOW. Use business language.",
    "business_analyst": "Write requirements as detailed functional specifications. Be precise and measurable. Include acceptance criteria hints.",
    "developer": "Write requirements as technical specifications. Include implementation details, APIs, data structures, and performance metrics.",
    "stakeholder": "Write requirements as business goals and benefits. Focus on value delivered, ROI, and business impact. Use non-technical language.",
}


def generate_requirements(
    domain: str,
    role: str,
    answers: list,
    document_text: str = "",
    knowledge_context: str = "",
    country: str = "Jordan",
) -> dict:
    if not knowledge_context:
        query = f"{domain} system requirements {' '.join([a.get('answer', '') for a in answers])}"
        knowledge_context = retrieve_context(domain, query, limit=3)

    answers_text = "\n".join(
        [f"Q: {a.get('question', '')} A: {a.get('answer', '')}" for a in answers]
    )
    role_instruction = _ROLE_INSTRUCTIONS.get(role, "Write clear and detailed requirements.")

    validation_prompt = (
        f'Does "{" ".join([a.get("answer", "") for a in answers])}" '
        f"relate to the {domain} domain?\nAnswer with only YES or NO."
    )
    try:
        validation = _get_client().messages.create(
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

    system_text = f"""You are an expert requirements engineer specializing in the {domain} domain in {country}.

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

    user_prompt_parts = [
        f"## Project Context\n- Domain: {domain}\n- Target Role: {role.replace('_', ' ').title()}\n- Country: {country}",
        f"## Questionnaire Answers\n{answers_text}",
    ]
    if document_text:
        user_prompt_parts.append(f"## Additional Document Content\n{document_text}")
    if knowledge_context:
        user_prompt_parts.append(f"## {country} Domain Knowledge Base\n{knowledge_context}")

    user_prompt = "\n\n".join(user_prompt_parts)

    try:
        message = _get_client().messages.create(
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


def parse_json_response(text: str) -> list:
    """Parse a JSON array from a Claude response, stripping markdown code fences."""
    clean = text.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        logger.warning("Could not parse JSON response: %s", text[:200])
        return []


def generate_use_cases(domain_name: str, country: str, requirements: list) -> list:
    """Build a use-case prompt, call Claude, return a list of use-case dicts."""
    fr_text = "\n".join([f"{r.code}: {r.description}" for r in requirements])
    prompt = f"""Based on these functional requirements for a {domain_name} system in {country}, generate use cases as structured text.

Functional Requirements:
{fr_text}

Generate use cases and return them as a JSON array. Each use case must have:
- title: short title
- actor: who performs this action
- preconditions: what must be true before
- main_flow: step by step flow as text
- postconditions: what happens after

Return ONLY a valid JSON array, no other text. Example:
[{{"title": "User Login", "actor": "Registered User", "preconditions": "User has an account", "main_flow": "1. User opens login page\\n2. User enters credentials\\n3. System validates\\n4. User is logged in", "postconditions": "User is authenticated"}}]"""

    try:
        message = _get_client().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        logger.exception("Claude use-cases call failed")
        raise HTTPException(status_code=503, detail="AI service unavailable. Please try again.")
    return parse_json_response(message.content[0].text)


def generate_srs(
    project_name: str,
    description: str,
    domain_name: str,
    country: str,
    functional: list,
    non_functional: list,
) -> str:
    """Build an IEEE 830 SRS prompt, call Claude, return the raw SRS text."""
    fr_text = "\n".join([f"{r.code}: {r.description}" for r in functional])
    nfr_text = "\n".join([f"{r.code}: {r.description}" for r in non_functional])

    prompt = f"""Generate a complete IEEE 830 Software Requirements Specification (SRS) document for the following project:

Project Name: {project_name}
Domain: {domain_name}
Country: {country}
Description: {description}

Functional Requirements:
{fr_text}

Non-Functional Requirements:
{nfr_text}

Generate a complete SRS document following IEEE 830 standard with these sections:
1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Definitions and Abbreviations
   1.4 References
   1.5 Overview
2. Overall Description
   2.1 Product Perspective
   2.2 Product Functions
   2.3 User Classes and Characteristics
   2.4 Operating Environment
   2.5 Constraints
3. Specific Requirements
   3.1 Functional Requirements
   3.2 Non-Functional Requirements
4. Appendices

Make it professional and complete."""

    try:
        message = _get_client().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        logger.exception("Claude SRS call failed")
        raise HTTPException(status_code=503, detail="AI service unavailable. Please try again.")
    return message.content[0].text


def run_crosscheck(req_list: str, answers_text: str, kb_context: str) -> list:
    """Build a cross-check prompt, call Claude, return a list of issue dicts."""
    prompt = f"""You are a senior requirements engineer.

Analyze the following requirements using:
1. Internal consistency (requirements vs requirements)
2. User answers (original input)
3. Domain knowledge (rules and regulations)

Requirements:
{req_list}

User Answers:
{answers_text}

Domain Knowledge:
{kb_context}

Find issues and return JSON array. Each issue must have:
- requirement_code: the code of the problematic requirement (e.g., "FR-1")
- issue_type: one of ["ambiguity", "duplicate", "inconsistency", "conflict", "unsupported"]
- issue_detail: clear explanation of the issue
- conflict_with: specify EXACTLY what this conflicts with:
  * If conflicts with another requirement: "Requirement FR-X" or "Requirement NFR-X"
  * If conflicts with domain rules: "Domain Knowledge: [quote the specific rule]"
  * If unsupported by user input: "User Answer: [quote what user said or didn't say]"
  * If duplicate: "Duplicate of FR-X"
  * If ambiguity: "N/A"

Return ONLY a valid JSON array. If no issues found, return []."""

    try:
        message = _get_client().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        logger.exception("Claude crosscheck call failed")
        raise HTTPException(status_code=503, detail="AI service unavailable. Please try again.")
    return parse_json_response(message.content[0].text)
