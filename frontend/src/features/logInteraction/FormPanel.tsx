import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  useCreateInteractionMutation,
  useUpdateInteractionMutation,
} from '../../api/interactionsApi'
import type { HCP, Interaction, Sentiment } from '../../api/types'
import {
  INTERACTION_TYPES,
  occurredAtFromDraft,
  validateDraft,
  type DraftValidationErrors,
  type InteractionDraft,
} from './draft'
import HcpTypeahead from './HcpTypeahead'
import MultiValueInput from './MultiValueInput'
import './FormPanel.css'

interface FormPanelProps {
  value: InteractionDraft
  onChange: (draft: InteractionDraft) => void
  suggestedFollowUps?: string[]
  onSuggestedFollowUpClick?: (suggestion: string) => void
  onSaved?: (interaction: Interaction) => void
  // Set once the chat panel's log_interaction tool has already created
  // this interaction server-side (see MEDGENT-021) — submitting then
  // updates that same row instead of creating a duplicate.
  interactionId?: string | null
}

const SENTIMENT_OPTIONS: { value: Sentiment; label: string }[] = [
  { value: 'positive', label: 'Positive' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'negative', label: 'Negative' },
]

function FormPanel({
  value,
  onChange,
  suggestedFollowUps = [],
  onSuggestedFollowUpClick,
  onSaved,
  interactionId = null,
}: FormPanelProps) {
  const [createInteraction, { isLoading: isCreating }] =
    useCreateInteractionMutation()
  const [updateInteraction, { isLoading: isUpdating }] =
    useUpdateInteractionMutation()
  const isLoading = isCreating || isUpdating
  const [errors, setErrors] = useState<DraftValidationErrors>({})
  const [submitState, setSubmitState] = useState<'idle' | 'success' | 'error'>(
    'idle',
  )
  const [submitErrorMessage, setSubmitErrorMessage] = useState<string | null>(
    null,
  )

  function updateField<K extends keyof InteractionDraft>(
    key: K,
    fieldValue: InteractionDraft[K],
  ) {
    onChange({ ...value, [key]: fieldValue })
  }

  function handleHcpSelect(hcp: HCP) {
    onChange({ ...value, hcp_id: hcp.id, hcp_name: hcp.name })
  }

  function handleHcpQueryChange(query: string) {
    onChange({ ...value, hcp_name: query, hcp_id: null })
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const validationErrors = validateDraft(value)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setSubmitErrorMessage(null)
    const fields = {
      hcp_id: value.hcp_id as string,
      interaction_type: value.interaction_type,
      occurred_at: occurredAtFromDraft(value),
      attendees: value.attendees,
      topics_discussed: value.topics_discussed || null,
      materials_shared: value.materials_shared,
      samples_distributed: value.samples_distributed,
      sentiment: value.sentiment,
      outcomes: value.outcomes || null,
      follow_up_notes: value.follow_up_notes || null,
    }
    try {
      const saved = interactionId
        ? await updateInteraction({ id: interactionId, body: fields }).unwrap()
        : await createInteraction({ ...fields, source: 'form' }).unwrap()
      setSubmitState('success')
      onSaved?.(saved)
    } catch {
      setSubmitState('error')
      setSubmitErrorMessage(
        'Could not save this interaction. Check your connection and try again.',
      )
    }
  }

  return (
    <form className="form-panel" onSubmit={handleSubmit} noValidate>
      <h2 className="form-panel__title">Interaction Details</h2>

      <HcpTypeahead
        query={value.hcp_name}
        onQueryChange={handleHcpQueryChange}
        onSelect={handleHcpSelect}
        error={errors.hcp_id}
      />

      <div className="field">
        <label className="field-label" htmlFor="interaction-type">
          Interaction Type
        </label>
        <select
          id="interaction-type"
          value={value.interaction_type}
          onChange={(event) =>
            updateField('interaction_type', event.target.value)
          }
        >
          {INTERACTION_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        {errors.interaction_type && (
          <p className="field-error">{errors.interaction_type}</p>
        )}
      </div>

      <div className="form-panel__row">
        <div className="field">
          <label className="field-label" htmlFor="interaction-date">
            Date
          </label>
          <input
            id="interaction-date"
            type="date"
            value={value.date}
            onChange={(event) => updateField('date', event.target.value)}
          />
          {errors.date && <p className="field-error">{errors.date}</p>}
        </div>
        <div className="field">
          <label className="field-label" htmlFor="interaction-time">
            Time
          </label>
          <input
            id="interaction-time"
            type="time"
            value={value.time}
            onChange={(event) => updateField('time', event.target.value)}
          />
          {errors.time && <p className="field-error">{errors.time}</p>}
        </div>
      </div>

      <MultiValueInput
        label="Attendees"
        values={value.attendees}
        onChange={(attendees) => updateField('attendees', attendees)}
        placeholder="Enter names or search..."
      />

      <div className="field">
        <label className="field-label" htmlFor="topics-discussed">
          Topics Discussed
        </label>
        <textarea
          id="topics-discussed"
          rows={4}
          placeholder="Enter key discussion points..."
          value={value.topics_discussed}
          onChange={(event) =>
            updateField('topics_discussed', event.target.value)
          }
        />
        <button
          type="button"
          className="form-panel__voice-note-button"
          disabled
          title="Voice note capture is coming soon"
        >
          Summarize from Voice Note (Requires Consent)
        </button>
      </div>

      <MultiValueInput
        label="Materials Shared"
        values={value.materials_shared}
        onChange={(materials) => updateField('materials_shared', materials)}
        placeholder="Search/add materials..."
        addButtonLabel="Search/Add"
      />

      <MultiValueInput
        label="Samples Distributed"
        values={value.samples_distributed}
        onChange={(samples) => updateField('samples_distributed', samples)}
        placeholder="Add sample..."
        addButtonLabel="Add Sample"
      />

      <fieldset className="field form-panel__sentiment">
        <legend className="field-label">Observed/Inferred HCP Sentiment</legend>
        {SENTIMENT_OPTIONS.map((option) => (
          <label key={option.value} className="form-panel__radio-option">
            <input
              type="radio"
              name="sentiment"
              value={option.value}
              checked={value.sentiment === option.value}
              onChange={() => updateField('sentiment', option.value)}
            />
            {option.label}
          </label>
        ))}
        {errors.sentiment && <p className="field-error">{errors.sentiment}</p>}
      </fieldset>

      <div className="field">
        <label className="field-label" htmlFor="outcomes">
          Outcomes
        </label>
        <textarea
          id="outcomes"
          rows={3}
          placeholder="Key outcomes or agreements..."
          value={value.outcomes}
          onChange={(event) => updateField('outcomes', event.target.value)}
        />
      </div>

      <div className="field">
        <label className="field-label" htmlFor="follow-up-notes">
          Follow-up Actions
        </label>
        <textarea
          id="follow-up-notes"
          rows={3}
          placeholder="Enter next steps or tasks..."
          value={value.follow_up_notes}
          onChange={(event) =>
            updateField('follow_up_notes', event.target.value)
          }
        />
        {suggestedFollowUps.length > 0 && (
          <div className="form-panel__suggested-follow-ups">
            <p className="field-label">AI Suggested Follow-ups</p>
            <ul>
              {suggestedFollowUps.map((suggestion) => (
                <li key={suggestion}>
                  <button
                    type="button"
                    onClick={() => onSuggestedFollowUpClick?.(suggestion)}
                  >
                    + {suggestion}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {submitState === 'error' && submitErrorMessage && (
        <p
          role="alert"
          className="form-panel__banner form-panel__banner--error"
        >
          {submitErrorMessage}
        </p>
      )}
      {submitState === 'success' && (
        <p
          role="status"
          className="form-panel__banner form-panel__banner--success"
        >
          Interaction saved.
        </p>
      )}

      <button type="submit" className="form-panel__submit" disabled={isLoading}>
        {isLoading
          ? 'Saving…'
          : interactionId
            ? 'Save Changes'
            : 'Log Interaction'}
      </button>
    </form>
  )
}

export default FormPanel
