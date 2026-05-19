import json
import logging
from app.core.ai import _get_client

logger = logging.getLogger("requirements_ai")


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

    message = _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
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

    message = _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
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

    message = _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_json_response(message.content[0].text)
