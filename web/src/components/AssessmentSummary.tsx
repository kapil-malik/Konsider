import type { CatalogCriterionV2, RankingV2 } from '../api/types'
import {
  COVERAGE_CONTENT,
  LOCALITY_CONTENT,
  PROFILE_CONTENT,
  countryCode,
  readableCode,
} from '../localityPresentation'

type AssessmentSummaryProps = {
  ranking: RankingV2
  criteria: CatalogCriterionV2[]
  onSelectCountry: (countryCode: string) => void
}

function AssessmentNotice({
  domain,
  content,
}: {
  domain: string
  content: {
    label: string
    message: string
    prominence: 'neutral' | 'mild' | 'caution' | 'strong'
    icon: string
  }
}) {
  return (
    <article
      className={`assessment-notice assessment-${content.prominence}`}
      role="status"
      aria-label={`${domain} status: ${content.label}`}
    >
      <span className="assessment-icon" aria-hidden="true">
        {content.icon}
      </span>
      <div>
        <span className="assessment-domain">{domain}</span>
        <strong>{content.label}</strong>
        <p>{content.message}</p>
      </div>
    </article>
  )
}

export function AssessmentSummary({
  ranking,
  criteria,
  onSelectCountry,
}: AssessmentSummaryProps) {
  const coverage = ranking.assessments.coverage
  const locality = ranking.assessments.locality
  const profile = ranking.assessments.profile
  const criterionNames = new Map(
    criteria.map((criterion) => [criterion.id, criterion.display_name]),
  )

  return (
    <div className="assessment-summary">
      <div className="assessment-domain-grid">
        <AssessmentNotice
          domain="Coverage"
          content={COVERAGE_CONTENT[coverage.status]}
        />
        <AssessmentNotice
          domain="Locality"
          content={LOCALITY_CONTENT[locality.status]}
        />
        <AssessmentNotice
          domain="Profile"
          content={PROFILE_CONTENT[profile.status]}
        />
      </div>

      <dl className="ranking-summary-grid">
        <div>
          <dt>Countries ranked</dt>
          <dd>{ranking.rankings.length}</dd>
        </div>
        <div>
          <dt>Countries excluded</dt>
          <dd>{coverage.excluded_countries.length}</dd>
        </div>
        <div>
          <dt>Locality criteria contributing</dt>
          <dd>
            {locality.contributing_criterion_ids.length
              ? locality.contributing_criterion_ids
                  .map((id) => criterionNames.get(id) ?? id)
                  .join(', ')
              : 'None'}
          </dd>
        </div>
        <div>
          <dt>Locality analysis triggered</dt>
          <dd>
            {locality.analysis_triggered_criterion_ids.length
              ? locality.analysis_triggered_criterion_ids
                  .map((id) => criterionNames.get(id) ?? id)
                  .join(', ')
              : 'None'}
          </dd>
        </div>
      </dl>

      {coverage.excluded_countries.length > 0 && (
        <details className="excluded-country-details">
          <summary>
            Review {coverage.excluded_countries.length} coverage-excluded{' '}
            {coverage.excluded_countries.length === 1 ? 'country' : 'countries'}
          </summary>
          <div className="excluded-country-list">
            {coverage.excluded_countries.map((excluded) => {
              const code = countryCode(excluded.country.entity_id)
              const unavailable = excluded.criterion_evidence.filter(
                (item) => item.outcome !== 'valid',
              )
              return (
                <article key={excluded.country.entity_id} className="excluded-country-card">
                  <div className="excluded-country-heading">
                    <div>
                      <button
                        className="text-button"
                        onClick={() => onSelectCountry(code)}
                      >
                        {excluded.country.display_name}
                      </button>
                      <span>Coverage excluded · no final aggregate</span>
                    </div>
                    <span className="badge badge-unavailable">! Not ranked</span>
                  </div>
                  <dl>
                    <div>
                      <dt>Unavailable active criteria</dt>
                      <dd>
                        {unavailable
                          .map((item) => {
                            const name =
                              criterionNames.get(item.criterion_id) ??
                              item.criterion_id
                            const reasons = item.reason_codes
                              .map(readableCode)
                              .join(', ')
                            return `${name}: ${readableCode(item.outcome)}${
                              reasons ? ` — ${reasons}` : ''
                            }`
                          })
                          .join('; ')}
                      </dd>
                    </div>
                    <div>
                      <dt>Locality assessment</dt>
                      <dd>{readableCode(excluded.locality_assessment.status)}</dd>
                    </div>
                  </dl>
                </article>
              )
            })}
          </div>
        </details>
      )}
    </div>
  )
}
