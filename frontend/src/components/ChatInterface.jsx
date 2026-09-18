import React, { useState, useRef, useEffect } from 'react'
import { StatusBadge } from './StatusBadge'
import './ChatInterface.css'

const STARTER_QUESTIONS = [
  "My VPN isn't connecting",
  "My Outlook isn't syncing",
  "I can't connect to Wi-Fi",
  "My laptop is extremely slow",
  "I forgot my password",
  "An application won't open",
]

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user'

  // Format markdown-style bold text
  const formatText = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>
      }
      return <span key={i}>{part}</span>
    })
  }

  return (
    <div className={`message-row ${isUser ? 'message-user' : 'message-ai'} fade-in`}>
      {!isUser && (
        <div className="avatar ai-avatar">
          <span>🤖</span>
        </div>
      )}
      <div className={`bubble ${isUser ? 'bubble-user' : 'bubble-ai'}`}>
        <div className="bubble-text">
          {msg.text.split('\n').map((line, i) => (
            <span key={i}>
              {formatText(line)}
              {i < msg.text.split('\n').length - 1 && <br />}
            </span>
          ))}
        </div>
        <div className="bubble-meta">
          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
      {isUser && (
        <div className="avatar user-avatar">
          <span>👤</span>
        </div>
      )}
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="message-row message-ai fade-in">
      <div className="avatar ai-avatar">
        <span>🤖</span>
      </div>
      <div className="bubble bubble-ai typing-bubble">
        <div className="typing-dots">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  )
}

export function ChatInterface({ onSendMessage, messages, isLoading, status, onReset }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isLoading) return
    onSendMessage(text)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleStarter = (q) => {
    if (isLoading) return
    onSendMessage(q)
  }

  const showStarters = messages.length === 0

  return (
    <div className="chat-container">
      {/* Messages Area */}
      <div className="messages-area">
        {showStarters ? (
          <div className="starters-wrapper fade-in">
            <div className="starters-intro">
              <div className="bot-welcome">
                <div className="welcome-icon">🤖</div>
                <h2 className="welcome-title">HelpDeskAI</h2>
                <p className="welcome-sub">
                  Describe your IT issue and I'll help you troubleshoot it step by step.
                </p>
              </div>
            </div>
            <div className="starters-grid">
              {STARTER_QUESTIONS.map((q) => (
                <button
                  key={q}
                  className="starter-btn"
                  onClick={() => handleStarter(q)}
                  disabled={isLoading}
                >
                  <span className="starter-icon">💬</span>
                  <span>{q}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}
            {isLoading && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Reply Buttons for Yes/No */}
      {status === 'diagnosing' && !isLoading && messages.length > 0 && (
        <div className="quick-replies">
          <span className="qr-label">Quick reply:</span>
          {['Yes, that fixed it!', 'No, still not working', 'Not sure'].map((reply) => (
            <button
              key={reply}
              className="qr-btn"
              onClick={() => {
                onSendMessage(reply)
              }}
            >
              {reply}
            </button>
          ))}
        </div>
      )}

      {/* Status bar */}
      {status && status !== 'greeting' && messages.length > 0 && (
        <div className="chat-status-bar">
          <div className="flex items-center gap-2">
            {isLoading && <div className="spinner" style={{ width: 12, height: 12 }} />}
            <StatusBadge status={status} size="sm" />
          </div>
          <button className="btn-ghost text-xs" onClick={onReset} title="Start new conversation">
            ↺ New Issue
          </button>
        </div>
      )}

      {/* Input Area */}
      <div className="input-area">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your IT issue..."
          rows={2}
          disabled={isLoading}
        />
        <button
          className="send-btn btn-primary"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? <div className="spinner" style={{ width: 14, height: 14 }} /> : '→'}
        </button>
      </div>
    </div>
  )
}
