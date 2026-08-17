export default function SuggestionChips({ suggestions, onInsert, onSend }) {
  return (
    <div className="chips">
      {suggestions.map((text, i) => (
        <div key={i} className="chip">
          <button
            className="chip-label"
            onClick={() => onInsert(text)}
            title="Put in composer to edit"
          >
            {text}
          </button>
          <button
            className="chip-send"
            onClick={() => onSend(text)}
            aria-label={`Send: ${text}`}
            title="Send now"
          >
            ↵
          </button>
        </div>
      ))}
    </div>
  )
}