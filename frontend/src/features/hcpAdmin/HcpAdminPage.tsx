import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useCreateHcpMutation, useListHcpsQuery } from '../../api/hcpsApi'
import './HcpAdminPage.css'

interface HcpFormState {
  name: string
  specialty: string
  institution: string
  contact_info: string
}

function emptyForm(): HcpFormState {
  return { name: '', specialty: '', institution: '', contact_info: '' }
}

function HcpAdminPage() {
  const [search, setSearch] = useState('')
  const { data: hcps = [], isFetching } = useListHcpsQuery({
    search: search.trim() || undefined,
    limit: 50,
  })
  const [createHcp, { isLoading }] = useCreateHcpMutation()
  const [form, setForm] = useState<HcpFormState>(emptyForm())
  const [error, setError] = useState<string | null>(null)

  function updateField<K extends keyof HcpFormState>(
    key: K,
    value: HcpFormState[K],
  ) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!form.name.trim()) {
      setError('Name is required.')
      return
    }
    setError(null)
    try {
      await createHcp({
        name: form.name.trim(),
        specialty: form.specialty.trim() || undefined,
        institution: form.institution.trim() || undefined,
        contact_info: form.contact_info.trim() || undefined,
      }).unwrap()
      setForm(emptyForm())
    } catch {
      setError(
        'Could not create this HCP. Check your connection and try again.',
      )
    }
  }

  return (
    <div className="hcp-admin">
      <div className="hcp-admin__header">
        <h1>HCPs</h1>
        <Link to="/">← Back to Log Interaction</Link>
      </div>

      <form className="hcp-admin__create-form" onSubmit={handleSubmit}>
        <h2>Add HCP</h2>
        <div className="hcp-admin__create-fields">
          <input
            aria-label="Name"
            placeholder="Name"
            value={form.name}
            onChange={(event) => updateField('name', event.target.value)}
          />
          <input
            aria-label="Specialty"
            placeholder="Specialty"
            value={form.specialty}
            onChange={(event) => updateField('specialty', event.target.value)}
          />
          <input
            aria-label="Institution"
            placeholder="Institution"
            value={form.institution}
            onChange={(event) => updateField('institution', event.target.value)}
          />
          <input
            aria-label="Contact info"
            placeholder="Contact info"
            value={form.contact_info}
            onChange={(event) =>
              updateField('contact_info', event.target.value)
            }
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Adding…' : 'Add HCP'}
          </button>
        </div>
        {error && (
          <p role="alert" className="hcp-admin__error">
            {error}
          </p>
        )}
      </form>

      <div className="hcp-admin__search">
        <label htmlFor="hcp-admin-search">Search</label>
        <input
          id="hcp-admin-search"
          placeholder="Search by name..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <table className="hcp-admin__table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Specialty</th>
            <th>Institution</th>
            <th>Contact Info</th>
            <th>Active</th>
          </tr>
        </thead>
        <tbody>
          {hcps.map((hcp) => (
            <tr key={hcp.id}>
              <td>{hcp.name}</td>
              <td>{hcp.specialty ?? '—'}</td>
              <td>{hcp.institution ?? '—'}</td>
              <td>{hcp.contact_info ?? '—'}</td>
              <td>{hcp.is_active ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!isFetching && hcps.length === 0 && (
        <p className="hcp-admin__empty">No HCPs found.</p>
      )}
    </div>
  )
}

export default HcpAdminPage
