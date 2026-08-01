import { useEffect, useState } from 'react'
import { checkInbox, connectGmailUrl, getGmailStatus, listProcessedEmails } from '../api'

function Inbox() {
  const [status, setStatus] = useState(null)
  const [emails, setEmails] = useState([])
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState(null)
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    refresh()
  }, [])

  async function refresh() {
    try {
      const current = await getGmailStatus()
      setStatus(current)
      if (current.connected) {
        const list = await listProcessedEmails()
        setEmails(list)
      }
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleCheck() {
    setChecking(true)
    setError(null)
    setSummary(null)
    try {
      const result = await checkInbox()
      setSummary(result)
      const list = await listProcessedEmails()
      setEmails(list)
    } catch (err) {
      setError(err.message)
    } finally {
      setChecking(false)
    }
  }

  if (!status) return null

  if (!status.connected) {
    return (
      <div>
        <div className="page-header">
          <h1>Inbox Agent</h1>
          <p>Connect Gmail to let the AI draft replies to your incoming emails — nothing ever sends on its own.</p>
        </div>
        <div className="card connect-card">
          <h2>Connect your Gmail account</h2>
          <p>You'll be asked to authorize read + draft access. Inbox Agent never sends email on your behalf.</p>
          <a className="btn-primary" href={connectGmailUrl()}>
            Connect Gmail
          </a>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Inbox</h1>
        <p>Scan your inbox for emails that need a reply, and draft one for each — saved straight to Gmail as a draft.</p>
      </div>

      {error && <div className="form-error">{error}</div>}
      {summary && (
        <div className="form-success">
          Scanned {summary.emails_scanned} email{summary.emails_scanned === 1 ? '' : 's'}, created{' '}
          {summary.drafts_created} draft{summary.drafts_created === 1 ? '' : 's'}.
        </div>
      )}

      <div className="connected-bar">
        <div className="connected-status">
          <span className="connected-dot" />
          Connected as {status.email_address}
        </div>
        <button className="btn-primary" onClick={handleCheck} disabled={checking}>
          {checking ? 'Checking…' : 'Check inbox now'}
        </button>
      </div>

      {emails.length === 0 && <div className="empty-state">No emails processed yet — click "Check inbox now" above.</div>}

      <div className="emails-grid">
        {emails.map((email) => (
          <div className="email-card" key={email.id}>
            <div className="email-card-top">
              <div>
                <div className="email-subject">{email.subject || '(no subject)'}</div>
                <div className="email-from">{email.from_address}</div>
              </div>
              <span className={`reply-badge ${email.needs_reply ? 'needed' : 'skipped'}`}>
                {email.needs_reply ? 'Draft created' : 'No reply needed'}
              </span>
            </div>

            {email.draft_preview && (
              <div className="draft-box">
                <div className="draft-label">Draft reply</div>
                {email.draft_preview}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Inbox
