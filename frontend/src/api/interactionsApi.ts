import { apiSlice } from './apiSlice'
import type { Interaction, InteractionCreate, InteractionUpdate } from './types'

export interface ListInteractionsParams {
  hcp_id?: string
  rep_id?: string
  occurred_from?: string
  occurred_to?: string
  skip?: number
  limit?: number
}

export const interactionsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listInteractions: builder.query<
      Interaction[],
      ListInteractionsParams | void
    >({
      query: (params) => ({ url: 'interactions', params: params ?? undefined }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: 'Interaction' as const,
                id,
              })),
              { type: 'Interaction' as const, id: 'LIST' },
            ]
          : [{ type: 'Interaction' as const, id: 'LIST' }],
    }),
    getInteraction: builder.query<Interaction, string>({
      query: (id) => `interactions/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'Interaction', id }],
    }),
    createInteraction: builder.mutation<Interaction, InteractionCreate>({
      query: (body) => ({ url: 'interactions', method: 'POST', body }),
      // Creating an interaction also affects the owning HCP's history view.
      invalidatesTags: (result) => [
        { type: 'Interaction', id: 'LIST' },
        ...(result ? [{ type: 'HCP' as const, id: result.hcp_id }] : []),
      ],
    }),
    updateInteraction: builder.mutation<
      Interaction,
      { id: string; body: InteractionUpdate }
    >({
      query: ({ id, body }) => ({
        url: `interactions/${id}`,
        method: 'PATCH',
        body,
      }),
      invalidatesTags: (result, _error, { id }) => [
        { type: 'Interaction', id },
        ...(result ? [{ type: 'HCP' as const, id: result.hcp_id }] : []),
      ],
    }),
    deleteInteraction: builder.mutation<void, string>({
      query: (id) => ({
        url: `interactions/${id}`,
        method: 'DELETE',
        responseHandler: (response) =>
          response.status === 204
            ? Promise.resolve(undefined)
            : response.json(),
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'Interaction', id },
        { type: 'Interaction', id: 'LIST' },
      ],
    }),
  }),
})

export const {
  useListInteractionsQuery,
  useGetInteractionQuery,
  useCreateInteractionMutation,
  useUpdateInteractionMutation,
  useDeleteInteractionMutation,
} = interactionsApi
