import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type {
  ComplianceFlag,
  InteractionSource,
  LogInteractionOutput,
} from '../../api/types'
import { createEmptyDraft, type InteractionDraft } from './draft'

export interface LogInteractionDraftState {
  draft: InteractionDraft
  interactionId: string | null
  source: InteractionSource
  suggestedFollowUps: string[]
  complianceFlags: ComplianceFlag[]
}

function initialState(): LogInteractionDraftState {
  return {
    draft: createEmptyDraft(),
    interactionId: null,
    source: 'form',
    suggestedFollowUps: [],
    complianceFlags: [],
  }
}

const logInteractionDraftSlice = createSlice({
  name: 'logInteractionDraft',
  initialState: initialState(),
  reducers: {
    draftChanged(state, action: PayloadAction<InteractionDraft>) {
      state.draft = action.payload
    },
    hcpContextResolved(
      state,
      action: PayloadAction<{ id: string; name: string }>,
    ) {
      state.draft.hcp_id = action.payload.id
      state.draft.hcp_name = action.payload.name
    },
    hcpNameResolved(
      state,
      action: PayloadAction<{ id: string; name: string }>,
    ) {
      if (state.draft.hcp_id === action.payload.id) {
        state.draft.hcp_name = action.payload.name
      }
    },
    chatLogInteractionApplied(
      state,
      action: PayloadAction<LogInteractionOutput>,
    ) {
      const output = action.payload
      if (output.status !== 'created') {
        return
      }
      state.draft = {
        ...state.draft,
        hcp_id: output.hcp_id ?? state.draft.hcp_id,
        interaction_type:
          output.interaction_type ?? state.draft.interaction_type,
        attendees: output.attendees,
        topics_discussed: output.topics_discussed ?? '',
        materials_shared: output.materials_shared,
        samples_distributed: output.samples_distributed,
        sentiment: output.sentiment,
        outcomes: output.outcomes ?? '',
      }
      if (output.occurred_at) {
        const occurredAt = new Date(output.occurred_at)
        state.draft.date = occurredAt.toISOString().slice(0, 10)
        state.draft.time = occurredAt.toISOString().slice(11, 16)
      }
      state.interactionId = output.interaction_id
      state.source = 'chat'
      state.suggestedFollowUps = output.suggested_follow_ups
      state.complianceFlags = output.compliance_flags
    },
    draftLoaded(
      state,
      action: PayloadAction<{
        draft: InteractionDraft
        interactionId: string | null
        source: InteractionSource
        complianceFlags?: ComplianceFlag[]
      }>,
    ) {
      state.draft = action.payload.draft
      state.interactionId = action.payload.interactionId
      state.source = action.payload.source
      state.suggestedFollowUps = []
      state.complianceFlags = action.payload.complianceFlags ?? []
    },
    draftReset() {
      return initialState()
    },
  },
})

export const {
  draftChanged,
  hcpContextResolved,
  hcpNameResolved,
  chatLogInteractionApplied,
  draftLoaded,
  draftReset,
} = logInteractionDraftSlice.actions

export default logInteractionDraftSlice.reducer
