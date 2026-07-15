import { configureStore } from '@reduxjs/toolkit'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
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

const existingInteraction: Interaction = {
  id: 'int-existing',
  hcp_id: 'hcp-1',
  rep_id: '00000000-0000-0000-0000-000000000001',
  interaction_type: 'Meeting',
  occurred_at: '2026-07-10T09:00:00Z',
  attendees: [],
  topics_discussed: 'Discussed CardioX dosing',
  materials_shared: [],
  samples_distributed: [],
  sentiment: 'neutral',
  outcomes: 'Agreed to review data',
  follow_up_notes: null,
  source: 'form',
  compliance_flags: [],
  has_compliance_flags: false,
  is_active: true,
  created_at: '2026-07-10T09:00:00Z',
  updated_at: '2026-07-10T09:00:00Z',
}

let chatResponseQueue: Array<() => Response | Promise<Response>> = []
let lastChatRequestBody: { message: string; session_id?: string } | null = null
let patchedInteraction: Interaction = existingInteraction

const server = setupServer(
  http.get(`${BASE_URL}/hcps`, ({ request }) => {
    const url = new URL(request.url)
    const search = (url.searchParams.get('search') ?? '').toLowerCase()
    const matches = [hcpAda].filter((hcp) =>
      hcp.name.toLowerCase().includes(search),
    )
    return HttpResponse.json(matches)
  }),
  http.get(`${BASE_URL}/hcps/:id`, ({ params }) =>
    params.id === hcpAda.id
      ? HttpResponse.json(hcpAda)
      : new HttpResponse(null, { status: 404 }),
  ),
  http.get(`${BASE_URL}/interactions`, () =>
    HttpResponse.json([patchedInteraction]),
  ),
  http.patch(`${BASE_URL}/interactions/:id`, async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    patchedInteraction = {
      ...patchedInteraction,
      id: params.id as string,
      ...body,
    } as Interaction
    return HttpResponse.json(patchedInteraction)
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
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  chatResponseQueue = []
  lastChatRequestBody = null
  patchedInteraction = existingInteraction
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
      <MemoryRouter>
        <LogInteractionScreen />
      </MemoryRouter>
    </Provider>,
  )
}

async function selectHcp(user: ReturnType<typeof userEvent.setup>) {
  const hcpInput = screen.getByRole('combobox', { name: /hcp name/i })
  await user.type(hcpInput, 'Ada')
  const option = await screen.findByRole('button', {
    name: /Dr\. Ada Lovelace/i,
  })
  await user.click(option)
}

describe('Edit Interaction flow', () => {
  it('lists recent interactions for the selected HCP and loads one for direct editing', async () => {
    const user = userEvent.setup()
    renderScreen()
    await selectHcp(user)

    const editButton = await screen.findByRole('button', { name: /^edit$/i })
    await user.click(editButton)

    expect(await screen.findByLabelText(/^outcomes$/i)).toHaveValue(
      'Agreed to review data',
    )
    expect(
      screen.getByRole('button', { name: /save changes/i }),
    ).toBeInTheDocument()
  })

  it('shows a before/after confirmation after a direct form edit', async () => {
    const user = userEvent.setup()
    renderScreen()
    await selectHcp(user)
    const editButton = await screen.findByRole('button', { name: /^edit$/i })
    await user.click(editButton)

    const outcomesField = await screen.findByLabelText(/^outcomes$/i)
    await user.clear(outcomesField)
    await user.type(outcomesField, 'Placed a trial order')

    await user.click(screen.getByRole('button', { name: /save changes/i }))

    const confirmation = (
      await screen.findByText(/here's what changed/i)
    ).closest('[role="status"]') as HTMLElement
    expect(
      within(confirmation).getByText(/agreed to review data/i),
    ).toBeInTheDocument()
    expect(
      within(confirmation).getByText(/placed a trial order/i),
    ).toBeInTheDocument()
  })

  it('scopes a conversational edit to the loaded interaction and applies the result to the form', async () => {
    const user = userEvent.setup()
    renderScreen()
    await selectHcp(user)
    const editButton = await screen.findByRole('button', { name: /^edit$/i })
    await user.click(editButton)

    queueChatReply({
      session_id: 'session-edit-1',
      reply: 'Updated the outcome for that interaction.',
      side_effects: [
        {
          tool: 'edit_interaction',
          output: {
            status: 'updated',
            message: 'Updated.',
            interaction_id: 'int-existing',
            changes: [
              {
                field: 'outcomes',
                old_value: 'Agreed to review data',
                new_value: 'Placed a trial order via chat',
              },
            ],
            candidate_interactions: [],
          },
        },
      ],
    })

    const chatInput = screen.getByPlaceholderText(/describe interaction/i)
    await user.type(chatInput, 'Actually she placed a trial order')
    await user.click(screen.getByRole('button', { name: /⚠ log/i }))

    expect(lastChatRequestBody?.message).toContain(
      'editing an already-logged interaction with id int-existing',
    )
    expect(await screen.findByLabelText(/^outcomes$/i)).toHaveValue(
      'Placed a trial order via chat',
    )
    expect(screen.getByText(/✓ Interaction updated/i)).toBeInTheDocument()
  })

  it('surfaces re-screened compliance flags after a direct edit', async () => {
    const user = userEvent.setup()
    renderScreen()
    await selectHcp(user)
    const editButton = await screen.findByRole('button', { name: /^edit$/i })
    await user.click(editButton)

    const topicsField = await screen.findByLabelText(/topics discussed/i)
    await user.clear(topicsField)
    await user.type(topicsField, 'Said CardioX cures everything')

    patchedInteraction = {
      ...existingInteraction,
      topics_discussed: 'Said CardioX cures everything',
      has_compliance_flags: true,
      compliance_flags: [
        {
          category: 'off_label_claim',
          excerpt: 'cures everything',
          rationale: 'Discusses an unapproved indication.',
        },
      ],
    }

    await user.click(screen.getByRole('button', { name: /save changes/i }))

    const alerts = await screen.findAllByRole('alert')
    expect(
      alerts.some((alert) => /off label claim/i.test(alert.textContent ?? '')),
    ).toBe(true)
  })
})
