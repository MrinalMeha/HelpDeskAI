import React from 'react'

export function StatusBadge({ status, size = 'md' }) {
  const map = {
    diagnosing: { label: 'Diagnosing', cls: 'badge-info' },
    classifying: { label: 'Classifying', cls: 'badge-info' },
    ticket_created: { label: 'Ticket Created', cls: 'badge-warning' },
    resolved: { label: 'Resolved', cls: 'badge-success' },
    error: { label: 'Error', cls: 'badge-danger' },
    greeting: { label: 'Idle', cls: 'badge-muted' },
    Open: { label: 'Open', cls: 'badge-info' },
    'In Progress': { label: 'In Progress', cls: 'badge-warning' },
    Resolved: { label: 'Resolved', cls: 'badge-success' },
    Closed: { label: 'Closed', cls: 'badge-muted' },
    Low: { label: 'Low', cls: 'badge-success' },
    Medium: { label: 'Medium', cls: 'badge-warning' },
    High: { label: 'High', cls: 'badge-danger' },
    Critical: { label: 'Critical', cls: 'badge-danger' },
  }

  const config = map[status] || { label: status || 'Unknown', cls: 'badge-muted' }

  return (
    <span className={`badge ${config.cls}`} style={size === 'sm' ? { fontSize: '10px', padding: '2px 8px' } : {}}>
      {config.label}
    </span>
  )
}
