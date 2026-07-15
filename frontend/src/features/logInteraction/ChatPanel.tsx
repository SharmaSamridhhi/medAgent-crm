import { useState } from 'react'
import type { FormEvent } from 'react'
import SideEffectCard from './SideEffectCard'
import type { UseAgentChatResult } from './useAgentChat'
import './ChatPanel.css'

interface ChatPanelProps {
  chat: UseAgentChatResult
  onSuggestedFollowUpClick?: (suggestion: string) => void
}

function ChatPanel({ chat, onSuggestedFollowUpClick }: ChatPanelProps) {
  const [draft, setDraft] = useState('')

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = draft
    setDraft('')
    await chat.sendMessage(text)
  }

  // Defaults to accepting the suggestion as a chat turn — the system
  // prompt already tells the agent to treat a verbatim suggested follow-up
  // as a schedule_follow_up request. Callers (e.g. MEDGENT-021's form-side
  // chip) can override this if they need different behavior.
  async function handleSuggestedFollowUpClick(suggestion: string) {
    if (onSuggestedFollowUpClick) {
      onSuggestedFollowUpClick(suggestion)
      return
    }
    await chat.sendMessage(suggestion)
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel__header">
        <h2 className="chat-panel__title">AI Assistant</h2>
        <p className="chat-panel__subtitle">Log interaction via chat</p>
      </div>

      <div className="chat-panel__messages">
        {chat.messages.length === 0 && (
          <p className="chat-panel__placeholder">
            Log interaction details here (e.g., "Met Dr. Smith, discussed
            Product X efficacy, positive sentiment, shared brochure") or ask for
            help.
          </p>
        )}
        {chat.messages.map((message) => (
          <div
            key={message.id}
            className={`chat-panel__message chat-panel__message--${message.role}`}
          >
            <p>{message.text}</p>
            {message.sideEffects?.map((effect, index) => (
              <SideEffectCard
                key={`${message.id}-${effect.tool}-${index}`}
                effect={effect}
                onSuggestedFollowUpClick={handleSuggestedFollowUpClick}
              />
            ))}
          </div>
        ))}
        {chat.isLoading && (
          <p className="chat-panel__typing" aria-live="polite">
            AI Assistant is typing…
          </p>
        )}
        {chat.error && (
          <p role="alert" className="chat-panel__error">
            {chat.error}
          </p>
        )}
      </div>

      <form className="chat-panel__composer" onSubmit={handleSubmit}>
        <input
          type="text"
          value={draft}
          placeholder="Describe interaction..."
          onChange={(event) => setDraft(event.target.value)}
        />
        <button type="submit" disabled={chat.isLoading || !draft.trim()}>
          ⚠ Log
        </button>
      </form>
    </div>
  )
}

export default ChatPanel
