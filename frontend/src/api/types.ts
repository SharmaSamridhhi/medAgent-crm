// Hand-mirrored from backend/app/schemas/hcp.py and interaction.py.
// Keep in sync manually until OpenAPI codegen is worth the setup cost.

export interface HCP {
  id: string
  name: string
  specialty: string | null
  institution: string | null
  contact_info: string | null
  is_active: boolean
  created_at: string
}

export interface HCPCreate {
  name: string
  specialty?: string | null
  institution?: string | null
  contact_info?: string | null
}

export interface HCPUpdate {
  name?: string
  specialty?: string | null
  institution?: string | null
  contact_info?: string | null
}

export type Sentiment = 'positive' | 'neutral' | 'negative'
export type InteractionSource = 'form' | 'chat'
export type ComplianceFlagCategory =
  | 'off_label_claim'
  | 'unsubstantiated_claim'
  | 'adverse_event_mention'
  | 'other'

export interface ComplianceFlag {
  category: ComplianceFlagCategory
  excerpt: string
  rationale: string
}

export interface Interaction {
  id: string
  hcp_id: string
  rep_id: string
  interaction_type: string
  occurred_at: string
  attendees: string[]
  topics_discussed: string | null
  materials_shared: string[]
  samples_distributed: string[]
  sentiment: Sentiment | null
  outcomes: string | null
  follow_up_notes: string | null
  source: InteractionSource
  compliance_flags: ComplianceFlag[]
  has_compliance_flags: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InteractionCreate {
  hcp_id: string
  interaction_type: string
  occurred_at: string
  attendees?: string[]
  topics_discussed?: string | null
  materials_shared?: string[]
  samples_distributed?: string[]
  sentiment?: Sentiment | null
  outcomes?: string | null
  follow_up_notes?: string | null
  source?: InteractionSource
}

export interface InteractionUpdate {
  hcp_id?: string
  interaction_type?: string
  occurred_at?: string
  attendees?: string[]
  topics_discussed?: string | null
  materials_shared?: string[]
  samples_distributed?: string[]
  sentiment?: Sentiment | null
  outcomes?: string | null
  follow_up_notes?: string | null
  source?: InteractionSource
  compliance_flags?: ComplianceFlag[]
  has_compliance_flags?: boolean
}
