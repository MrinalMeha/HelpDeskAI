import React from 'react'
import { StatusBadge } from './StatusBadge'
import './TicketPanel.css'

export function TicketPanel({ ticket }) {
  if (!ticket) return null

  const formatDate = (iso) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="ticket-panel fade-in">
      <div className="ticket-header">
        <div className="flex items-center gap-2">
          <span className="ticket-icon">🎫</span>
          <span className="ticket-label">Ticket Created</span>
        </div>
        <StatusBadge status="ticket_created" size="sm" />
      </div>

      <div className="ticket-id-row">
        <span className="ticket-id">{ticket.ticket_id}</span>
        <StatusBadge status={ticket.priority} size="sm" />
      </div>

      <div className="ticket-meta">
        <div className="ticket-meta-item">
          <span className="meta-label">Category</span>
          <span className="meta-value">{ticket.category}</span>
        </div>
        <div className="ticket-meta-item">
          <span className="meta-label">Status</span>
          <StatusBadge status={ticket.status || 'Open'} size="sm" />
        </div>
        <div className="ticket-meta-item">
          <span className="meta-label">Created</span>
          <span className="meta-value">{formatDate(ticket.created_at)}</span>
        </div>
      </div>

      <div className="divider" />

      <div className="ticket-desc">
        <span className="meta-label">Description</span>
        <p className="desc-text">{ticket.description}</p>
      </div>
    </div>
  )
}
