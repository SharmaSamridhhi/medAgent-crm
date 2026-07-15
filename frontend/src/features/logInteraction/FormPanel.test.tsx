import { configureStore } from '@reduxjs/toolkit'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { useState } from 'react'
import { Provider } from 'react-redux'
import {
  afterAll,
  afterEach,
  beforeAll,
  describe,
  expect,
  it,
  vi,
} from 'vitest'
import { apiSlice } from '../../api/apiSlice'
import type { HCP, Interaction } from '../../api/types'
import { createEmptyDraft, type InteractionDraft } from './draft'
import FormPanel from './FormPanel'

const BASE_URL = 'http://localhost:8000/api/v1'

const testHcp: HCP = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Dr. Ada Lovelace',
  specialty: 'Cardiology',
  institution: null,
  contact_info: null,
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
}

let createInteractionStatus = 201

const server = setupServer(
  http.get(`${BASE_URL}/hcps`, ({ request }) => {
    const url = new URL(request.url)
    const search = (url.searchParams.get('search') ?? '').toLowerCase()
    const matches =
      search && testHcp.name.toLowerCase().includes(search) ? [testHcp] : []
    return HttpResponse.json(matches)
  }),
  http.post(`${BASE_URL}/interactions`, async ({ request }) => {
    if (createInteractionStatus !== 201) {
      return new HttpResponse(null, { status: createInteractionStatus })
    }
    const body = (await request.json()) as Record<string, unknown>
    const created: Interaction = {
      id: '22222222-2222-2222-2222-222222222222',
      hcp_id: body.hcp_id as string,
      rep_id: '00000000-0000-0000-0000-000000000001',
      interaction_type: body.interaction_type as string,
      occurred_at: body.occurred_at as string,
      attendees: (body.attendees as string[]) ?? [],
      topics_discussed: (body.topics_discussed as string | null) ?? null,
      materials_shared: (body.materials_shared as string[]) ?? [],
      samples_distributed: (body.samples_distributed as string[]) ?? [],
      sentiment: (body.sentiment as Interaction['sentiment']) ?? null,
      outcomes: (body.outcomes as string | null) ?? null,
      follow_up_notes: (body.follow_up_notes as string | null) ?? null,
      source: 'form',
      compliance_flags: [],
      has_compliance_flags: false,
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    }
    return HttpResponse.json(created, { status: 201 })
  }),
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  createInteractionStatus = 201
})
afterAll(() => server.close())

function renderFormPanel(
  props: Partial<React.ComponentProps<typeof FormPanel>> = {},
) {
  const store = configureStore({
    reducer: { [apiSlice.reducerPath]: apiSlice.reducer },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
  })

  function Harness() {
    const [value, setValue] = useState<InteractionDraft>(createEmptyDraft())
    return <FormPanel value={value} onChange={setValue} {...props} />
  }

  render(
    <Provider store={store}>
      <Harness />
    </Provider>,
  )
}

async function selectHcp(user: ReturnType<typeof userEvent.setup>) {
  const input = screen.getByRole('combobox', { name: /hcp name/i })
  await user.type(input, 'Ada')
  const option = await screen.findByRole('button', {
    name: /Dr\. Ada Lovelace/i,
  })
  await user.click(option)
}

function fillDateAndTime() {
  fireEvent.change(screen.getByLabelText(/^date$/i), {
    target: { value: '2026-07-20' },
  })
  fireEvent.change(screen.getByLabelText(/^time$/i), {
    target: { value: '14:30' },
  })
}

describe('FormPanel', () => {
  it('lets the rep search for and select an HCP', async () => {
    const user = userEvent.setup()
    renderFormPanel()
    await selectHcp(user)
    expect(screen.getByRole('combobox', { name: /hcp name/i })).toHaveValue(
      'Dr. Ada Lovelace',
    )
  })

  it('shows validation errors when required fields are missing', async () => {
    const user = userEvent.setup()
    renderFormPanel()
    await user.click(screen.getByRole('button', { name: /log interaction/i }))
    expect(
      await screen.findByText(/select an hcp from the search results/i),
    ).toBeInTheDocument()
  })

  it('submits successfully and reports the created interaction', async () => {
    const user = userEvent.setup()
    const onSaved = vi.fn()
    renderFormPanel({ onSaved })
    await selectHcp(user)
    fillDateAndTime()
    await user.click(screen.getByRole('button', { name: /log interaction/i }))
    expect(await screen.findByText(/interaction saved/i)).toBeInTheDocument()
    expect(onSaved).toHaveBeenCalledTimes(1)
  })

  it('shows an error and preserves entered data on network failure', async () => {
    createInteractionStatus = 500
    const user = userEvent.setup()
    renderFormPanel()
    await selectHcp(user)
    fillDateAndTime()
    await user.type(
      screen.getByLabelText(/topics discussed/i),
      'Discussed CardioX efficacy',
    )
    await user.click(screen.getByRole('button', { name: /log interaction/i }))
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(screen.getByLabelText(/topics discussed/i)).toHaveValue(
      'Discussed CardioX efficacy',
    )
  })
})
