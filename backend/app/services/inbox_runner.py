from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import GmailAccount, ProcessedEmail, ReplySettings
from app.services import gmail_client, google_oauth
from app.services.reply_agent import generate_reply, needs_reply

QUERY = "-from:me newer_than:2d"


class InboxError(RuntimeError):
    pass


async def _valid_access_token(db: Session, account: GmailAccount) -> str:
    if account.token_expiry > datetime.utcnow() + timedelta(seconds=60):
        return account.access_token

    tokens = await google_oauth.refresh_access_token(account.refresh_token)
    account.access_token = tokens["access_token"]
    account.token_expiry = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
    db.commit()
    return account.access_token


async def check_inbox(db: Session) -> dict:
    account = db.query(GmailAccount).first()
    if not account:
        raise InboxError("Gmail is not connected yet.")

    access_token = await _valid_access_token(db, account)

    reply_settings = db.query(ReplySettings).first()
    tone = reply_settings.tone_instructions if reply_settings else ""
    signature = reply_settings.signature if reply_settings else ""

    message_ids = await gmail_client.list_message_ids(access_token, QUERY)
    already_processed = {
        row.gmail_message_id
        for row in db.query(ProcessedEmail).filter(ProcessedEmail.gmail_message_id.in_(message_ids)).all()
    }

    new_records = []
    for message_id in message_ids:
        if message_id in already_processed:
            continue

        message = await gmail_client.get_message(access_token, message_id)
        reply_needed = needs_reply(message["subject"], message["body_text"])

        draft_created = False
        draft_preview = ""
        if reply_needed:
            draft_preview = generate_reply(message["subject"], message["body_text"], tone, signature)
            await gmail_client.create_draft_reply(
                access_token,
                to_address=message["from_address"],
                subject=message["subject"],
                body_text=draft_preview,
                thread_id=message["thread_id"],
                in_reply_to=message["message_id_header"],
            )
            draft_created = True

        record = ProcessedEmail(
            gmail_message_id=message["id"],
            thread_id=message["thread_id"],
            subject=message["subject"],
            from_address=message["from_address"],
            needs_reply=reply_needed,
            draft_created=draft_created,
            draft_preview=draft_preview,
        )
        db.add(record)
        new_records.append(record)

    db.commit()
    for record in new_records:
        db.refresh(record)

    return {
        "emails_scanned": len(message_ids),
        "drafts_created": sum(1 for r in new_records if r.draft_created),
        "emails": new_records,
    }
