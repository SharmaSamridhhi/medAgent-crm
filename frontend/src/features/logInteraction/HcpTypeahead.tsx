import { skipToken } from '@reduxjs/toolkit/query/react'
import { useEffect, useRef, useState } from 'react'
import { useListHcpsQuery } from '../../api/hcpsApi'
import type { HCP } from '../../api/types'
import './HcpTypeahead.css'

interface HcpTypeaheadProps {
  query: string
  onQueryChange: (query: string) => void
  onSelect: (hcp: HCP) => void
  error?: string
}

function HcpTypeahead({
  query,
  onQueryChange,
  onSelect,
  error,
}: HcpTypeaheadProps) {
  const [debouncedQuery, setDebouncedQuery] = useState(query)
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handle = setTimeout(() => setDebouncedQuery(query), 250)
    return () => clearTimeout(handle)
  }, [query])

  const trimmed = debouncedQuery.trim()
  const { data: hcps = [], isFetching } = useListHcpsQuery(
    trimmed.length > 0 ? { search: trimmed, limit: 10 } : skipToken,
  )

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function handleSelect(hcp: HCP) {
    onSelect(hcp)
    setIsOpen(false)
  }

  return (
    <div className="hcp-typeahead" ref={containerRef}>
      <label className="field-label" htmlFor="hcp-typeahead-input">
        HCP Name
      </label>
      <input
        id="hcp-typeahead-input"
        type="text"
        role="combobox"
        aria-expanded={isOpen}
        aria-autocomplete="list"
        autoComplete="off"
        placeholder="Search or select HCP..."
        value={query}
        onChange={(event) => {
          onQueryChange(event.target.value)
          setIsOpen(true)
        }}
        onFocus={() => setIsOpen(true)}
      />
      {error && <p className="field-error">{error}</p>}
      {isOpen && trimmed.length > 0 && (
        <ul className="hcp-typeahead__results">
          {isFetching && <li className="hcp-typeahead__status">Searching…</li>}
          {!isFetching && hcps.length === 0 && (
            <li className="hcp-typeahead__status">No matching HCPs.</li>
          )}
          {hcps.map((hcp) => (
            <li key={hcp.id}>
              <button type="button" onClick={() => handleSelect(hcp)}>
                <span className="hcp-typeahead__name">{hcp.name}</span>
                {hcp.specialty && (
                  <span className="hcp-typeahead__specialty">
                    {hcp.specialty}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default HcpTypeahead
