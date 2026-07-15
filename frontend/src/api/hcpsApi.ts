import { apiSlice } from './apiSlice'
import type { HCP, HCPCreate, HCPUpdate } from './types'

export interface ListHcpsParams {
  search?: string
  specialty?: string
  skip?: number
  limit?: number
}

export const hcpsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listHcps: builder.query<HCP[], ListHcpsParams | void>({
      query: (params) => ({ url: 'hcps', params: params ?? undefined }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'HCP' as const, id })),
              { type: 'HCP' as const, id: 'LIST' },
            ]
          : [{ type: 'HCP' as const, id: 'LIST' }],
    }),
    getHcp: builder.query<HCP, string>({
      query: (id) => `hcps/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'HCP', id }],
    }),
    createHcp: builder.mutation<HCP, HCPCreate>({
      query: (body) => ({ url: 'hcps', method: 'POST', body }),
      invalidatesTags: [{ type: 'HCP', id: 'LIST' }],
    }),
    updateHcp: builder.mutation<HCP, { id: string; body: HCPUpdate }>({
      query: ({ id, body }) => ({ url: `hcps/${id}`, method: 'PATCH', body }),
      invalidatesTags: (_result, _error, { id }) => [{ type: 'HCP', id }],
    }),
    deleteHcp: builder.mutation<void, string>({
      query: (id) => ({
        url: `hcps/${id}`,
        method: 'DELETE',
        responseHandler: (response) =>
          response.status === 204
            ? Promise.resolve(undefined)
            : response.json(),
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'HCP', id },
        { type: 'HCP', id: 'LIST' },
      ],
    }),
  }),
})

export const {
  useListHcpsQuery,
  useGetHcpQuery,
  useCreateHcpMutation,
  useUpdateHcpMutation,
  useDeleteHcpMutation,
} = hcpsApi
