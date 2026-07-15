import type { Sentiment } from '../../api/types'

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
