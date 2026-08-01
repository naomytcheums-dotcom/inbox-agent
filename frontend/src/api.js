export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8050'

async function handle(res) {
  if (!res.ok) {
    let message = 'Something went wrong.'
    try {
      const data = await res.json()
      message = data.detail || message
    } catch {
      // ignore
    }
    throw new Error(message)
  }
  return res.json()
}

export function connectGmailUrl() {
  return `${API_URL}/api/gmail/connect`
}

export async function getGmailStatus() {
  const res = await fetch(`${API_URL}/api/gmail/status`)
  return handle(res)
}

export async function checkInbox() {
  const res = await fetch(`${API_URL}/api/gmail/check`, { method: 'POST' })
  return handle(res)
}

export async function listProcessedEmails() {
  const res = await fetch(`${API_URL}/api/gmail/emails`)
  return handle(res)
}

export async function getSettings() {
  const res = await fetch(`${API_URL}/api/settings`)
  return handle(res)
}

export async function saveSettings(settings) {
  const res = await fetch(`${API_URL}/api/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  return handle(res)
}
