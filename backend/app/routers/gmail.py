from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth import require_site_password
from app.config import settings
from app.database import get_db
from app.models import GmailAccount, ProcessedEmail
from app.schemas import CheckInboxResult, GmailStatusOut, ProcessedEmailOut
from app.services import google_oauth
from app.services.inbox_runner import InboxError, check_inbox

router = APIRouter(prefix="/api/gmail", tags=["gmail"])


@router.get("/connect")
def connect():
    if not settings.google_client_id:
        raise HTTPException(400, "Google OAuth is not configured on this server.")
    return RedirectResponse(google_oauth.build_auth_url())


@router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    tokens = await google_oauth.exchange_code(code)
    email_address = await google_oauth.get_user_email(tokens["access_token"])

    account = db.query(GmailAccount).first()
    if not account:
        account = GmailAccount()
        db.add(account)

    account.email_address = email_address
    account.access_token = tokens["access_token"]
    if tokens.get("refresh_token"):
        account.refresh_token = tokens["refresh_token"]
    account.token_expiry = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
    account.connected_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(f"{settings.frontend_url}?connected=true")


@router.get("/status", response_model=GmailStatusOut, dependencies=[Depends(require_site_password)])
def status(db: Session = Depends(get_db)):
    oauth_configured = bool(settings.google_client_id and settings.google_client_secret)
    account = db.query(GmailAccount).first()
    if not account or not account.refresh_token:
        return GmailStatusOut(connected=False, oauth_configured=oauth_configured)
    return GmailStatusOut(connected=True, email_address=account.email_address, oauth_configured=oauth_configured)


@router.post("/check", response_model=CheckInboxResult, dependencies=[Depends(require_site_password)])
async def check(db: Session = Depends(get_db)):
    try:
        result = await check_inbox(db)
    except InboxError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Error checking inbox: {exc}") from exc
    return result


@router.get("/emails", response_model=list[ProcessedEmailOut], dependencies=[Depends(require_site_password)])
def list_emails(db: Session = Depends(get_db)):
    return db.query(ProcessedEmail).order_by(ProcessedEmail.created_at.desc()).limit(50).all()
