import type { FieldChange } from '../../api/types'
import './FieldChangesList.css'

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : '—'
  }
  return String(value)
}

interface FieldChangesListProps {
  changes: FieldChange[]
}

// Shared before/after rendering for both edit paths (direct form edit and
// conversational edit_interaction) so a rep sees an identical confirmation
// regardless of how the edit was made — see MEDGENT-022.
function FieldChangesList({ changes }: FieldChangesListProps) {
  if (changes.length === 0) {
    return null
  }
  return (
    <ul className="field-changes-list">
      {changes.map((change) => (
        <li key={change.field}>
          <strong>{change.field.replace(/_/g, ' ')}:</strong>{' '}
          <span className="field-changes-list__old">
            {formatValue(change.old_value)}
          </span>{' '}
          →{' '}
          <span className="field-changes-list__new">
            {formatValue(change.new_value)}
          </span>
        </li>
      ))}
    </ul>
  )
}

export default FieldChangesList
