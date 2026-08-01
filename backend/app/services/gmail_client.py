import base64
from email.mime.text import MIMEText

import httpx

GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


async def list_message_ids(access_token: str, query: str, max_results: int = 15) -> list[str]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{GMAIL_API}/messages",
            params={"q": query, "maxResults": max_results},
            headers=_headers(access_token),
        )
        response.raise_for_status()
        data = response.json()
        return [m["id"] for m in data.get("messages", [])]


def _find_header(headers: list[dict], name: str) -> str:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def _extract_plain_text(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        text = _extract_plain_text(part)
        if text:
            return text
    return ""


async def get_message(access_token: str, message_id: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{GMAIL_API}/messages/{message_id}",
            params={"format": "full"},
            headers=_headers(access_token),
        )
        response.raise_for_status()
        data = response.json()

    payload = data.get("payload", {})
    headers = payload.get("headers", [])
    return {
        "id": data["id"],
        "thread_id": data.get("threadId", ""),
        "subject": _find_header(headers, "Subject"),
        "from_address": _find_header(headers, "From"),
        "message_id_header": _find_header(headers, "Message-ID"),
        "body_text": _extract_plain_text(payload) or data.get("snippet", ""),
    }


async def create_draft_reply(
    access_token: str,
    to_address: str,
    subject: str,
    body_text: str,
    thread_id: str,
    in_reply_to: str,
) -> None:
    mime_message = MIMEText(body_text, "plain")
    mime_message["To"] = to_address
    mime_message["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if in_reply_to:
        mime_message["In-Reply-To"] = in_reply_to
        mime_message["References"] = in_reply_to

    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{GMAIL_API}/drafts",
            json={"message": {"raw": raw, "threadId": thread_id}},
            headers=_headers(access_token),
        )
        response.raise_for_status()
