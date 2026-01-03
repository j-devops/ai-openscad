import { useEffect, useRef } from 'react'
import './Console.css'

export interface ConsoleMessage {
  id: string
  timestamp: Date
  type: 'info' | 'warning' | 'error' | 'success'
  message: string
}

interface ConsoleProps {
  messages: ConsoleMessage[]
  onClear?: () => void
}

export default function Console({ messages, onClear }: ConsoleProps) {
  const consoleEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'error': return '✖'
      case 'warning': return '⚠'
      case 'success': return '✓'
      default: return '●'
    }
  }

  return (
    <div className="console">
      <div className="console-header">
        <h3>Console Output</h3>
        <div className="console-actions">
          <span className="console-count">{messages.length} messages</span>
          {onClear && (
            <button onClick={onClear} className="console-clear" title="Clear console">
              Clear
            </button>
          )}
        </div>
      </div>
      <div className="console-content">
        {messages.length === 0 ? (
          <div className="console-empty">
            <p>Console output will appear here...</p>
            <p className="console-hint">Compilation messages, warnings, and errors</p>
          </div>
        ) : (
          <div className="console-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`console-message console-${msg.type}`}>
                <span className="console-time">[{formatTime(msg.timestamp)}]</span>
                <span className="console-icon">{getMessageIcon(msg.type)}</span>
                <span className="console-text">{msg.message}</span>
              </div>
            ))}
            <div ref={consoleEndRef} />
          </div>
        )}
      </div>
    </div>
  )
}
