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

// Hand-mirrored from backend/app/agent/tools/*.py and api/v1/agent.py.
// One shape per LangGraph tool's output model, discriminated by the
// `tool` field on ToolSideEffect so the chat UI can render each kind
// distinctly (see MEDGENT-020).

export interface HCPCandidate {
  id: string
  name: string
  specialty: string | null
}

export interface LogInteractionOutput {
  status: 'created' | 'needs_clarification'
  message: string
  interaction_id: string | null
  hcp_id: string | null
  interaction_type: string | null
  occurred_at: string | null
  attendees: string[]
  topics_discussed: string | null
  materials_shared: string[]
  samples_distributed: string[]
  sentiment: Sentiment | null
  outcomes: string | null
  suggested_follow_ups: string[]
  compliance_flags: ComplianceFlag[]
  candidate_hcps: HCPCandidate[]
}

export interface FieldChange {
  field: string
  old_value: unknown
  new_value: unknown
}

export interface InteractionCandidate {
  id: string
  hcp_name: string
  occurred_at: string
}

export interface EditInteractionOutput {
  status: 'updated' | 'needs_clarification'
  message: string
  interaction_id: string | null
  changes: FieldChange[]
  candidate_interactions: InteractionCandidate[]
}

export interface InteractionSummary {
  id: string
  occurred_at: string
  interaction_type: string
  topics_discussed: string | null
  sentiment: Sentiment | null
  outcomes: string | null
}

export interface RetrieveHCPHistoryOutput {
  status: 'found' | 'needs_clarification'
  message: string
  hcp_id: string | null
  hcp_name: string | null
  specialty: string | null
  institution: string | null
  interactions: InteractionSummary[]
  summary: string | null
  candidate_hcps: HCPCandidate[]
}

export interface ScheduleFollowUpOutput {
  status: 'scheduled' | 'needs_clarification'
  message: string
  follow_up_id: string | null
  hcp_id: string | null
  due_date: string | null
  note: string | null
  candidate_hcps: HCPCandidate[]
}

export interface FlagComplianceRisksOutput {
  flags: ComplianceFlag[]
}

export type ToolSideEffect =
  | { tool: 'log_interaction'; output: LogInteractionOutput }
  | { tool: 'edit_interaction'; output: EditInteractionOutput }
  | { tool: 'retrieve_hcp_history'; output: RetrieveHCPHistoryOutput }
  | { tool: 'schedule_follow_up'; output: ScheduleFollowUpOutput }
  | { tool: 'flag_compliance_risks'; output: FlagComplianceRisksOutput }

export interface ChatRequest {
  message: string
  session_id?: string
}

export interface ChatResponse {
  session_id: string
  reply: string
  side_effects: ToolSideEffect[]
}
