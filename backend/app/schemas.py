from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReplySettingsIn(BaseModel):
    tone_instructions: str
    signature: str


class ReplySettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tone_instructions: str
    signature: str
    updated_at: datetime


class GmailStatusOut(BaseModel):
    connected: bool
    email_address: str = ""
    oauth_configured: bool = False


class ProcessedEmailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_message_id: str
    thread_id: str
    subject: str
    from_address: str
    needs_reply: bool
    draft_created: bool
    draft_preview: str
    created_at: datetime


class CheckInboxResult(BaseModel):
    emails_scanned: int
    drafts_created: int
    emails: list[ProcessedEmailOut]
