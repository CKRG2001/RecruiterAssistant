"""
Guardrails for Recruiter Assistant.

Purpose:
- Block off-topic questions that are not related to resume/candidate evaluation.
- Detect common prompt-injection and jailbreak attempts.
- Keep the assistant scoped to recruiter-style resume analysis.
"""

from __future__ import annotations
import re
from dataclasses import dataclass


OFF_TOPIC_RESPONSE = (
    "I can only answer questions related to the candidate's resume, skills, "
    "experience, education, projects, achievements, or role fit."
)

PROMPT_INJECTION_RESPONSE = (
    "I can’t follow instructions that try to override the system rules, reveal hidden prompts, "
    "ignore resume context, or access private data. Please ask a resume-related question."
)


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str
    message: str | None = None


PROMPT_INJECTION_PATTERNS = [
    r"\bignore (all )?(previous|prior|above|earlier) instructions\b",
    r"\bdisregard (all )?(previous|prior|above|earlier) instructions\b",
    r"\boverride (the )?(system|developer|previous|prior) instructions\b",
    r"\bforget (the )?(system|developer|previous|prior) instructions\b",
    r"\bnew instructions?\b",
    r"\byou are now\b",
    r"\bact as\b.*\b(jailbreak|unrestricted|uncensored|developer mode)\b",
    r"\bdeveloper mode\b",
    r"\bjailbreak\b",
    r"\bDAN\b",
    r"\breveal\b.*\b(system prompt|developer prompt|hidden prompt|instructions)\b",
    r"\bshow\b.*\b(system prompt|developer prompt|hidden prompt|instructions)\b",
    r"\bprint\b.*\b(system prompt|developer prompt|hidden prompt|instructions)\b",
    r"\bwhat are your (system|developer|hidden) instructions\b",
    r"\bexfiltrate\b",
    r"\bapi[_ -]?key\b",
    r"\bOPENAI_API_KEY\b",
    r"\b.env\b",
    r"\bsecret(s)?\b",
    r"\bpassword(s)?\b",
    r"\btoken(s)?\b",
    r"\bprivate key\b",
    r"\bbase64\b.*\bdecode\b",
    r"\bexecute\b.*\bcode\b",
    r"\brun\b.*\bcommand\b",
    r"\bdelete\b.*\bfile\b",
    r"\bread\b.*\b(local|server|system) file\b",
]


def normalize_text(text: str) -> str:
    """Normalize user input for safer checks."""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def is_prompt_injection(question: str) -> bool:
    """Return True when the question contains common injection/jailbreak patterns."""
    q = normalize_text(question)
    if not q:
        return False

    return any(
        re.search(pattern, q, flags=re.IGNORECASE)
        for pattern in PROMPT_INJECTION_PATTERNS
    )


def validate_question(question: str) -> GuardrailResult:
    """
    Validate a recruiter question before retrieval or LLM calls.

    Order matters:
    1. Empty question
    2. Prompt injection / unsafe instruction override
    3. Off-topic intent
    """
    q = normalize_text(question)

    if not q:
        return GuardrailResult(
            allowed=False,
            reason="empty_question",
            message="Please ask a resume-related question.",
        )

    if is_prompt_injection(q):
        return GuardrailResult(
            allowed=False,
            reason="prompt_injection",
            message=PROMPT_INJECTION_RESPONSE,
        )

    return GuardrailResult(allowed=True, reason="allowed", message=None)


# def strip_unsafe_chat_history(chat_history: list[dict], max_messages: int = 8) -> list[dict]:
#     """
#     Keep recent safe chat history only.

#     This prevents earlier malicious user turns from being repeatedly passed back into the model.
#     """
#     safe_messages: list[dict] = []

#     for msg in chat_history[-max_messages:]:
#         role = msg.get("role")
#         content = msg.get("content", "")

#         if role not in {"user", "assistant"}:
#             continue

#         if role == "user" and is_prompt_injection(content):
#             continue

#         safe_messages.append({"role": role, "content": content})

#     return safe_messages
