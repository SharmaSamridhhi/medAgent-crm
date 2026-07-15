import { configureStore } from '@reduxjs/toolkit'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { apiSlice } from '../../api/apiSlice'
import type { HCP } from '../../api/types'
import HcpAdminPage from './HcpAdminPage'

const BASE_URL = 'http://localhost:8000/api/v1'

let hcps: HCP[] = [
  {
    id: 'hcp-1',
    name: 'Dr. Ada Lovelace',
    specialty: 'Cardiology',
    institution: null,
    contact_info: null,
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'hcp-2',
    name: 'Dr. Ben Okafor',
    specialty: 'Oncology',
    institution: null,
    contact_info: null,
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
  },
]

const server = setupServer(
  http.get(`${BASE_URL}/hcps`, ({ request }) => {
    const url = new URL(request.url)
    const search = (url.searchParams.get('search') ?? '').toLowerCase()
    const matches = search
      ? hcps.filter((hcp) => hcp.name.toLowerCase().includes(search))
      : hcps
    return HttpResponse.json(matches)
  }),
  http.post(`${BASE_URL}/hcps`, async ({ request }) => {
    const body = (await request.json()) as Partial<HCP>
    const created: HCP = {
      id: 'hcp-3',
      name: body.name ?? '',
      specialty: body.specialty ?? null,
      institution: body.institution ?? null,
      contact_info: body.contact_info ?? null,
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
    }
    hcps = [...hcps, created]
    return HttpResponse.json(created, { status: 201 })
  }),
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  hcps = hcps.filter((hcp) => hcp.id !== 'hcp-3')
})
afterAll(() => server.close())

function renderPage() {
  const store = configureStore({
    reducer: { [apiSlice.reducerPath]: apiSlice.reducer },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
  })

  render(
    <Provider store={store}>
      <MemoryRouter>
        <HcpAdminPage />
      </MemoryRouter>
    </Provider>,
  )
}

describe('HcpAdminPage', () => {
  it('renders existing HCPs in a table', async () => {
    renderPage()
    expect(await screen.findByText('Dr. Ada Lovelace')).toBeInTheDocument()
    expect(screen.getByText('Dr. Ben Okafor')).toBeInTheDocument()
    expect(screen.getByText('Cardiology')).toBeInTheDocument()
  })

  it('filters the table by search', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('Dr. Ada Lovelace')

    await user.type(screen.getByLabelText(/^search$/i), 'Ben')

    expect(await screen.findByText('Dr. Ben Okafor')).toBeInTheDocument()
    expect(screen.queryByText('Dr. Ada Lovelace')).not.toBeInTheDocument()
  })

  it('adds a new HCP to the table on create', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('Dr. Ada Lovelace')

    await user.type(screen.getByLabelText('Name'), 'Dr. Chidi Okonkwo')
    await user.type(screen.getByLabelText('Specialty'), 'Neurology')
    await user.click(screen.getByRole('button', { name: /add hcp/i }))

    expect(await screen.findByText('Dr. Chidi Okonkwo')).toBeInTheDocument()
    expect(screen.getByText('Neurology')).toBeInTheDocument()
  })
})
