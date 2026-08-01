import { useEffect, useState } from 'react'
import { getSettings, saveSettings } from '../api'

function Settings() {
  const [toneInstructions, setToneInstructions] = useState('')
  const [signature, setSignature] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getSettings()
      .then((settings) => {
        if (settings) {
          setToneInstructions(settings.tone_instructions || '')
          setSignature(settings.signature || '')
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      await saveSettings({ tone_instructions: toneInstructions, signature })
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return null

  return (
    <div>
      <div className="page-header">
        <h1>Reply settings</h1>
        <p>Tell the AI how you want your drafts written. Leave blank to use sensible defaults.</p>
      </div>

      <div className="card">
        {error && <div className="form-error">{error}</div>}
        {saved && <div className="form-success">Settings saved.</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label>
              Tone & instructions <span className="hint">how replies should sound</span>
            </label>
            <textarea
              value={toneInstructions}
              onChange={(e) => setToneInstructions(e.target.value)}
              placeholder="e.g. Friendly but professional. Keep it short — 3 sentences max. Reply in the same language as the inbound email. If a question needs info I don't have, use a placeholder like [ANSWER HERE]."
            />
          </div>

          <div className="form-field">
            <label>
              Signature <span className="hint">appended to every draft</span>
            </label>
            <textarea
              value={signature}
              onChange={(e) => setSignature(e.target.value)}
              placeholder={'e.g. Best,\nNaomy'}
            />
          </div>

          <button className="btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Save settings'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Settings
