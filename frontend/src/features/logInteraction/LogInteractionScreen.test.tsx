import { configureStore } from '@reduxjs/toolkit'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { Provider } from 'react-redux'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { apiSlice } from '../../api/apiSlice'
import type { HCP, Interaction } from '../../api/types'
import LogInteractionScreen from './LogInteractionScreen'
import logInteractionDraftReducer from './logInteractionDraftSlice'

const BASE_URL = 'http://localhost:8000/api/v1'

const hcpAda: HCP = {
  id: 'hcp-1',
  name: 'Dr. Ada Lovelace',
  specialty: 'Cardiology',
  institution: null,
  contact_info: null,
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
}

const hcpBen: HCP = {
  id: 'hcp-2',
  name: 'Dr. Ben Okafor',
  specialty: 'Oncology',
  institution: null,
  contact_info: null,
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
}

const allHcps = [hcpAda, hcpBen]

let chatResponseQueue: Array<() => Response | Promise<Response>> = []
let lastChatRequestBody: { message: string; session_id?: string } | null = null

const server = setupServer(
  http.get(`${BASE_URL}/hcps`, ({ request }) => {
    const url = new URL(request.url)
    const search = (url.searchParams.get('search') ?? '').toLowerCase()
    const matches = allHcps.filter((hcp) =>
      hcp.name.toLowerCase().includes(search),
    )
    return HttpResponse.json(matches)
  }),
  http.get(`${BASE_URL}/hcps/:id`, ({ params }) => {
    const hcp = allHcps.find((candidate) => candidate.id === params.id)
    return hcp
      ? HttpResponse.json(hcp)
      : new HttpResponse(null, { status: 404 })
  }),
  http.post(`${BASE_URL}/agent/chat`, async ({ request }) => {
    lastChatRequestBody = (await request.json()) as {
      message: string
      session_id?: string
    }
    const next = chatResponseQueue.shift()
    if (!next) {
      throw new Error('no mocked chat response queued')
    }
    return next()
  }),
  http.patch(`${BASE_URL}/interactions/:id`, async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    const updated: Interaction = {
      id: params.id as string,
      hcp_id: (body.hcp_id as string) ?? hcpAda.id,
      rep_id: '00000000-0000-0000-0000-000000000001',
      interaction_type: (body.interaction_type as string) ?? 'Call',
      occurred_at: (body.occurred_at as string) ?? '2026-07-20T14:30:00Z',
      attendees: (body.attendees as string[]) ?? [],
      topics_discussed: (body.topics_discussed as string | null) ?? null,
      materials_shared: (body.materials_shared as string[]) ?? [],
      samples_distributed: (body.samples_distributed as string[]) ?? [],
      sentiment: (body.sentiment as Interaction['sentiment']) ?? null,
      outcomes: (body.outcomes as string | null) ?? null,
      follow_up_notes: (body.follow_up_notes as string | null) ?? null,
      source: 'chat',
      compliance_flags: [],
      has_compliance_flags: false,
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    }
    return HttpResponse.json(updated)
  }),
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  chatResponseQueue = []
  lastChatRequestBody = null
})
afterAll(() => server.close())

function queueChatReply(body: Record<string, unknown>) {
  chatResponseQueue.push(() => HttpResponse.json(body, { status: 200 }))
}

function renderScreen() {
  const store = configureStore({
    reducer: {
      [apiSlice.reducerPath]: apiSlice.reducer,
      logInteractionDraft: logInteractionDraftReducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
  })

  render(
    <Provider store={store}>
      <LogInteractionScreen />
    </Provider>,
  )
}

async function sendChatMessage(
  user: ReturnType<typeof userEvent.setup>,
  text: string,
) {
  const input = screen.getByPlaceholderText(/describe interaction/i)
  await user.type(input, text)
  await user.click(screen.getByRole('button', { name: /⚠ log/i }))
}

describe('LogInteractionScreen', () => {
  it('populates the form from a chat extraction, lets the rep edit, and saves in place', async () => {
    const user = userEvent.setup()
    queueChatReply({
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
            suggested_follow_ups: [],
            compliance_flags: [],
            candidate_hcps: [],
          },
        },
      ],
    })

    renderScreen()
    await sendChatMessage(user, 'Met Dr. Lovelace, discussed CardioX')

    expect(await screen.findByLabelText(/topics discussed/i)).toHaveValue(
      'Discussed CardioX',
    )
    expect(screen.getByRole('radio', { name: /positive/i })).toBeChecked()
    expect(
      await screen.findByRole('combobox', { name: /hcp name/i }),
    ).toHaveValue('Dr. Ada Lovelace')

    const outcomesField = screen.getByLabelText(/^outcomes$/i)
    await user.type(outcomesField, 'Agreed to a follow-up call')

    const saveButton = screen.getByRole('button', { name: /save changes/i })
    await user.click(saveButton)

    expect(await screen.findByText(/interaction saved/i)).toBeInTheDocument()
  })

  it('reflects a form HCP selection as chat context on the first turn', async () => {
    const user = userEvent.setup()
    queueChatReply({
      session_id: 'session-2',
      reply: 'Got it.',
      side_effects: [],
    })

    renderScreen()
    const hcpInput = screen.getByRole('combobox', { name: /hcp name/i })
    await user.type(hcpInput, 'Ada')
    const option = await screen.findByRole('button', {
      name: /Dr\. Ada Lovelace/i,
    })
    await user.click(option)

    await sendChatMessage(user, 'Discussed CardioX efficacy')

    expect(lastChatRequestBody?.message).toContain('Dr. Ada Lovelace')
    expect(lastChatRequestBody?.message).toContain('hcp-1')
    expect(lastChatRequestBody?.message).toContain('Discussed CardioX efficacy')
  })

  it("syncs the chat's resolved HCP back into the form picker", async () => {
    const user = userEvent.setup()
    queueChatReply({
      session_id: 'session-3',
      reply: 'Dr. Ben Okafor has 3 prior interactions on file.',
      side_effects: [
        {
          tool: 'retrieve_hcp_history',
          output: {
            status: 'found',
            message: 'Found history.',
            hcp_id: 'hcp-2',
            hcp_name: 'Dr. Ben Okafor',
            specialty: 'Oncology',
            institution: null,
            interactions: [],
            summary: 'Frequent, positive interactions.',
            candidate_hcps: [],
          },
        },
      ],
    })

    renderScreen()
    await sendChatMessage(user, 'Who is Dr. Ben Okafor?')

    expect(
      await screen.findByRole('combobox', { name: /hcp name/i }),
    ).toHaveValue('Dr. Ben Okafor')
  })

  it('creates a real follow-up when a suggested follow-up chip is clicked', async () => {
    const user = userEvent.setup()
    queueChatReply({
      session_id: 'session-4',
      reply: 'Logged.',
      side_effects: [
        {
          tool: 'log_interaction',
          output: {
            status: 'created',
            message: 'Logged.',
            interaction_id: 'int-2',
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
    queueChatReply({
      session_id: 'session-4',
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

    renderScreen()
    await sendChatMessage(user, 'Met Dr. Lovelace')

    const chips = await screen.findAllByRole('button', {
      name: /schedule follow-up meeting in 2 weeks/i,
    })
    await user.click(chips[0])

    expect(await screen.findByText(/follow-up scheduled/i)).toBeInTheDocument()
  })

  it('renders compliance flags consistently at the screen level', async () => {
    const user = userEvent.setup()
    queueChatReply({
      session_id: 'session-5',
      reply: 'Logged your call with Dr. Ada Lovelace.',
      side_effects: [
        {
          tool: 'log_interaction',
          output: {
            status: 'created',
            message: 'Logged.',
            interaction_id: 'int-3',
            hcp_id: 'hcp-1',
            interaction_type: 'Call',
            occurred_at: '2026-07-20T14:30:00Z',
            attendees: [],
            topics_discussed: 'Mentioned off-label use',
            materials_shared: [],
            samples_distributed: [],
            sentiment: null,
            outcomes: null,
            suggested_follow_ups: [],
            compliance_flags: [
              {
                category: 'off_label_claim',
                excerpt: 'off-label use',
                rationale: 'Discusses an unapproved indication.',
              },
            ],
            candidate_hcps: [],
          },
        },
      ],
    })

    renderScreen()
    await sendChatMessage(user, 'Met Dr. Lovelace, mentioned off-label use')

    const alerts = await screen.findAllByRole('alert')
    expect(
      alerts.some((alert) => /off label claim/i.test(alert.textContent ?? '')),
    ).toBe(true)
  })
})
