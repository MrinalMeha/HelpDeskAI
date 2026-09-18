import React, { useState } from 'react'
import { StatusBadge } from './StatusBadge'
import './MyTickets.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export function MyTickets() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(null)

  const loadTickets = async () => {
    if (loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/tickets`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setTickets(data)
      setLoaded(true)
    } catch (e) {
      setError('Could not load tickets. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const toggleExpand = (id) => {
    setExpanded(expanded === id ? null : id)
  }

  const formatDate = (iso) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const priorityOrder = { Critical: 0, High: 1, Medium: 2, Low: 3 }
  const sorted = [...tickets].sort((a, b) =>
    (priorityOrder[a.priority] ?? 4) - (priorityOrder[b.priority] ?? 4)
  )

  return (
    <div className="my-tickets">
      <div className="mt-header">
        <div className="flex items-center gap-2">
          <span>📋</span>
          <span className="mt-title">My Tickets</span>
          {loaded && tickets.length > 0 && (
            <span className="mt-count">{tickets.length}</span>
          )}
        </div>
        <button
          className="btn-outline"
          onClick={loadTickets}
          disabled={loading}
        >
          {loading ? 'Loading...' : loaded ? '↻ Refresh' : 'Load Tickets'}
        </button>
      </div>

      {error && (
        <div className="mt-error">
          ⚠️ {error}
        </div>
      )}

      {loaded && tickets.length === 0 && (
        <div className="mt-empty">
          No tickets found. Describe an IT issue to get started.
        </div>
      )}

      <div className="tickets-list">
        {sorted.map((t) => (
          <div
            key={t.ticket_id}
            className={`ticket-card fade-in ${expanded === t.ticket_id ? 'ticket-card-expanded' : ''}`}
          >
            <div
              className="ticket-card-header"
              onClick={() => toggleExpand(t.ticket_id)}
            >
              <div className="flex items-center gap-2">
                <span className="tc-id">{t.ticket_id}</span>
                <span className="tc-category">{t.category}</span>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={t.priority} size="sm" />
                <StatusBadge status={t.status} size="sm" />
                <span className="tc-chevron">{expanded === t.ticket_id ? '▲' : '▼'}</span>
              </div>
            </div>

            <div className="tc-date">{formatDate(t.created_at)}</div>

            {expanded === t.ticket_id && (
              <div className="tc-details fade-in">
                <div className="divider" style={{ margin: '8px 0' }} />
                <div className="tc-desc">{t.description}</div>
                {t.diagnostics && t.diagnostics.length > 0 && (
                  <div className="tc-diagnostics">
                    <div className="tc-diag-label">Diagnostic Steps</div>
                    {t.diagnostics.map((d, i) => (
                      <div key={i} className="tc-diag-item">
                        <span className="tc-diag-step">{d.step}</span>
                        <span className="tc-diag-result">→ {d.result}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
