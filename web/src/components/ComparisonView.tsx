import { useEffect, useRef } from 'react'

import type {
  ComparisonV2,
  ContributionV2,
  OpportunityFilterCatalogV2,
  TfcCatalogV2,
} from '../api/types'
import {
  LOCALITY_CONTENT,
  countryCode,
  localityName,
  readableCode,
} from '../localityPresentation'
import { formatScore } from '../preferences'
import {
  OPPORTUNITY_STATE_CONTENT,
  filterName,
  routeSummary,
} from '../opportunityPresentation'
import { tfcName, tfcOutcomeContent } from '../tfcPresentation'
import { CountryFeasibilitySummary } from './FeasibilitySummary'

type ComparisonViewProps = {
  comparison: ComparisonV2
  opportunityCatalog: OpportunityFilterCatalogV2
  tfcCatalog: TfcCatalogV2 | null
  onBack: () => void
  onSelectCountry: (countryCode: string) => void
}

function ContributionValue({
  contribution,
  outcome,
  reasons,
}: {
  contribution: ContributionV2 | null
  outcome: string
  reasons: string[]
}) {
  if (!contribution) {
    const reasonText = reasons.map(readableCode).join(', ')
    return (
      <span
        className="unavailable-cell"
        aria-label={`Data not available: ${reasonText || readableCode(outcome)}`}
      >
        <span aria-hidden="true">—</span>
        <small>{readableCode(outcome)}</small>
        {reasonText && <small>{reasonText}</small>}
      </span>
    )
  }
  return (
    <div className="comparison-value">
      <strong>{contribution.score.toFixed(1)}</strong>
      {contribution.derivation === 'AGGREGATED_FROM_LOCALITIES' && (
        <>
          <span className="badge badge-scope">⌖ Locality-derived</span>
          <span className="comparison-localities">
            {contribution.contributing_localities
              .map(
                (item) =>
                  `${item.locality.display_name} ${item.input_score.toFixed(1)}`,
              )
              .join(', ')}
          </span>
        </>
      )}
    </div>
  )
}

export function ComparisonView({
  comparison,
  opportunityCatalog,
  tfcCatalog,
  onBack,
  onSelectCountry,
}: ComparisonViewProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)
  useEffect(() => headingRef.current?.focus(), [])
  const opportunityDefinitions = new Map(
    opportunityCatalog.definitions.map((definition) => [definition.id, definition]),
  )
  const opportunityFiltersActive =
    comparison.assessments.opportunity.active_filter_ids.length > 0
  const tfcDefinitions = new Map(
    (tfcCatalog?.definitions ?? []).map((definition) => [definition.id, definition]),
  )

  return (
    <section className="comparison-panel" aria-labelledby="comparison-heading">
      <div className="comparison-header">
        <div>
          <button className="back-button" onClick={onBack}>
            ← Back to rankings
          </button>
          <p className="eyebrow">Side-by-side view</p>
          <h2 id="comparison-heading" ref={headingRef} tabIndex={-1}>
            Compare countries
          </h2>
          <p>
            Scores, locality provenance, and unavailable evidence come directly from the API. No
            partial aggregate is fabricated.
          </p>
        </div>
        <button
          className="icon-button"
          aria-label="Close comparison and return to rankings"
          onClick={onBack}
        >
          ×
        </button>
      </div>

      {comparison.countries.some((country) => country.coverage_excluded) && (
        <div className="comparison-data-notice" role="status">
          <span aria-hidden="true">!</span>
          <p>
            Coverage-excluded countries have no final aggregate. Their available criterion and
            locality evidence remains visible.
          </p>
        </div>
      )}
      {comparison.countries.some((country) => country.opportunity_excluded) && (
        <div className="comparison-data-notice opportunity-comparison-notice" role="status">
          <span aria-hidden="true">○</span>
          <p>
            Opportunity-filter excluded countries retain their canonical affinity score and base
            rank, but are not assigned a filtered rank.
          </p>
        </div>
      )}

      <div className="comparison-table-wrap">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col">Criterion</th>
              {comparison.countries.map((country) => {
                const code = countryCode(country.country.entity_id)
                return (
                  <th
                    scope="col"
                    key={country.country.entity_id}
                    className={
                      country.coverage_excluded ? 'unranked-country-column' : undefined
                    }
                  >
                    <button
                      className="country-column-button"
                      onClick={() => onSelectCountry(code)}
                    >
                      {country.country.display_name}
                    </button>
                    {country.coverage_excluded && (
                      <span className="column-status">Coverage excluded</span>
                    )}
                    {country.opportunity_excluded && (
                      <span className="column-status">Opportunity-filter excluded</span>
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Overall affinity</th>
              {comparison.countries.map((country) => (
                <td
                  key={country.country.entity_id}
                  className={
                    country.coverage_excluded ? 'unranked-country-column' : undefined
                  }
                >
                  {country.final_aggregate !== null ? (
                    <>
                      <strong>{formatScore(country.final_aggregate)}</strong>
                      <span className="comparison-rank">
                        {country.rank !== null
                          ? `${opportunityFiltersActive ? 'Filtered rank' : 'Rank'} ${country.rank}`
                          : `Base rank ${country.base_rank}`}
                      </span>
                    </>
                  ) : (
                    <span className="unavailable-cell" aria-label="No partial affinity score">
                      <span aria-hidden="true">—</span>
                      <small>Coverage excluded</small>
                    </span>
                  )}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Locality assessment</th>
              {comparison.countries.map((country) => {
                const locality = country.assessments.locality
                const contributions = comparison.criterion_rows.flatMap((row) =>
                  row.cells
                    .filter(
                      (cell) =>
                        cell.country.entity_id === country.country.entity_id &&
                        cell.contribution,
                    )
                    .map((cell) => cell.contribution as ContributionV2),
                )
                const bestCommon = localityName(
                  locality.best_common_locality_entity_id,
                  contributions,
                )
                return (
                  <td key={country.country.entity_id}>
                    <strong>{LOCALITY_CONTENT[locality.status].label}</strong>
                    {bestCommon && <span>Best common: {bestCommon}</span>}
                    {!bestCommon && locality.common_locality_entity_ids.length > 0 && (
                      <span>
                        Common evidence:{' '}
                        {locality.common_locality_entity_ids
                          .map((id) => localityName(id, contributions))
                          .join(', ')}
                      </span>
                    )}
                  </td>
                )
              })}
            </tr>
            {comparison.assessments.opportunity.active_filter_ids.map((filterId) => {
              const definition = opportunityDefinitions.get(filterId)
              return (
                <tr className="opportunity-comparison-row" key={`opportunity:${filterId}`}>
                  <th scope="row">
                    Opportunity filter
                    <span>{filterName(definition, filterId)}</span>
                  </th>
                  {comparison.countries.map((country) => {
                    const evidence = country.assessments.opportunity.filter_evidence.find(
                      (item) => item.filter_id === filterId,
                    )
                    if (!evidence) {
                      return <td key={country.country.entity_id}>Not evaluated</td>
                    }
                    const content = OPPORTUNITY_STATE_CONTENT[evidence.state]
                    const route = routeSummary(evidence)
                    return (
                      <td key={country.country.entity_id}>
                        <span className={`opportunity-state-badge state-${content.className}`}>
                          <span aria-hidden="true">{content.icon}</span> {content.label}
                        </span>
                        {route && <small>Route: {route}</small>}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
            {tfcCatalog &&
              comparison.assessments.feasibility?.selected_tfc_ids.map((tfcId) => (
                <tr className="feasibility-comparison-row" key={`feasibility:${tfcId}`}>
                  <th scope="row">
                    Feasibility check
                    <span>{tfcName(tfcDefinitions.get(tfcId), tfcId)}</span>
                  </th>
                  {comparison.countries.map((country) => {
                    const outcome = country.assessments.feasibility?.outcomes.find(
                      (item) => item.tfc_id === tfcId,
                    )
                    if (!outcome) return <td key={country.country.entity_id}>Not evaluated</td>
                    const content = tfcOutcomeContent(outcome)
                    return (
                      <td key={country.country.entity_id}>
                        <span className={`tfc-status-badge tfc-tone-${content.tone}`}>
                          <span aria-hidden="true">{content.icon}</span> {content.label}
                        </span>
                        {outcome.input_required_fields.length > 0 && (
                          <small>{outcome.input_required_fields.length} more inputs requested</small>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            {comparison.criterion_rows.map((row) => (
              <tr key={row.criterion_id}>
                <th scope="row">
                  {row.criterion_name}
                  <span className="row-badges">
                    {row.coverage.mode === 'CONDITIONAL_COMPLETE_CASE' && (
                      <span className="badge badge-limited">! Limited coverage</span>
                    )}
                    {row.scope.derivation === 'AGGREGATED_FROM_LOCALITIES' && (
                      <span className="badge badge-scope">⌖ Locality-derived</span>
                    )}
                  </span>
                </th>
                {comparison.countries.map((country) => {
                  const cell = row.cells.find(
                    (item) => item.country.entity_id === country.country.entity_id,
                  )
                  return (
                    <td
                      key={country.country.entity_id}
                      className={
                        country.coverage_excluded
                          ? 'unranked-country-column'
                          : undefined
                      }
                    >
                      {cell ? (
                        <ContributionValue
                          contribution={cell.contribution}
                          outcome={cell.outcome}
                          reasons={cell.reason_codes}
                        />
                      ) : (
                        <span aria-label="Data not available">—</span>
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="comparison-cards">
        {comparison.countries.map((country) => {
          const code = countryCode(country.country.entity_id)
          return (
            <article className="comparison-card" key={country.country.entity_id}>
              <h3>
                <button onClick={() => onSelectCountry(code)}>
                  {country.country.display_name}
                </button>
              </h3>
              <p>
                {country.final_aggregate !== null
                  ? `${formatScore(country.final_aggregate)} · ${
                      country.rank !== null
                        ? `${opportunityFiltersActive ? 'Filtered rank' : 'Rank'} ${country.rank}`
                        : `Base rank ${country.base_rank} · Opportunity-filter excluded`
                    }`
                  : 'Coverage excluded · no final aggregate'}
              </p>
              <p>
                <strong>Locality:</strong>{' '}
                {LOCALITY_CONTENT[country.assessments.locality.status].label}
              </p>
              {comparison.assessments.opportunity.active_filter_ids.length > 0 && (
                <div className="comparison-opportunity-list">
                  <strong>Opportunity filters</strong>
                  <ul>
                    {comparison.assessments.opportunity.active_filter_ids.map((filterId) => {
                      const evidence = country.assessments.opportunity.filter_evidence.find(
                        (item) => item.filter_id === filterId,
                      )
                      const content = evidence
                        ? OPPORTUNITY_STATE_CONTENT[evidence.state]
                        : null
                      const route = evidence ? routeSummary(evidence) : ''
                      return (
                        <li key={filterId}>
                          {filterName(opportunityDefinitions.get(filterId), filterId, true)}:{' '}
                          {content?.label ?? 'Not evaluated'}
                          {route && <small>Route: {route}</small>}
                        </li>
                      )
                    })}
                  </ul>
                </div>
              )}
              {tfcCatalog && country.assessments.feasibility && (
                <div className="comparison-feasibility-list">
                  <strong>Feasibility checks</strong>
                  <CountryFeasibilitySummary
                    assessment={country.assessments.feasibility}
                    catalog={tfcCatalog}
                    detailed
                  />
                </div>
              )}
              <dl>
                {comparison.criterion_rows.map((row) => {
                  const cell = row.cells.find(
                    (item) => item.country.entity_id === country.country.entity_id,
                  )
                  return (
                    <div key={row.criterion_id}>
                      <dt>{row.criterion_name}</dt>
                      <dd>
                        {cell ? (
                          <ContributionValue
                            contribution={cell.contribution}
                            outcome={cell.outcome}
                            reasons={cell.reason_codes}
                          />
                        ) : (
                          '—'
                        )}
                      </dd>
                    </div>
                  )
                })}
              </dl>
            </article>
          )
        })}
      </div>

      <footer className="comparison-footer">Data release: {comparison.release_id}</footer>
    </section>
  )
}
