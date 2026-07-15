import { useState } from 'react'
import { useSendChatMessageMutation } from '../../api/agentApi'
import type { ToolSideEffect } from '../../api/types'

export interface ChatMessage {
  id: string
  role: 'rep' | 'agent'
  text: string
  sideEffects?: ToolSideEffect[]
}

export interface ActiveHcp {
  id: string
  name: string
}

export interface UseAgentChatResult {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sessionId: string | null
  sendMessage: (text: string) => Promise<void>
}

let messageIdCounter = 0
function nextMessageId(): string {
  messageIdCounter += 1
  return `msg-${messageIdCounter}`
}

export function useAgentChat(activeHcp: ActiveHcp | null): UseAgentChatResult {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [error, setError] = useState<string | null>(null)
  const [sendChatMessage, { isLoading }] = useSendChatMessageMutation()

  async function sendMessage(text: string) {
    const trimmed = text.trim()
    if (!trimmed) {
      return
    }

    setError(null)
    setMessages((prev) => [
      ...prev,
      { id: nextMessageId(), role: 'rep', text: trimmed },
    ])

    // The chat endpoint has no dedicated "active HCP" field, so context is
    // passed in-band on the first turn of a session — the displayed
    // message stays clean, only the outgoing payload is augmented.
    const outgoingMessage =
      !sessionId && activeHcp
        ? `[Context: the rep currently has HCP "${activeHcp.name}" (id: ${activeHcp.id}) selected in the form.] ${trimmed}`
        : trimmed

    try {
      const response = await sendChatMessage({
        message: outgoingMessage,
        session_id: sessionId ?? undefined,
      }).unwrap()
      setSessionId(response.session_id)
      setMessages((prev) => [
        ...prev,
        {
          id: nextMessageId(),
          role: 'agent',
          text: response.reply,
          sideEffects: response.side_effects,
        },
      ])
    } catch {
      setError("Couldn't reach the AI Assistant. Please try again.")
    }
  }

  return { messages, isLoading, error, sessionId, sendMessage }
}
