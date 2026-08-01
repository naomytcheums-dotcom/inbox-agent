from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_address: Mapped[str] = mapped_column(String, default="")
    access_token: Mapped[str] = mapped_column(Text, default="")
    refresh_token: Mapped[str] = mapped_column(Text, default="")
    token_expiry: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReplySettings(Base):
    __tablename__ = "reply_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tone_instructions: Mapped[str] = mapped_column(Text, default="")
    signature: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gmail_message_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    thread_id: Mapped[str] = mapped_column(String, default="")
    subject: Mapped[str] = mapped_column(String, default="")
    from_address: Mapped[str] = mapped_column(String, default="")
    needs_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    draft_created: Mapped[bool] = mapped_column(Boolean, default=False)
    draft_preview: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
