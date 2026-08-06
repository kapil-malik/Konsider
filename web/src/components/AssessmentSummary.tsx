import type {
  CatalogCriterionV2,
  CatalogV2,
  OpportunityFilterCatalogV2,
  RankingV2,
} from '../api/types'
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
  onRemoveOpportunityFilter: (filterId: string) => void
  onClearOpportunityFilters: () => void
}

export function AssessmentSummary({
  ranking,
  criteria,
  countries,
  opportunityCatalog,
  isUpdating,
  onSelectCountry,
  onRemoveOpportunityFilter,
  onClearOpportunityFilters,
}: AssessmentSummaryProps) {
  const coverage = ranking.assessments.coverage
  const locality = ranking.assessments.locality
  const opportunity = ranking.assessments.opportunity
  const criterionNames = new Map(
    criteria.map((criterion) => [criterion.id, criterion.display_name]),
  )
  const opportunityDefinitions = new Map(
    opportunityCatalog.definitions.map((definition) => [definition.id, definition]),
  )
  const countryNames = new Map(
    countries.map((country) => [countryCode(country.entity_id), country.display_name]),
  )

  return (
    <div className="assessment-summary">
      {opportunity.active_filter_ids.length > 0 && (
        <section
          className={`opportunity-result-summary opportunity-${opportunity.status.toLocaleLowerCase()}`}
          aria-labelledby="opportunity-result-heading"
          aria-live="polite"
        >
          <div className="opportunity-result-heading">
            <div>
              <span className="assessment-domain">Opportunity filters</span>
              <h3 id="opportunity-result-heading">
                {opportunity.status === 'NO_COUNTRIES_MATCH'
                  ? 'No country matches every selected opportunity filter'
                  : `${opportunity.passing_country_count} ${
                      opportunity.passing_country_count === 1 ? 'country matches' : 'countries match'
                    } all selected opportunity filters`}
              </h3>
            </div>
            <button
              type="button"
              className="text-button"
              disabled={isUpdating}
              onClick={onClearOpportunityFilters}
            >
              Clear all
            </button>
          </div>
          <p>
            Opportunity filters do not change affinity scores. All selected filters require a
            verified strong signal.
          </p>
          {opportunity.status === 'NO_COUNTRIES_MATCH' && (
            <p>
              This does not mean these opportunities are absent everywhere; some countries may
              have insufficient comparable evidence. Remove one filter to broaden the result.
            </p>
          )}
          <div className="active-filter-chips" aria-label="Active opportunity filters">
            {opportunity.active_filter_ids.map((filterId) => {
              const definition = opportunityDefinitions.get(filterId)
              const name = filterName(definition, filterId, true)
              return (
                <button
                  type="button"
                  className="active-filter-chip"
                  disabled={isUpdating}
                  title={definition?.display_name ?? filterId}
                  aria-label={`Remove ${definition?.display_name ?? filterId} opportunity filter`}
                  onClick={() => onRemoveOpportunityFilter(filterId)}
                  key={filterId}
                >
                  <span aria-hidden="true">✓</span> {name} <span aria-hidden="true">×</span>
                </button>
              )
            })}
          </div>
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
        </section>
      )}

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

      {opportunity.excluded_countries.length > 0 && (
        <details className="excluded-country-details opportunity-exclusions">
          <summary>
            Review {opportunity.excluded_countries.length} opportunity-filter excluded{' '}
            {opportunity.excluded_countries.length === 1 ? 'country' : 'countries'}
          </summary>
          <p>
            These countries keep their canonical affinity context but are not ranked in the
            filtered result.
          </p>
          <div className="excluded-country-list">
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
        </details>
      )}
    </div>
  )
}
