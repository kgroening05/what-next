import { useState, useRef, useEffect } from 'react'
import { streamChat } from './api'
import SuggestionChips from './SuggestionChips'
import './App.css'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight)
  }, [messages])

  async function send(textOverride) {
    const text = (textOverride ?? input).trim()
    if (!text || streaming) return

    const history = [...messages, { role: 'user', content: text }]
    setMessages([...history, { role: 'assistant', content: '' }])
    if (textOverride === undefined) setInput('')
    setStreaming(true)

    try {
      await streamChat(history, {
        onDelta: (delta) => {
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            next[next.length - 1] = { ...last, content: last.content + delta }
            return next
          })
        },
        onSuggestions: (suggestions) => {
          setMessages((prev) => {
            const next = [...prev]
            next[next.length - 1] = { ...next[next.length - 1], suggestions }
            return next
          })
        },
      })
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev]
        next[next.length - 1] = { role: 'assistant', content: `⚠️ ${err.message}` }
        return next
      })
    } finally {
      setStreaming(false)
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Palate</h1>
        <p>Tell me what you're in the mood for.</p>
      </header>

      <div className="messages" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="empty">
            e.g. "I want a cozy anime like Mushishi and Aria" or
            "instrumental music for deep focus, but not lofi"
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <div className="bubble">
              {m.content || (streaming && i === messages.length - 1 ? '…' : '')}
            </div>
          </div>
        ))}

        {!streaming &&
          messages.at(-1)?.role === 'assistant' &&
          messages.at(-1)?.suggestions && (
            <SuggestionChips
              suggestions={messages.at(-1).suggestions}
              onInsert={setInput}
              onSend={send}
            />
          )}
      </div>

      <div className="composer">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="What are you looking for?"
          rows={2}
        />
        <button onClick={() => send()} disabled={streaming || !input.trim()}>
          {streaming ? '…' : 'Send'}
        </button>
      </div>
    </div>
  )
}
