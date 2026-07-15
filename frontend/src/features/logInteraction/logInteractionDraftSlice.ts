import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type {
  ComplianceFlag,
  EditInteractionOutput,
  InteractionSource,
  LogInteractionOutput,
} from '../../api/types'
import { createEmptyDraft, type InteractionDraft } from './draft'

export interface LogInteractionDraftState {
  draft: InteractionDraft
  // Snapshot of the draft as last known to be saved server-side — the
  // "before" half of the before/after edit confirmation (MEDGENT-022).
  // null until something has actually been saved/loaded this session.
  originalDraft: InteractionDraft | null
  interactionId: string | null
  source: InteractionSource
  suggestedFollowUps: string[]
  complianceFlags: ComplianceFlag[]
}

function initialState(): LogInteractionDraftState {
  return {
    draft: createEmptyDraft(),
    originalDraft: null,
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
      state.originalDraft = state.draft
    },
    chatEditInteractionApplied(
      state,
      action: PayloadAction<EditInteractionOutput>,
    ) {
      const output = action.payload
      if (output.status !== 'updated' || output.changes.length === 0) {
        return
      }
      state.originalDraft = state.draft
      // FieldChange.field is one of edit_interaction's `_EDITABLE_FIELDS`
      // on the backend, which is exactly InteractionDraft's own field
      // names (see MEDGENT-019's technical details) — safe to index by.
      const nextDraft: Record<string, unknown> = { ...state.draft }
      for (const change of output.changes) {
        nextDraft[change.field] = change.new_value
      }
      state.draft = nextDraft as unknown as InteractionDraft
      if (output.interaction_id) {
        state.interactionId = output.interaction_id
      }
      state.source = 'chat'
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
      state.originalDraft = action.payload.draft
      state.interactionId = action.payload.interactionId
      state.source = action.payload.source
      state.suggestedFollowUps = []
      state.complianceFlags = action.payload.complianceFlags ?? []
    },
    // After a direct-form update (not a fresh create), the draft stays on
    // screen — re-baseline it against what was just saved and refresh
    // compliance flags so a materially-edited note's re-screening result
    // (MEDGENT-022) is visible, identically to the chat path.
    draftSavedAsUpdate(state, action: PayloadAction<ComplianceFlag[]>) {
      state.originalDraft = state.draft
      state.complianceFlags = action.payload
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
  chatEditInteractionApplied,
  draftLoaded,
  draftSavedAsUpdate,
  draftReset,
} = logInteractionDraftSlice.actions

export default logInteractionDraftSlice.reducer
