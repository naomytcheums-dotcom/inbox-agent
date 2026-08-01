from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_site_password
from app.database import get_db
from app.models import ReplySettings
from app.schemas import ReplySettingsIn, ReplySettingsOut

router = APIRouter(prefix="/api/settings", tags=["settings"], dependencies=[Depends(require_site_password)])


@router.get("", response_model=ReplySettingsOut | None)
def get_settings(db: Session = Depends(get_db)):
    return db.query(ReplySettings).first()


@router.put("", response_model=ReplySettingsOut)
def upsert_settings(payload: ReplySettingsIn, db: Session = Depends(get_db)):
    reply_settings = db.query(ReplySettings).first()
    if not reply_settings:
        reply_settings = ReplySettings()
        db.add(reply_settings)
    reply_settings.tone_instructions = payload.tone_instructions
    reply_settings.signature = payload.signature
    db.commit()
    db.refresh(reply_settings)
    return reply_settings
