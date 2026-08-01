import json
import re

from app.config import settings
from app.services.llm_client import get_client

NEEDS_REPLY_PROMPT = (
    "You decide whether an incoming email requires a reply from the recipient. "
    "Marketing emails, newsletters, automated notifications, and receipts do NOT need a "
    "reply. A real message from a real person asking a question, requesting something, "
    "or continuing a conversation DOES need a reply.\n\n"
    'Respond with ONLY valid JSON, no markdown, no extra text: {"needs_reply": true or false}'
)

DEFAULT_REPLY_INSTRUCTIONS = (
    "Be concise and maintain a business casual tone. Start with \"Hello,\" and end with "
    "\"Best,\". When replying to a yes-no question, draft two short options — one "
    "affirmative, one negative — separated by a line with just \"---\". If you don't know "
    "an answer, leave a placeholder like [YOUR ANSWER HERE]. Plain text only, no markdown "
    "formatting. Reply in the same language as the inbound email."
)


def _strip_code_fence(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def needs_reply(subject: str, body: str) -> bool:
    client = get_client()
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": NEEDS_REPLY_PROMPT},
            {"role": "user", "content": f"Subject: {subject}\n\n{body[:3000]}"},
        ],
        temperature=0,
        max_tokens=1024,
    )
    raw = response.choices[0].message.content.strip()
    try:
        return bool(json.loads(_strip_code_fence(raw)).get("needs_reply", False))
    except (json.JSONDecodeError, AttributeError):
        return False


def generate_reply(subject: str, body: str, tone_instructions: str, signature: str) -> str:
    client = get_client()

    instructions = tone_instructions.strip() or DEFAULT_REPLY_INSTRUCTIONS
    system_prompt = (
        "You're a helpful personal assistant drafting a reply on behalf of the user to an "
        "incoming email. Return only the reply text, nothing else. Do not make things up — "
        "if you don't know something, use a placeholder.\n\n"
        f"Instructions:\n{instructions}"
    )
    if signature.strip():
        system_prompt += f"\n\nSign off with:\n{signature.strip()}"

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Subject: {subject}\n\n{body[:4000]}"},
        ],
        temperature=0.4,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
