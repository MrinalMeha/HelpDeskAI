import React, { useState, useCallback } from 'react'
import { ChatInterface } from '../components/ChatInterface'
import { AgentActivity } from '../components/AgentActivity'
import { TicketPanel } from '../components/TicketPanel'
import { MyTickets } from '../components/MyTickets'
import { StatusBadge } from '../components/StatusBadge'
import './Dashboard.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const SESSION_ID = 'demo-session-' + Math.random().toString(36).slice(2, 8)

export function Dashboard() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const isRequesting = React.useRef(false)
  const [status, setStatus] = useState('greeting')
  const [issueCategory, setIssueCategory] = useState(null)
  const [severity, setSeverity] = useState(null)
  const [agentActivity, setAgentActivity] = useState([])
  const [currentTicket, setCurrentTicket] = useState(null)
  const [activeTab, setActiveTab] = useState('chat') // 'chat' | 'tickets'

  const addMessage = (role, text) => {
    setMessages((prev) => [
      ...prev,
      { id: Date.now() + Math.random(), role, text, timestamp: new Date().toISOString() },
    ])
  }

  const sendMessage = useCallback(async (text) => {
    if (isRequesting.current) return
    isRequesting.current = true
    setIsLoading(true)
    
    const message_id = Date.now().toString(36) + Math.random().toString(36).slice(2)
    
    addMessage('user', text)

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: SESSION_ID, message_id }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()

      addMessage('ai', data.message)
      setStatus(data.status)
      if (data.issue_category) setIssueCategory(data.issue_category)
      if (data.severity) setSeverity(data.severity)
      if (data.agent_activity?.length) setAgentActivity(data.agent_activity)

      if (data.ticket_id && data.ticket_details) {
        setCurrentTicket({
          ...data.ticket_details,
          ticket_id: data.ticket_id,
        })
      }
    } catch (e) {
      addMessage('ai', `⚠️ Error: ${e.message}. Please make sure the backend is running.`)
      setStatus('error')
    } finally {
      setIsLoading(false)
      isRequesting.current = false
    }
  }, [isLoading])

  const handleReset = async () => {
    // Reset session on backend
    try {
      await fetch(`${API_BASE}/api/session/${SESSION_ID}`, { method: 'DELETE' })
    } catch (_) {}
    setMessages([])
    setStatus('greeting')
    setIssueCategory(null)
    setSeverity(null)
    setAgentActivity([])
    setCurrentTicket(null)
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <div className="header-logo">
            <span className="logo-icon">🤖</span>
            <div>
              <h1 className="header-title">HelpDeskAI</h1>
              <p className="header-sub">AI-powered Internal IT Support</p>
            </div>
          </div>
        </div>
        <div className="header-right">
          {issueCategory && (
            <div className="header-meta">
              <span className="meta-chip">{issueCategory}</span>
              {severity && <StatusBadge status={severity} size="sm" />}
            </div>
          )}
          <div className="user-chip">
            <span className="user-avatar-sm">👤</span>
            <div>
              <div className="user-name">Demo Employee</div>
              <div className="user-id">EMP001 · Engineering</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="pulse-dot" />
            <span style={{ fontSize: 11, color: 'var(--success)' }}>Online</span>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === 'chat' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat Support
        </button>
        <button
          className={`tab-btn ${activeTab === 'tickets' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('tickets')}
        >
          📋 My Tickets
        </button>
      </div>

      {/* Main Content */}
      {activeTab === 'chat' ? (
        <div className="chat-layout">
          {/* Left: Chat */}
          <div className="chat-main">
            <ChatInterface
              messages={messages}
              onSendMessage={sendMessage}
              isLoading={isLoading}
              status={status}
              onReset={handleReset}
            />
          </div>

          {/* Right: Sidebar */}
          <div className="chat-sidebar">
            <AgentActivity
              activities={agentActivity}
              status={status}
              issueCategory={issueCategory}
            />
            {currentTicket && (
              <>
                <div className="divider" />
                <TicketPanel ticket={currentTicket} />
              </>
            )}
          </div>
        </div>
      ) : (
        <div className="tickets-layout">
          <MyTickets />
        </div>
      )}
    </div>
  )
}
