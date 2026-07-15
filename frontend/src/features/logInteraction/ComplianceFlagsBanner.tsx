import type { ComplianceFlag } from '../../api/types'
import './SideEffectCard.css'

interface ComplianceFlagsBannerProps {
  flags: ComplianceFlag[]
}

function ComplianceFlagsBanner({ flags }: ComplianceFlagsBannerProps) {
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

export default ComplianceFlagsBanner
