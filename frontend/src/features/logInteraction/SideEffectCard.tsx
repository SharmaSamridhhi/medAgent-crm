import type { ComplianceFlag, ToolSideEffect } from '../../api/types'
import './SideEffectCard.css'

interface SideEffectCardProps {
  effect: ToolSideEffect
  onSuggestedFollowUpClick?: (suggestion: string) => void
}

function ComplianceFlags({ flags }: { flags: ComplianceFlag[] }) {
  if (flags.length === 0) {
    return null
  }
  return (
    <div className="side-effect-card__flags" role="alert">
      <p className="side-effect-card__flags-title">⚠ Compliance flags</p>
      <ul>
        {flags.map((flag) => (
          <li key={`${flag.category}-${flag.excerpt}`}>
            <strong>{flag.category.replace(/_/g, ' ')}:</strong> "{flag.excerpt}
            " — {flag.rationale}
          </li>
        ))}
      </ul>
    </div>
  )
}

function SideEffectCard({
  effect,
  onSuggestedFollowUpClick,
}: SideEffectCardProps) {
  if (effect.tool === 'log_interaction') {
    const output = effect.output
    if (output.status === 'needs_clarification') {
      return null
    }
    return (
      <div className="side-effect-card side-effect-card--log">
        <p className="side-effect-card__title">✓ Interaction logged</p>
        <dl className="side-effect-card__fields">
          {output.interaction_type && (
            <>
              <dt>Type</dt>
              <dd>{output.interaction_type}</dd>
            </>
          )}
          {output.sentiment && (
            <>
              <dt>Sentiment</dt>
              <dd>{output.sentiment}</dd>
            </>
          )}
          {output.topics_discussed && (
            <>
              <dt>Topics</dt>
              <dd>{output.topics_discussed}</dd>
            </>
          )}
          {output.outcomes && (
            <>
              <dt>Outcomes</dt>
              <dd>{output.outcomes}</dd>
            </>
          )}
        </dl>
        {output.suggested_follow_ups.length > 0 && (
          <div className="side-effect-card__suggestions">
            <p className="side-effect-card__suggestions-title">
              Suggested follow-ups
            </p>
            <ul>
              {output.suggested_follow_ups.map((suggestion) => (
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
        <ComplianceFlags flags={output.compliance_flags} />
      </div>
    )
  }

  if (effect.tool === 'edit_interaction') {
    const output = effect.output
    if (
      output.status === 'needs_clarification' ||
      output.changes.length === 0
    ) {
      return null
    }
    return (
      <div className="side-effect-card side-effect-card--edit">
        <p className="side-effect-card__title">✓ Interaction updated</p>
        <ul className="side-effect-card__changes">
          {output.changes.map((change) => (
            <li key={change.field}>
              <strong>{change.field.replace(/_/g, ' ')}:</strong>{' '}
              <span className="side-effect-card__old-value">
                {JSON.stringify(change.old_value)}
              </span>{' '}
              →{' '}
              <span className="side-effect-card__new-value">
                {JSON.stringify(change.new_value)}
              </span>
            </li>
          ))}
        </ul>
      </div>
    )
  }

  if (effect.tool === 'retrieve_hcp_history') {
    const output = effect.output
    if (output.status === 'needs_clarification') {
      return null
    }
    return (
      <div className="side-effect-card side-effect-card--history">
        <p className="side-effect-card__title">
          HCP history — {output.hcp_name}
        </p>
        {output.summary && <p>{output.summary}</p>}
      </div>
    )
  }

  if (effect.tool === 'schedule_follow_up') {
    const output = effect.output
    if (output.status === 'needs_clarification') {
      return null
    }
    return (
      <div className="side-effect-card side-effect-card--follow-up">
        <p className="side-effect-card__title">
          ✓ Follow-up scheduled
          {output.due_date ? ` for ${output.due_date}` : ''}
        </p>
        {output.note && <p>{output.note}</p>}
      </div>
    )
  }

  if (effect.tool === 'flag_compliance_risks') {
    return <ComplianceFlags flags={effect.output.flags} />
  }

  return null
}

export default SideEffectCard
