import React from 'react'
import './AgentActivity.css'

export function AgentActivity({ activities = [], status, issueCategory }) {
  const isLoading = status === 'diagnosing' || status === 'classifying'

  return (
    <div className="agent-activity-panel">
      <div className="aa-header">
        <div className="flex items-center gap-2">
          <span className="aa-icon">⚡</span>
          <span className="aa-title">Agent Activity</span>
        </div>
        {isLoading && <div className="spinner" />}
      </div>

      {issueCategory && (
        <div className="aa-category">
          <span className="aa-cat-label">Category</span>
          <span className="aa-cat-value">{issueCategory}</span>
        </div>
      )}

      <div className="aa-timeline">
        {activities.length === 0 ? (
          <div className="aa-empty">
            <span>Awaiting your first message...</span>
          </div>
        ) : (
          activities.map((activity, idx) => (
            <div key={idx} className="aa-item fade-in">
              <span className="aa-item-icon">
                {activity.startsWith('✓') ? '✓' :
                 activity.startsWith('⚠') ? '⚠' :
                 activity.startsWith('⟳') ? '⟳' : '•'}
              </span>
              <span className={`aa-item-text ${
                activity.startsWith('✓') ? 'aa-success' :
                activity.startsWith('⚠') ? 'aa-warning' :
                activity.startsWith('⟳') ? 'aa-loading' : ''
              }`}>
                {activity.replace(/^[✓⚠⟳•]\s?/, '')}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
