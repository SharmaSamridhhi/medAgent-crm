import { skipToken } from '@reduxjs/toolkit/query/react'
import { useListInteractionsQuery } from '../../api/interactionsApi'
import type { Interaction } from '../../api/types'
import './RecentInteractionsList.css'

const RECENT_LIMIT = 5

interface RecentInteractionsListProps {
  hcpId: string | null
  onEdit: (interaction: Interaction) => void
}

function formatDate(occurredAt: string): string {
  return new Date(occurredAt).toLocaleDateString()
}

function RecentInteractionsList({
  hcpId,
  onEdit,
}: RecentInteractionsListProps) {
  const { data: interactions = [] } = useListInteractionsQuery(
    hcpId ? { hcp_id: hcpId, limit: RECENT_LIMIT } : skipToken,
  )

  if (!hcpId) {
    return null
  }

  return (
    <section className="recent-interactions">
      <h3 className="recent-interactions__title">Recent interactions</h3>
      {interactions.length === 0 ? (
        <p className="recent-interactions__empty">
          No interactions logged with this HCP yet.
        </p>
      ) : (
        <ul>
          {interactions.map((interaction) => (
            <li key={interaction.id} className="recent-interactions__item">
              <div>
                <span className="recent-interactions__type">
                  {interaction.interaction_type}
                </span>
                <span className="recent-interactions__date">
                  {formatDate(interaction.occurred_at)}
                </span>
                {interaction.topics_discussed && (
                  <p className="recent-interactions__topics">
                    {interaction.topics_discussed}
                  </p>
                )}
              </div>
              <button type="button" onClick={() => onEdit(interaction)}>
                Edit
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default RecentInteractionsList
