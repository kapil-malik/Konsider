import type {
  CatalogCriterionV2,
  CatalogV2,
  OpportunityFilterCatalogV2,
  RankingV2,
} from '../api/types'
import { compactDisplayName } from '../displayName'
import {
  countryCode,
  readableCode,
} from '../localityPresentation'
import {
  OPPORTUNITY_STATE_CONTENT,
  filterName,
} from '../opportunityPresentation'

type AssessmentSummaryProps = {
  ranking: RankingV2
  criteria: CatalogCriterionV2[]
  countries: CatalogV2['countries']
  opportunityCatalog: OpportunityFilterCatalogV2
  isUpdating: boolean
  onSelectCountry: (countryCode: string) => void
  onClearOpportunityFilters: () => void
}

export function AssessmentSummary({
  ranking,
  criteria,
  countries,
  opportunityCatalog,
  isUpdating,
  onSelectCountry,
  onClearOpportunityFilters,
}: AssessmentSummaryProps) {
  const coverage = ranking.assessments.coverage
  const opportunity = ranking.assessments.opportunity
  const criterionNames = new Map(
    criteria.map((criterion) => [criterion.id, compactDisplayName(criterion)]),
  )
  const opportunityDefinitions = new Map(
    opportunityCatalog.definitions.map((definition) => [definition.id, definition]),
  )
  const countryNames = new Map(
    countries.map((country) => [countryCode(country.entity_id), country.display_name]),
  )

  if (
    opportunity.active_filter_ids.length === 0 &&
    coverage.excluded_countries.length === 0
  ) {
    return null
  }

  return (
    <section className="assessment-summary" aria-labelledby="result-details-heading">
      <div className="result-details-heading">
        <div>
          <p className="eyebrow">Supporting detail</p>
          <h3 id="result-details-heading">Result details and exclusions</h3>
        </div>
        <span>Review why countries were included or left out.</span>
      </div>

      {opportunity.active_filter_ids.length > 0 && (
        <details
          className={`excluded-country-details opportunity-exclusions opportunity-${opportunity.status.toLocaleLowerCase()}`}
        >
          <summary>
            <span>Opportunity-filter results</span>
            <span>
              {opportunity.passing_country_count} matching · {opportunity.excluded_country_count}{' '}
              excluded
            </span>
          </summary>
          <div className="result-detail-body">
            <div className="result-detail-intro">
              <p>
                Selected filters require a verified strong signal. They restrict the result but
                do not change affinity scores.
              </p>
              <button
                type="button"
                className="text-button"
                disabled={isUpdating}
                onClick={onClearOpportunityFilters}
              >
                Clear all filters
              </button>
            </div>
            {opportunity.status === 'NO_COUNTRIES_MATCH' && (
              <p>
                This does not mean these opportunities are absent everywhere; some countries may
                have insufficient comparable evidence. Remove one filter to broaden the result.
              </p>
            )}
            <dl className="opportunity-counts">
              <div>
                <dt>Match every selected filter</dt>
                <dd>{opportunity.passing_country_count}</dd>
              </div>
              <div className="count-not-established">
                <dt>Strong signal not established</dt>
                <dd>
                  {opportunity.excluded_counts_by_state.STRONG_SIGNAL_NOT_ESTABLISHED}
                </dd>
              </div>
              <div className="count-insufficient">
                <dt>Insufficient evidence</dt>
                <dd>{opportunity.excluded_counts_by_state.INSUFFICIENT_EVIDENCE}</dd>
              </div>
            </dl>
            <details className="opportunity-filter-counts">
              <summary>Counts by selected filter</summary>
              <ul>
                {opportunity.per_filter.map((filter) => (
                  <li key={filter.filter_id}>
                    <strong>
                      {filterName(
                        opportunityDefinitions.get(filter.filter_id),
                        filter.filter_id,
                      )}
                    </strong>
                    <span>
                      {filter.passing_country_count} verified ·{' '}
                      {filter.state_counts.STRONG_SIGNAL_NOT_ESTABLISHED} not established ·{' '}
                      {filter.state_counts.INSUFFICIENT_EVIDENCE} insufficient evidence
                    </span>
                  </li>
                ))}
              </ul>
            </details>
            {opportunity.excluded_countries.length > 0 && (
              <div className="excluded-country-list opportunity-excluded-list">
                {opportunity.excluded_countries.map((excluded) => (
                  <article className="excluded-country-card" key={excluded.country_code}>
                    <div className="excluded-country-heading">
                      <div>
                        <button
                          className="text-button"
                          onClick={() => onSelectCountry(excluded.country_code)}
                        >
                          {countryNames.get(excluded.country_code) ?? excluded.country_code}
                        </button>
                        <span>Base rank {excluded.base_rank} · excluded by selected evidence</span>
                      </div>
                      <span
                        className={`opportunity-state-badge state-${
                          OPPORTUNITY_STATE_CONTENT[excluded.exclusion_category].className
                        }`}
                      >
                        {OPPORTUNITY_STATE_CONTENT[excluded.exclusion_category].label}
                      </span>
                    </div>
                    <ul className="failing-filter-list">
                      {excluded.failing_filter_evidence.map((evidence) => {
                        const content = OPPORTUNITY_STATE_CONTENT[evidence.state]
                        return (
                          <li key={evidence.filter_id}>
                            <strong>
                              {filterName(
                                opportunityDefinitions.get(evidence.filter_id),
                                evidence.filter_id,
                              )}
                            </strong>
                            <span className={`opportunity-state-badge state-${content.className}`}>
                              <span aria-hidden="true">{content.icon}</span> {content.label}
                            </span>
                            <p>{content.explanation}</p>
                          </li>
                        )
                      })}
                    </ul>
                  </article>
                ))}
              </div>
            )}
          </div>
        </details>
      )}

      {coverage.excluded_countries.length > 0 && (
        <details className="excluded-country-details">
          <summary>
            <span>Coverage exclusions</span>
            <span>
              {coverage.excluded_countries.length}{' '}
              {coverage.excluded_countries.length === 1 ? 'country' : 'countries'}
            </span>
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
    </section>
  )
}
