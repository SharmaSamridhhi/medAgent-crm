import { configureStore } from '@reduxjs/toolkit'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { Provider } from 'react-redux'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { apiSlice } from '../../api/apiSlice'
import ChatPanel from './ChatPanel'
import { useAgentChat, type ActiveHcp } from './useAgentChat'

const BASE_URL = 'http://localhost:8000/api/v1'

let responseQueue: Array<() => Response | Promise<Response>> = []

const server = setupServer(
  http.post(`${BASE_URL}/agent/chat`, async () => {
    const next = responseQueue.shift()
    if (!next) {
      throw new Error('no mocked response queued')
    }
    return next()
  }),
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  responseQueue = []
})
afterAll(() => server.close())

function queueJson<T extends Record<string, unknown>>(body: T) {
  responseQueue.push(() => HttpResponse.json(body, { status: 200 }))
}

function queueError(status: number) {
  responseQueue.push(() => new HttpResponse(null, { status }))
}

const activeHcp: ActiveHcp = { id: 'hcp-1', name: 'Dr. Ada Lovelace' }

function renderChatPanel() {
  const store = configureStore({
    reducer: { [apiSlice.reducerPath]: apiSlice.reducer },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
  })

  function Harness() {
    const chat = useAgentChat({ hcp: activeHcp })
    return <ChatPanel chat={chat} />
  }

  render(
    <Provider store={store}>
      <Harness />
    </Provider>,
  )
}

async function sendMessage(
  user: ReturnType<typeof userEvent.setup>,
  text: string,
) {
  const input = screen.getByPlaceholderText(/describe interaction/i)
  await user.type(input, text)
  await user.click(screen.getByRole('button', { name: /log/i }))
}

describe('ChatPanel', () => {
  it('sends a message and renders the reply with a structured side effect', async () => {
    const user = userEvent.setup()
    queueJson({
      session_id: 'session-1',
      reply: 'Logged your call with Dr. Ada Lovelace.',
      side_effects: [
        {
          tool: 'log_interaction',
          output: {
            status: 'created',
            message: 'Logged.',
            interaction_id: 'int-1',
            hcp_id: 'hcp-1',
            interaction_type: 'Call',
            occurred_at: '2026-07-20T14:30:00Z',
            attendees: [],
            topics_discussed: 'Discussed CardioX',
            materials_shared: [],
            samples_distributed: [],
            sentiment: 'positive',
            outcomes: null,
            suggested_follow_ups: ['Schedule follow-up meeting in 2 weeks'],
            compliance_flags: [],
            candidate_hcps: [],
          },
        },
      ],
    })

    renderChatPanel()
    await sendMessage(user, 'Met Dr. Lovelace, discussed CardioX')

    expect(await screen.findByText(/logged your call/i)).toBeInTheDocument()
    expect(screen.getByText(/interaction logged/i)).toBeInTheDocument()
    expect(
      screen.getByText(/schedule follow-up meeting in 2 weeks/i),
    ).toBeInTheDocument()
  })

  it('supports a clarification round-trip across two turns', async () => {
    const user = userEvent.setup()
    queueJson({
      session_id: 'session-2',
      reply: "I couldn't find that HCP on file — could you confirm the name?",
      side_effects: [],
    })
    queueJson({
      session_id: 'session-2',
      reply: 'Logged your call with Dr. Ada Lovelace.',
      side_effects: [],
    })

    renderChatPanel()
    await sendMessage(user, 'Met with the doctor')
    expect(
      await screen.findByText(/could you confirm the name/i),
    ).toBeInTheDocument()

    await sendMessage(user, 'Dr. Ada Lovelace')
    expect(await screen.findByText(/logged your call/i)).toBeInTheDocument()
  })

  it('sends a chat message when a suggested follow-up chip is clicked', async () => {
    const user = userEvent.setup()
    queueJson({
      session_id: 'session-3',
      reply: 'Logged.',
      side_effects: [
        {
          tool: 'log_interaction',
          output: {
            status: 'created',
            message: 'Logged.',
            interaction_id: 'int-1',
            hcp_id: 'hcp-1',
            interaction_type: 'Call',
            occurred_at: '2026-07-20T14:30:00Z',
            attendees: [],
            topics_discussed: null,
            materials_shared: [],
            samples_distributed: [],
            sentiment: null,
            outcomes: null,
            suggested_follow_ups: ['Schedule follow-up meeting in 2 weeks'],
            compliance_flags: [],
            candidate_hcps: [],
          },
        },
      ],
    })
    queueJson({
      session_id: 'session-3',
      reply: 'Scheduled a follow-up with Dr. Ada Lovelace for 2026-08-03.',
      side_effects: [
        {
          tool: 'schedule_follow_up',
          output: {
            status: 'scheduled',
            message: 'Scheduled.',
            follow_up_id: 'fu-1',
            hcp_id: 'hcp-1',
            due_date: '2026-08-03',
            note: 'Schedule follow-up meeting in 2 weeks',
            candidate_hcps: [],
          },
        },
      ],
    })

    renderChatPanel()
    await sendMessage(user, 'Met with Dr. Lovelace')
    const chip = await screen.findByRole('button', {
      name: /schedule follow-up meeting in 2 weeks/i,
    })
    await user.click(chip)
    expect(await screen.findByText(/follow-up scheduled/i)).toBeInTheDocument()
  })

  it("shows an error without losing the rep's message from the transcript", async () => {
    queueError(500)
    const user = userEvent.setup()
    renderChatPanel()
    await sendMessage(user, 'Met with Dr. Lovelace')
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(screen.getByText(/met with dr\. lovelace/i)).toBeInTheDocument()
  })
})
