import { configureStore } from '@reduxjs/toolkit'
import { apiSlice } from '../api/apiSlice'
import logInteractionDraftReducer from '../features/logInteraction/logInteractionDraftSlice'

export const store = configureStore({
  reducer: {
    [apiSlice.reducerPath]: apiSlice.reducer,
    logInteractionDraft: logInteractionDraftReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
