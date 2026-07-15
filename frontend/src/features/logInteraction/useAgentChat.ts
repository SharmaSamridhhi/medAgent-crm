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

export interface ChatContext {
  hcp?: ActiveHcp | null
  // Set while editing an already-saved interaction (MEDGENT-022) so the
  // agent's edit_interaction tool can resolve it without the rep having
  // to restate which one they mean.
  interactionId?: string | null
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

export function useAgentChat(context: ChatContext | null): UseAgentChatResult {
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

    // The chat endpoint has no dedicated fields for active HCP/interaction
    // context, so it's passed in-band on the first turn of a session only
    // — the displayed message stays clean, only the outgoing payload is
    // augmented (see MEDGENT-020's and MEDGENT-022's implementation notes).
    const contextParts: string[] = []
    if (context?.hcp) {
      contextParts.push(
        `HCP "${context.hcp.name}" (id: ${context.hcp.id}) is selected in the form`,
      )
    }
    if (context?.interactionId) {
      contextParts.push(
        `the rep is editing an already-logged interaction with id ${context.interactionId}`,
      )
    }
    const outgoingMessage =
      !sessionId && contextParts.length > 0
        ? `[Context: ${contextParts.join('; ')}.] ${trimmed}`
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
