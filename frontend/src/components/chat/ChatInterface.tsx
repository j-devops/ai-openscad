import { useState, useRef, useEffect } from 'react'
import { useSettingsStore } from '../../store/settingsStore'
import './ChatInterface.css'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  currentCode: string
  onCodeModified: (code: string) => void
  onLog?: (type: 'info' | 'warning' | 'error' | 'success', message: string) => void
}

export default function ChatInterface({ currentCode, onCodeModified, onLog }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { llm } = useSettingsStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsProcessing(true)
    onLog?.('info', `Processing: "${input.trim()}"`)

    try {
      // TODO: Call chat API endpoint
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input.trim(),
          current_code: currentCode,
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content
          })),
          model: llm.model,
          temperature: llm.temperature,
          max_tokens: llm.maxTokens
        })
      })

      if (!response.ok) {
        throw new Error('Chat request failed')
      }

      const data = await response.json()

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // If the response includes modified code, update it
      if (data.modified_code && data.modified_code !== currentCode) {
        onCodeModified(data.modified_code)
        onLog?.('success', 'Code updated based on conversation')
      }

    } catch (err: any) {
      const errorMsg = err.message || 'Failed to process chat message'
      onLog?.('error', errorMsg)

      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMsg}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleClear = () => {
    setMessages([])
    onLog?.('info', 'Chat conversation cleared')
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>Chat Assistant</h3>
        <button onClick={handleClear} className="chat-clear-btn" disabled={messages.length === 0}>
          Clear
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>💬 Start a conversation about your model</p>
            <p className="chat-hint">Try: "Make it 2x bigger" or "Add mounting holes" or "Explain this code"</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message chat-${msg.role}`}>
            <div className="chat-message-header">
              <span className="chat-role">{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
              <span className="chat-timestamp">
                {msg.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <div className="chat-message-content">{msg.content}</div>
          </div>
        ))}

        {isProcessing && (
          <div className="chat-message chat-assistant">
            <div className="chat-message-header">
              <span className="chat-role">AI Assistant</span>
            </div>
            <div className="chat-message-content chat-typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about the model or request modifications..."
          disabled={isProcessing}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={isProcessing || !input.trim()}
          className="chat-send-btn"
        >
          {isProcessing ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}
