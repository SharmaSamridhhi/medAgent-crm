import { configureStore } from '@reduxjs/toolkit'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { apiSlice } from './apiSlice'
import { hcpsApi } from './hcpsApi'
import type { HCP } from './types'

const BASE_URL = 'http://localhost:8000/api/v1'

let hcps: HCP[] = []

const server = setupServer(
  http.post(`${BASE_URL}/hcps`, async ({ request }) => {
    const body = (await request.json()) as { name: string; specialty?: string }
    const created: HCP = {
      id: '11111111-1111-1111-1111-111111111111',
      name: body.name,
      specialty: body.specialty ?? null,
      institution: null,
      contact_info: null,
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
    }
    hcps = [created]
    return HttpResponse.json(created, { status: 201 })
  }),
  http.get(`${BASE_URL}/hcps`, () => HttpResponse.json(hcps)),
)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  hcps = []
})
afterAll(() => server.close())

function createTestStore() {
  return configureStore({
    reducer: { [apiSlice.reducerPath]: apiSlice.reducer },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
  })
}

describe('hcpsApi', () => {
  it('creates then lists an HCP as a round trip', async () => {
    const store = createTestStore()

    const createResult = await store.dispatch(
      hcpsApi.endpoints.createHcp.initiate({
        name: 'Dr. Ada Lovelace',
        specialty: 'Cardiology',
      }),
    )
    if (!('data' in createResult) || !createResult.data) {
      throw new Error('createHcp did not return data')
    }
    expect(createResult.data.name).toBe('Dr. Ada Lovelace')

    const listResult = await store.dispatch(
      hcpsApi.endpoints.listHcps.initiate(),
    )
    if (!('data' in listResult) || !listResult.data) {
      throw new Error('listHcps did not return data')
    }
    expect(listResult.data).toHaveLength(1)
    expect(listResult.data[0].name).toBe('Dr. Ada Lovelace')
  })
})
