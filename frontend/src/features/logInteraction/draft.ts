import type { FieldChange, Interaction, Sentiment } from '../../api/types'

export const INTERACTION_TYPES = [
  'Meeting',
  'Call',
  'Email',
  'Conference',
  'Other',
] as const

// UI-only shape: mirrors InteractionCreate's field names directly (see
// MEDGENT-019's technical details) plus a couple of fields (hcp_name,
// date/time) that only exist for editing convenience and get combined /
// dropped when building the API payload.
export interface InteractionDraft {
  hcp_id: string | null
  hcp_name: string
  interaction_type: string
  date: string
  time: string
  attendees: string[]
  topics_discussed: string
  materials_shared: string[]
  samples_distributed: string[]
  sentiment: Sentiment | null
  outcomes: string
  follow_up_notes: string
}

export function createEmptyDraft(): InteractionDraft {
  return {
    hcp_id: null,
    hcp_name: '',
    interaction_type: INTERACTION_TYPES[0],
    date: '',
    time: '',
    attendees: [],
    topics_discussed: '',
    materials_shared: [],
    samples_distributed: [],
    sentiment: null,
    outcomes: '',
    follow_up_notes: '',
  }
}

export interface DraftValidationErrors {
  hcp_id?: string
  interaction_type?: string
  date?: string
  time?: string
  sentiment?: string
}

const VALID_SENTIMENTS: Sentiment[] = ['positive', 'neutral', 'negative']

export function validateDraft(draft: InteractionDraft): DraftValidationErrors {
  const errors: DraftValidationErrors = {}

  if (!draft.hcp_id) {
    errors.hcp_id = 'Select an HCP from the search results.'
  }
  if (!draft.interaction_type.trim()) {
    errors.interaction_type = 'Interaction type is required.'
  }
  if (!draft.date) {
    errors.date = 'Date is required.'
  }
  if (!draft.time) {
    errors.time = 'Time is required.'
  }
  if (draft.sentiment !== null && !VALID_SENTIMENTS.includes(draft.sentiment)) {
    errors.sentiment = 'Sentiment must be positive, neutral, or negative.'
  }

  return errors
}

export function occurredAtFromDraft(draft: InteractionDraft): string {
  return new Date(`${draft.date}T${draft.time}`).toISOString()
}

// Loads an already-saved interaction into the shared draft shape for
// editing (MEDGENT-022). hcp_name isn't on Interaction — LogInteraction
// Screen resolves it the same way it resolves a chat-created hcp_id.
export function draftFromInteraction(
  interaction: Interaction,
): InteractionDraft {
  const occurredAt = new Date(interaction.occurred_at)
  return {
    hcp_id: interaction.hcp_id,
    hcp_name: '',
    interaction_type: interaction.interaction_type,
    date: occurredAt.toISOString().slice(0, 10),
    time: occurredAt.toISOString().slice(11, 16),
    attendees: interaction.attendees,
    topics_discussed: interaction.topics_discussed ?? '',
    materials_shared: interaction.materials_shared,
    samples_distributed: interaction.samples_distributed,
    sentiment: interaction.sentiment,
    outcomes: interaction.outcomes ?? '',
    follow_up_notes: interaction.follow_up_notes ?? '',
  }
}

const DIFFABLE_FIELDS = [
  'interaction_type',
  'attendees',
  'topics_discussed',
  'materials_shared',
  'samples_distributed',
  'sentiment',
  'outcomes',
  'follow_up_notes',
] as const satisfies readonly (keyof InteractionDraft)[]

// Field-by-field before/after diff for the edit confirmation UI
// (MEDGENT-022) — deliberately mirrors edit_interaction's own
// `FieldChange` shape so both edit paths render identically.
export function diffDraftFields(
  before: InteractionDraft,
  after: InteractionDraft,
): FieldChange[] {
  const changes: FieldChange[] = []
  for (const field of DIFFABLE_FIELDS) {
    const oldValue = before[field]
    const newValue = after[field]
    if (JSON.stringify(oldValue) !== JSON.stringify(newValue)) {
      changes.push({ field, old_value: oldValue, new_value: newValue })
    }
  }
  return changes
}
