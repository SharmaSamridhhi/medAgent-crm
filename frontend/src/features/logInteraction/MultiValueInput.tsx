import { useState } from 'react'
import type { KeyboardEvent } from 'react'
import './MultiValueInput.css'

interface MultiValueInputProps {
  label: string
  values: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  addButtonLabel?: string
  emptyLabel?: string
}

function MultiValueInput({
  label,
  values,
  onChange,
  placeholder,
  addButtonLabel = 'Add',
  emptyLabel = 'None added',
}: MultiValueInputProps) {
  const [draftValue, setDraftValue] = useState('')

  function addValue() {
    const trimmed = draftValue.trim()
    if (!trimmed || values.includes(trimmed)) {
      setDraftValue('')
      return
    }
    onChange([...values, trimmed])
    setDraftValue('')
  }

  function removeValue(value: string) {
    onChange(values.filter((v) => v !== value))
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      addValue()
    }
  }

  return (
    <div className="multi-value-input">
      <label className="field-label" htmlFor={`multi-value-${label}`}>
        {label}
      </label>
      <div className="multi-value-input__row">
        <input
          id={`multi-value-${label}`}
          type="text"
          value={draftValue}
          placeholder={placeholder}
          onChange={(event) => setDraftValue(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button type="button" onClick={addValue}>
          {addButtonLabel}
        </button>
      </div>
      {values.length === 0 ? (
        <p className="multi-value-input__empty">{emptyLabel}</p>
      ) : (
        <ul className="multi-value-input__chips">
          {values.map((value) => (
            <li key={value} className="multi-value-input__chip">
              {value}
              <button
                type="button"
                aria-label={`Remove ${value}`}
                onClick={() => removeValue(value)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default MultiValueInput
