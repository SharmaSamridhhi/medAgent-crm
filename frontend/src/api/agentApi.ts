import { apiSlice } from './apiSlice'
import type { ChatRequest, ChatResponse } from './types'

export const agentApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    sendChatMessage: builder.mutation<ChatResponse, ChatRequest>({
      query: (body) => ({ url: 'agent/chat', method: 'POST', body }),
      // The agent's tools can create/edit interactions and follow-ups,
      // so a chat turn may change data any HCP/Interaction view depends on.
      invalidatesTags: ['HCP', 'Interaction'],
    }),
  }),
})

export const { useSendChatMessageMutation } = agentApi
