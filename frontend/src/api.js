// Talks to the Palate backend. We POST the transcript and read an SSE-formatted
// stream back. Native EventSource can't POST, so we read the fetch body manually.

// Streams a chat reply.
//   onDelta(text)       — called for each text chunk as it arrives
//   onSuggestions(list) — called once (if at all) with proposed user replies
// Returns when the stream completes; throws on transport/stream errors.
export async function streamChat(messages, { onDelta, onSuggestions, signal } = {}) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
    signal,
  })

  if (!res.ok) throw new Error(`Backend returned ${res.status}`)

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''

    for (const evt of events) {
      const line = evt.split('\n').find((l) => l.startsWith('data: '))
      if (!line) continue
      const payload = line.slice(6)
      if (payload === '[DONE]') return

      const data = JSON.parse(payload)
      if (data.error) throw new Error(data.error)
      if (data.delta) onDelta?.(data.delta)
      if (data.suggestions) onSuggestions?.(data.suggestions)
    }
  }
}